# Tasks: Idempotencia en Ventas

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~60–80 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

## Phase 1: Foundation — Modelo y Migración

- [x] 1.1 Crear `SQL/migration_idempotencia.sql` — ALTER TABLE facturav ADD idempotency_key VARCHAR(36) NULL + CREATE UNIQUE INDEX idx_uq_idempotency (idempotency_key) + CREATE UNIQUE INDEX idx_uq_comprobante (punto_vta, nro_comprobante, idtipocomprobante)
- [x] 1.2 Agregar `idempotency_key = db.Column(db.String(36), nullable=True)` a `Factura` en `models/ventas.py` (columna nullable, sin cambios en constructor existente)

## Phase 2: Core — Correlativo Tardío y Detección de Duplicados

- [x] 2.1 Cambiar `db.session.commit()` → `db.session.flush()` dentro de `getNroComprobante` en `services/ventas/facturacion.py` (línea 91). El correlativo se reserva en la transacción actual sin persistir hasta el commit final.
- [x] 2.2 Agregar bloque de idempotencia al inicio de `procesar_nueva_venta` en `services/ventas/ventas.py`: extraer `_idempotency_key` del form, validar formato UUID v4 (si presente pero inválido → raise `ValueError`), y si existe factura con esa key → return `(nro_comprobante, id)` early sin procesar items ni pagos.
- [x] 2.3 Mover `getNroComprobante` (línea 56) a justo antes del `db.session.commit()` (antes de línea 117). Setear `nueva_factura.idempotency_key` antes del commit. Agregar try-except para `IntegrityError` en el commit: rollback, re-query por key, retornar factura existente.

## Phase 3: Frontend — UUID v4 desde el Cliente

- [x] 3.1 En `static/js/nueva_venta.js`: agregar helper `generarUUID()` usando `crypto.randomUUID()` con fallback; inyectar `_idempotency_key` en FormData en ambos paths de submit (`procesarTransaccion` y handler directo).

## Phase 4: Tests

- [x] 4.1 Test: UUID inválido → ValueError
- [x] 4.2 Test: early return cuando factura con misma key ya existe
- [x] 4.3 Test: sin `_idempotency_key` → skip idempotency check
- [x] 4.4 Test: IntegrityError en commit → rollback + re-query + return existente

## Implementation Order

Migración y modelo primero (Phase 1), luego la lógica de negocio con correlativo tardío + detección de duplicados (Phase 2), y por último el frontend que genera el UUID (Phase 3). Este orden permite probar el backend con valores manuales antes de integrar el frontend. El cambio es chico y autónomo — un solo PR basta.

## Notas

- `idempotency_key` NULL mantiene backward compatibility: clientes sin el campo siguen funcionando igual que antes.
- 4 tests automatizados agregados en `tests/test_services_ventas.py` cubriendo UUID inválido, early return, skip sin key, y recovery de IntegrityError.
