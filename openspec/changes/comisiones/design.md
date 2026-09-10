# Design: Sistema de Comisiones

## Technical Approach

Build a self-contained `comisiones/` module following the existing routes→services→models pattern. The calculator engine is a pure Python class (no Flask dependency), invoked by `ComisionesService` which owns transactions. Commission calculation is batch-oriented and decoupled from the sale transaction — `costo_unitario` is captured inline during sale, commissions are computed later in a separate period-closing flow.

## Architecture Decisions

### Decision: Module structure as top-level package

**Choice**: `comisiones/` package under project root (not inside `routes/` or `services/`)

**Alternatives considered**: Flattened files in `services/` and `routes/`; nested under existing modules

**Rationale**: The spec defines 6+ tables, a calculator engine, validators, and constants. This is a bounded context. Following the same pattern as `routes/ventas/` which already groups `ventas.py`, `facturacion.py`, `notas_credito.py`, etc., but with its own `__init__.py` for clean imports.

### Decision: Calculator engine as pure function class

**Choice**: `CalculadorComisiones` in `calculator.py` — no Flask imports, receives data dicts

**Alternatives considered**: Inheriting from a Flask-aware base; mixing calculation into routes

**Rationale**: Enables unit testing without app context. The calculator takes `(plan, items, contexto)` and returns `[ResultadoComision]`. No `session`, no `db` access. The service layer fetches data and passes it in.

### Decision: Batch processing via service-level preloading

**Choice**: `ComisionesService` preloads all needed data (ventas, items, artículos, reglas) in a few bulk queries, then calls the calculator for each item in-memory

**Alternatives considered**: One SQL per item (N+1); stored procedure for everything

**Rationale**: Matches the spec's §49 requirement. A typical month might have 1000-5000 items across 200-500 invoices. 4-5 bulk queries is tractable. The calculator operates on in-memory dicts, not ORM objects.

### Decision: costo_unitario captured in sale transaction

**Choice**: Add `costo_unitario` to `Item` model, set `item.costo_unitario = articulo.costo` inside `procesar_items()` before `db.session.add(item)`

**Alternatives considered**: Trigger; separate UPDATE after commit; deferred copy

**Rationale**: §35 requires it in the same transaction. `procesar_items` already has `articulo` loaded (line 178 of `services/ventas/ventas.py`). One line added to the `Item()` constructor call. Rollback-safe.

### Decision: Idempotency via UNIQUE constraint on (id_liquidacion, id_factura, id_item, id_regla)

**Choice**: Composite UNIQUE on `comisiones_detalle` + application-level INSERT IGNORE pattern

**Alternatives considered**: Application-only checks; idempotency_key column

**Rationale**: §36 requires duplicate prevention. A DB constraint is the only reliable mechanism. The service catches `IntegrityError` and skips the duplicate gracefully.

### Decision: Permissions via existing `OpcionesMenu` system

**Choice**: Register new menu codes: `COMISIONES_ADMIN`, `COMISIONES_SUPERVISOR`, `COMISIONES_VENDEDOR`

**Alternatives considered**: Separate permission table; role-based override

**Rationale**: The ERP already uses `OpcionesMenu` → `PermisosMenu` → `Tareas` → `TareasUsuarios` chain (see `services/sessions.py`). Adding new codes is the standard pattern. Admin sees all CRUD + liquidation; Supervisor sees calculate + view; Vendor sees own data only.

### Decision: Nota de crédito subtraction via tipo_movimiento sign

**Choice**: `tipo_movimiento = 'VENTA'` → positive; `tipo_movimiento = 'NOTA_CREDITO'` → negative. Calculator applies sign based on `tipo_comprobantes`.

**Alternatives considered**: Separate tables; absolute values with manual negation

**Rationale**: §20 defines this explicitly. The detail row preserves the original `id_factura` reference so the audit trail is intact. Net commission = sum of all detail rows for a vendor in a period.

### Decision: Liquidation lifecycle (BORRADOR→CALCULADA→CONFIRMADA→PAGADA→ANULADA)

**Choice**: State machine in `ComisionesService` with explicit transitions

**Alternatives considered**: Free-form status; simple flag

**Rationale**: §37 requires that confirmed liquidations are immutable. Service checks `estado` before allowing mutations. ANULAR creates a new liquidation, never modifies the old one.

## Data Flow

```
VENTA (existing)
  │
  ├─ procesar_items() ──► item.costo_unitario = articulo.costo
  │                        (same transaction, §35)
  │
  ▼
[ SALE COMMITTED ]

CÁLCULO DE PERÍODO (batch, on-demand)
  │
  ├─ Service: preload ventas+items in date range
  ├─ Service: preload artículos (for rubro/marca/tipo)
  ├─ Service: preload asignaciones → planes → reglas
  ├─ Service: preload pagos_fv (for medio_pago rules)
  │
  ├─ For each (vendedor, venta, item):
  │   ├─ Find matching regla (priority + exclusivity)
  │   ├─ Calculate base: venta_total / neto / margen
  │   ├─ Apply percentage or fixed amount
  │   ├─ Sign flip for NC
  │   └─ Return ResultadoComision
  │
  ├─ Service: INSERT detalle rows (ignore duplicates)
  ├─ Service: UPDATE liquidacion.total = SUM(detalle)
  └─ Service: SET estado = CALCULADA
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `comisiones/__init__.py` | Create | Package init, exports `bp_comisiones` |
| `comisiones/constants.py` | Create | Commission types, states, movement types, base_calculo, modo_escalas enums |
| `comisiones/models.py` | Create | 6 SQLAlchemy models: Plan, Regla, Tramo, Asignacion, Liquidacion, Detalle |
| `comisiones/repositories.py` | Create | `ComisionesRepository` — all SQL queries (bulk preload, CRUD, reports) |
| `comisiones/calculator.py` | Create | `CalculadorComisiones` — pure calculation engine |
| `comisiones/services.py` | Create | `ComisionesService` — orchestrates repo + calculator, owns transactions |
| `comisiones/validators.py` | Create | Validation: assignment overlap, plan dates, rule priorities |
| `comisiones/routes.py` | Create | Blueprint: CRUD planes, reglas, asignaciones, calcular, liquidaciones, reportes |
| `models/ventas.py` | Modify | Add `costo_unitario` column to `Item` model |
| `services/ventas/ventas.py` | Modify | Set `costo_unitario=articulo.costo` in `procesar_items()` Item() call |
| `index.py` | Modify | Import and register `bp_comisiones` with prefix `/comisiones` |
| `templates/comisiones/` | Create | 8 templates: planes, plan_form, reglas, asignaciones, calcular, liquidaciones, liquidacion_detalle, reportes |
| `static/js/comisiones.js` | Create | Frontend: HTMX interactions, date pickers, preview |
| `SQL/migracion_comisiones.sql` | Create | DDL: ALTER itemsv + 6 CREATE TABLE + indexes |

## Interfaces / Contracts

```python
# constants.py
class TipoCalculo(Enum):
    PORCENTAJE_VENTA = "PORCENTAJE_VENTA"
    PORCENTAJE_NETO = "PORCENTAJE_NETO"
    PORCENTAJE_MARGEN = "PORCENTAJE_MARGEN"
    POR_ARTICULO = "POR_ARTICULO"
    POR_RUBRO = "POR_RUBRO"
    POR_MARCA = "POR_MARCA"
    POR_DESCUENTO = "POR_DESCUENTO"
    POR_UNIDAD = "POR_UNIDAD"
    ESCALONADA = "ESCALONADA"

class BaseCalculo(Enum):
    VENTA_TOTAL = "VENTA_TOTAL"
    VENTA_NETA = "VENTA_NETA"
    VENTA_DESCUENTO = "VENTA_DESCUENTO"
    MARGEN = "MARGEN"
    CANTIDAD = "CANTIDAD"

class TipoMovimiento(Enum):
    VENTA = "VENTA"
    NOTA_CREDITO = "NOTA_CREDITO"
    NOTA_DEBITO = "NOTA_DEBITO"

class EstadoLiquidacion(Enum):
    BORRADOR = "BORRADOR"
    CALCULADA = "CALCULADA"
    CONFIRMADA = "CONFIRMADA"
    PAGADA = "PAGADA"
    ANULADA = "ANULADA"

class ModoEscalas(Enum):
    TASA_ALCANZADA = "TASA_ALCANZADA"
    PROGRESIVA = "PROGRESIVA"
```

```python
# calculator.py
class ResultadoComision:
    id_factura: int
    id_item: int
    id_usuario: int
    id_regla: int
    tipo_comision: str
    tipo_movimiento: str
    base_calculo: Decimal
    cantidad: Decimal
    costo_unitario: Decimal
    importe_venta: Decimal
    importe_costo: Decimal
    importe_margen: Decimal
    porcentaje: Decimal
    importe_comision: Decimal

class CalculadorComisiones:
    def calcular_venta(self, venta: dict, items: list, contexto: dict,
                       reglas: list) -> list[ResultadoComision]
    def calcular_item(self, item: dict, contexto: dict,
                      reglas: list) -> ResultadoComision | None
    def _buscar_regla_aplicable(self, item: dict, contexto: dict,
                                reglas: list) -> dict | None
    def _calcular_base(self, item: dict, contexto: dict,
                       tipo_calculo: str, base_calculo: str) -> Decimal
    def _aplicar_porcentaje(self, base: Decimal, porcentaje: Decimal) -> Decimal
    def _calcular_escalonada(self, base: Decimal,
                             tramos: list) -> Decimal
```

```python
# services.py
class ComisionesService:
    def calcular_periodo(self, fecha_desde, fecha_hasta,
                         id_usuario=None) -> dict
        """Returns preview (not committed). Calculates all matching items."""
    def confirmar_calculo(self, id_liquidacion) -> None
        """Moves BORRADOR→CALCULADA, persists detalle rows."""
    def confirmar_liquidacion(self, id_liquidacion) -> None
        """Moves CALCULADA→CONFIRMADA. Immutable after this."""
    def anular_liquidacion(self, id_liquidacion, motivo) -> int
        """Creates new liquidation, marks old as ANULADA. Returns new ID."""
    def get_preview(self, fecha_desde, fecha_hasta,
                    id_usuario=None) -> list[dict]
        """Returns aggregated preview without persisting."""
```

```python
# repositories.py
class ComisionesRepository:
    def get_ventas_en_rango(self, desde, hasta, id_usuario=None) -> list
    def get_items_venta(self, id_factura) -> list
    def get_articulos_bulk(self, ids) -> dict
    def get_asignacion_vigente(self, id_usuario, fecha) -> dict
    def get_plan_con_reglas(self, id_plan) -> dict
    def get_pagos_venta(self, id_factura) -> list
    def save_liquidacion(self, data) -> int
    def save_detalle_bulk(self, items) -> None
    def get_liquidaciones(self, filters) -> list
    def get_detalle_liquidacion(self, id_liquidacion) -> list
    def get_reporte_vendedor(self, desde, hasta) -> list
    def get_reporte_articulo(self, desde, hasta) -> list
    def get_reporte_regla(self, desde, hasta) -> list
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | `CalculadorComisiones`: each tipo_calculo with known inputs/outputs | Pure Python test, no DB, no Flask |
| Unit | Rule matching priority + exclusivity vs acumulable | Table-driven tests |
| Unit | NC sign flip: venta positive, NC negative | Mock data dicts |
| Unit | Escalas: tasa alcanzada vs progresiva | Known boundary values |
| Integration | `ComisionesService`: bulk preload + calculate + persist | Flask test app + SQLite |
| Integration | Idempotency: duplicate insert ignored | SQLite with UNIQUE constraint |
| Integration | Liquidation state machine: valid/invalid transitions | Flask test app |
| E2E | Full cycle: create plan → assign → sale → calculate → liquidate | Manual, documented |

## Migration / Rollout

SQL migration script (`SQL/migracion_comisiones.sql`):

```sql
-- Phase 1: ALTER itemsv
ALTER TABLE itemsv ADD COLUMN costo_unitario DECIMAL(20,6) NOT NULL DEFAULT 0;

-- Phase 2: Commission tables
CREATE TABLE IF NOT EXISTS comisiones_planes (...);
CREATE TABLE IF NOT EXISTS comisiones_reglas (...);
CREATE TABLE IF NOT EXISTS comisiones_tramos (...);
CREATE TABLE IF NOT EXISTS comisiones_asignaciones (...);
CREATE TABLE IF NOT EXISTS comisiones_liquidaciones (...);
CREATE TABLE IF NOT EXISTS comisiones_detalle (...);

-- Phase 3: Indexes
CREATE INDEX IF NOT EXISTS idx_facturav_fecha ON facturav(fecha);
CREATE INDEX IF NOT EXISTS idx_itemsv_idfactura ON itemsv(idfactura);
-- ... etc per §50

-- Phase 4: Idempotency constraint
ALTER TABLE comisiones_detalle
ADD UNIQUE INDEX uq_detalle_comision
(id_liquidacion, id_factura, id_item, id_regla);
```

Backfill: Existing items get `costo_unitario = 0` (default). Historical commissions cannot use margen for pre-existing items — this is documented as a known limitation.

## Open Questions

- [ ] Should `comisiones_detalle.id_item` reference `itemsv.id` (composite PK) or a separate auto-increment? The composite PK `(idfactura, id)` on `itemsv` makes FK referencing awkward — may need to store `(idfactura, id_item)` as two columns or use a generated surrogate.
- [ ] Confirm `TipoCompAplica` values for NC/ND identification. The `ControlNc` model links NC to original invoice but doesn't expose `tipo_operacion.nombre`. Need to verify if `facturav.idtipocomprobante` directly distinguishes VENTA vs NC vs ND, or if a join to `tipo_comprobantes` + `tipo_comp_aplica` is needed.
- [ ] Phase 7 items (listas de precio, medios de pago, sucursal, categoría cliente) — should the rule model support these criteria columns from day one (nullable), or add columns later?
