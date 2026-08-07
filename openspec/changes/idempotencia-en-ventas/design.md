# Design: Idempotencia en Ventas

## Technical Approach

Three-layer idempotency: (1) frontend genera UUID v4 por submit y lo envía como `_idempotency_key`, (2) service layer consulta por key al inicio y retorna early si ya existe, (3) UNIQUE INDEX en MySQL como guarda final contra race conditions. El correlativo `getNroComprobante` se mueve a late assignment (flush en vez de commit) para evitar consumir números en transacciones fallidas.

## Architecture Decisions

### Decision: Idempotency key generation

| Choice | `crypto.randomUUID()` client-side | Server-generated UUID |
|---|---|---|
| Tradeoff | Sin round-trip extra; soporte ~95% browsers | +1 request pero control total |
| **Decision** | **Client-side** — `crypto.randomUUID()` con fallback a función helper. El costo de una llamada extra no justifica la latencia adicional. |

### Decision: Duplicate detection strategy

| Choice | Application check + DB UNIQUE INDEX | Solo aplicación | Solo DB |
|---|---|---|---|
| Tradeoff | Dos capas, más robusto | Más simple pero vulnerable a race conditions | No permite early return |
| **Decision** | **Application check + UNIQUE INDEX**. El check temprano evita procesar items/pagos innecesariamente; el INDEX captura el race condition de 2 requests concurrentes. |

### Decision: Correlative late assignment

| Choice | `flush()` en `getNroComprobante` | `commit()` actual |
|---|---|---|
| Tradeoff | El correlativo se consume atómicamente con la transacción | El correlativo se quema incluso si la venta falla después |
| **Decision** | **`flush()`**. Cambiar `db.session.commit()` → `db.session.flush()` dentro de `getNroComprobante`. El correlativo se reserva en la transacción actual y solo persiste si el commit final de `procesar_nueva_venta` tiene éxito. |

### Decision: Error response shape

La respuesta duplicada usa el mismo shape que éxito: `{success: true, id: N, nro_comprobante: "0001-00001234"}`. El frontend no necesita cambios para manejar el caso idempotente — ya consume `data.id` y `data.nro_comprobante`.

## Data Flow

```
Frontend                          Backend
   │                                │
   ├─ crypto.randomUUID()           │
   ├─ append _idempotency_key       │
   │      │                         │
   │      ▼                         │
   │  POST /nueva_venta            │
   │      │                         │
   │      ▼                         │
   │  procesar_nueva_venta()        │
   │      │                         │
   │      ├─ ¿_idempotency_key?     │
   │      │   └─ No → skip check    │
   │      │                         │
   │      ├─ ¿Factura por key?      │
   │      │   ├─ Sí → return {id}   │
   │      │   └─ No → continue      │
   │      │                         │
   │      ├─ Validar datos          │
   │      ├─ Crear Factura (sin nro)│
   │      ├─ flush() → idfactura    │
   │      ├─ procesar_items()       │
   │      ├─ procesar_pagos()       │
   │      ├─ getNroComprobante()    │
   │      │   └─ flush()            │
   │      ├─ nueva_factura.nro = X  │
   │      │                         │
   │      ├─ db.session.commit()    │
   │      │   ├─ IntegrityError?    │
   │      │   │  └─ rollback        │
   │      │   │  └─ re-query by key │
   │      │   │  └─ return existing │
   │      │   │                     │
   │      │   └─ OK → return {id}   │
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `models/ventas.py` | Modify | Agregar `idempotency_key = db.Column(db.String(36))` nullable |
| `services/ventas/ventas.py` | Modify | Agregar idempotency check al inicio; mover `getNroComprobante` justo antes del commit final |
| `services/ventas/facturacion.py` | Modify | `getNroComprobante`: cambiar `commit()` → `flush()` |
| `static/js/nueva_venta.js` | Modify | Inyectar `_idempotency_key` en FormData en ambos paths de submit (`procesarTransaccion` y submit handler) |
| `SQL/migration_idempotencia.sql` | Create | Script de migración |

## Interfaces / Contracts

`procesar_nueva_venta(form, id_sucursal)` → `(nro_comprobante, id_factura)`:
- Sin cambios en la firma ni tipo de retorno
- El caso idempotente retorna los datos de la factura existente

Formato de `_idempotency_key`: UUID v4 (36 chars, ej. `550e8400-e29b-41d4-a716-446655440000`).
- Si está presente pero no es UUID v4 válido → `400 Bad Request: "Formato de clave de idempotencia inválido"`
- Si está ausente → comportamiento actual (backward compatible)

```python
# Estructura del check en ventas.py
idempotency_key = form.get('_idempotency_key')
if idempotency_key:
    if not es_uuid_valido(idempotency_key):
        raise ValueError("Formato de clave de idempotencia inválido")
    factura = Factura.query.filter_by(idempotency_key=idempotency_key).first()
    if factura:
        return factura.nro_comprobante, factura.id
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Idempotency early return | Mock DB query, assert early return de `(nro, id)` sin procesar items |
| Unit | Validación formato UUID | Assert que UUID inválido lanza ValueError |
| Unit | Correlative late assignment | Assert `getNroComprobante` se llama después de items/pagos |
| Integration | Duplicate detection | Insert factura con key, llamar de nuevo, assert mismo ID retornado |
| Integration | Race condition UNIQUE INDEX | Dos inserts concurrentes misma key; assert exactamente 1 fila |
| Integration | Rollback IntegrityError | Assert que rollback + re-query funciona sin corruptar sesión |

## Migration / Rollout

```sql
-- Fase 1: Agregar columna
ALTER TABLE facturav ADD COLUMN idempotency_key VARCHAR(36) NULL;

-- Fase 2: UNIQUE INDEX para detección de duplicados (race condition)
CREATE UNIQUE INDEX idx_uq_idempotency ON facturav(idempotency_key);

-- Fase 3: UNIQUE INDEX compuesto para evitar correlativos duplicados
CREATE UNIQUE INDEX idx_uq_comprobante ON facturav(punto_vta, nro_comprobante, idtipocomprobante);
```

**Rollback**: `DROP INDEX idx_uq_idempotency ON facturav; DROP INDEX idx_uq_comprobante ON facturav; ALTER TABLE facturav DROP COLUMN idempotency_key;`

## Open Questions

None.
