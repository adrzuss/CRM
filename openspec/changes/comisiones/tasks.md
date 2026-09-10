# Tasks: Sistema de Comisiones

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 2000–2500 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 → PR 4 |
| Delivery strategy | ask-on-risk |
| Chain strategy | feature-branch-chain |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Database + models + constants | PR 1 | Base: feature/comisiones. Migration, ORM, enums. |
| 2 | Calculator engine + repositories + services + validators | PR 2 | Base: PR 1 branch. Core logic, no UI. |
| 3 | Routes + templates + sidebar | PR 3 | Base: PR 2 branch. Full CRUD UI. |
| 4 | Integration (ventas.py) + JS + index.py registration | PR 4 | Base: PR 3 branch. Wiring + polish. |

---

## Phase 1: Database

- [x] 1.1 Create `SQL/migracion_comisiones.sql` — ALTER itemsv ADD costo_unitario DECIMAL(20,6) NOT NULL DEFAULT 0
- [x] 1.2 Add CREATE TABLE `comisiones_planes` (id, nombre, tipo_calculo, base_calculo, modo_escalas, porcentaje_base, activo, fecha_desde, fecha_hasta, created_at, updated_at)
- [x] 1.3 Add CREATE TABLE `comisiones_reglas` (id, id_plan→FK, tipo_regla, criterio, valor_criterio, porcentaje, importe_fijo, prioridad, acumulable, activo)
- [x] 1.4 Add CREATE TABLE `comisiones_tramos` (id, id_plan→FK, desde, hasta, porcentaje, importe_fijo, orden)
- [x] 1.5 Add CREATE TABLE `comisiones_asignaciones` (id, id_usuario→FK, id_plan→FK, fecha_desde, fecha_hasta, activo)
- [x] 1.6 Add CREATE TABLE `comisiones_liquidaciones` (id, periodo_desde, periodo_hasta, estado, total, id_usuario→FK, created_at)
- [x] 1.7 Add CREATE TABLE `comisiones_detalle` (id, id_liquidacion→FK, id_usuario→FK, id_factura, id_item, id_regla→FK, tipo_movimiento, tipo_comision, base_calculo, cantidad, costo_unitario, importe_venta, importe_costo, importe_margen, porcentaje, importe_comision)
- [x] 1.8 Add UNIQUE INDEX `uq_detalle_comision` on (id_liquidacion, id_factura, id_item, id_regla) + performance indexes per NFR-02
- [x] 1.9 Verify migration runs cleanly with `IF NOT EXISTS` on all statements

## Phase 2: Backend Infrastructure

- [x] 2.1 Create `comisiones/__init__.py` — import and export `bp_comisiones`
- [x] 2.2 Create `comisiones/constants.py` — Enums: TipoCalculo, BaseCalculo, TipoMovimiento, EstadoLiquidacion, ModoEscalas, TipoRegla
- [x] 2.3 Create `comisiones/models.py` — 6 SQLAlchemy models: PlanComision, ReglaComision, TramoComision, AsignacionComision, LiquidacionComision, DetalleComision with relationships and __init__
- [x] 2.4 Add `costo_unitario` column to `Item` model in `models/ventas.py` — db.Column(db.Numeric(20,6), default=0), add to __init__ signature
- [x] 2.5 Create `comisiones/repositories.py` — ComisionesRepository class: `get_ventas_en_rango()`, `get_items_por_ventas()`, `get_articulos_bulk()`, `get_asignacion_vigente()`, `get_plan_con_reglas()`, `get_pagos_venta()`

## Phase 3: Calculator Engine

- [x] 3.1 Create `comisiones/calculator.py` — ResultadoComision dataclass with all audit fields
- [x] 3.2 Implement `CalculadorComisiones._buscar_regla_aplicable()` — priority matching + exclusivity vs acumulable logic
- [x] 3.3 Implement `_calcular_base()` — VENTA_TOTAL, VENTA_NETA, MARGEN, CANTIDAD bases using item + contexto dicts
- [x] 3.4 Implement `_aplicar_porcentaje()` and `_aplicar_importe_fijo()` — Decimal arithmetic, no floats
- [x] 3.5 Implement `_calcular_escalonada()` — TASA_ALCANZADA (single bracket) and PROGRESIVA (tiered) modes
- [x] 3.6 Implement `calcular_item()` — orchestrates rule search → base → percentage/fixed → escalas → sign flip for NC
- [x] 3.7 Implement `calcular_venta()` — iterates items, collects ResultadoComision list, handles NC via tipo_movimiento sign

## Phase 4: Service Layer + Validators

- [x] 4.1 Create `comisiones/validators.py` — `validar_superposicion_asignacion()` for BR-05, `validar_estado_liquidacion()` for BR-03, `validar_plan_vigente()` for date ranges
- [x] 4.2 Create `comisiones/services.py` — ComisionesService class, `calcular_periodo()`: preload ventas+items+articulos+asignaciones+reglas in bulk queries (NFR-01)
- [x] 4.3 Implement `confirmar_calculo()` — persist detalle rows with INSERT IGNORE for idempotency (BR-06), UPDATE liquidacion.total, set estado CALCULADA
- [x] 4.4 Implement `confirmar_liquidacion()` — move CALCULADA→CONFIRMADA, validate no mutations after (BR-03)
- [x] 4.5 Implement `anular_liquidacion()` — create new liquidation, mark old as ANULADA with motivo (BR-04)
- [x] 4.6 Implement `get_preview()` — aggregated preview by vendedor without persisting
- [x] 4.7 Implement CRUD repos for planes, reglas, tramos, asignaciones in repositories.py

## Phase 5: Routes + Templates

- [x] 5.1 Create `comisiones/routes.py` — Blueprint `bp_comisiones` with `@check_session` + `@alertas_mensajes` on all routes
- [x] 5.2 Implement routes: `GET/POST /comisiones/` (index), `GET/POST /comisiones/planes`, `GET/POST /comisiones/planes/nuevo`, `GET/POST /comisiones/planes/<id>`
- [x] 5.3 Implement routes: `GET/POST /comisiones/reglas`, `GET/POST /comisiones/reglas/<id_plan>`, `POST /comisiones/reglas/guardar`
- [x] 5.4 Implement routes: `GET/POST /comisiones/asignaciones`, `POST /comisiones/asignaciones/guardar`, `POST /comisiones/asignaciones/<id>/desactivar`
- [x] 5.5 Implement routes: `GET /comisiones/calcular`, `POST /comisiones/calcular/previsualizar`, `POST /comisiones/calcular/procesar`
- [x] 5.6 Implement routes: `GET /comisiones/liquidaciones`, `GET /comisiones/liquidaciones/<id>`, `POST /comisiones/liquidaciones/<id>/confirmar`, `POST /comisiones/liquidaciones/<id>/anular`
- [x] 5.7 Implement routes: `GET /comisiones/reportes`, `POST /comisiones/reportes/vendedor`, `POST /comisiones/reportes/articulo`
- [x] 5.8 Create `templates/comisiones/` directory — `index.html` (dashboard), `planes.html`, `plan_form.html`
- [x] 5.9 Create `templates/comisiones/reglas.html`, `asignaciones.html`
- [x] 5.10 Create `templates/comisiones/calcular.html`, `liquidaciones.html`, `liquidacion_detalle.html`
- [x] 5.11 Create `templates/comisiones/reportes.html`

## Phase 6: Integration

- [ ] 6.1 Modify `services/ventas/ventas.py` — in `procesar_items()`, add `costo_unitario=articulo.costo` to `Item()` constructor call (line ~231)
- [ ] 6.2 Modify `index.py` — add `from comisiones import bp_comisiones` import + `app.register_blueprint(bp_comisiones, url_prefix='/comisiones')`
- [ ] 6.3 Verify existing sales flow still works — `costo_unitario` defaults to 0 for new items, existing records unaffected

## Phase 7: Frontend

- [ ] 7.1 Create `static/js/comisiones.js` — date picker initialization, HTMX event handlers for plan/rule CRUD
- [ ] 7.2 Add preview rendering logic — format decimals, NC negative display, expand/collapse detalle
- [ ] 7.3 Modify `templates/partials/_sidebar.html` — add Comisiones menu section with collapse items (Planes, Asignaciones, Calcular, Liquidaciones, Reportes) using `tiene_permiso()` pattern
- [ ] 7.4 Include `comisiones.js` in comisiones base template
