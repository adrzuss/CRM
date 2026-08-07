# Proposal: Idempotencia en Ventas

## Intent

Prevenir duplicados de facturación por doble POST (timeout, doble click, reintento). `procesar_nueva_venta` no tiene idempotencia: cada llamado quema un correlativo y crea una factura duplicada en 11+ tablas.

## Scope

### In Scope
- Columna `idempotency_key VARCHAR(36)` + UNIQUE INDEX en `facturav`
- UNIQUE INDEX `(punto_vta, nro_comprobante, idtipocomprobante)` en `facturav`
- Validación de idempotencia al inicio del pipeline (retornar factura existente)
- `getNroComprobante` movido al final, antes del commit (correlativo tardío)
- UUID v4 desde frontend como campo oculto

### Out of Scope
- Retry lógico frontend, rate limiting, middleware genérico, idempotencia distribuida

## Capabilities

> No hay specs previos. Nueva capability.

### New Capabilities
- `ventas-idempotencia`: creación idempotente de comprobantes — rechaza o retorna existentes en submissions duplicadas

### Modified Capabilities
None

## Approach

1. **Migración BD**: `ALTER TABLE facturav ADD idempotency_key VARCHAR(36) NULL, ADD UNIQUE INDEX idx_uq_comprobante (punto_vta, nro_comprobante, idtipocomprobante)`
2. **Frontend**: UUID v4 en submit del form, campo `_idempotency_key` oculto
3. **Fase 0**: buscar `facturav WHERE idempotency_key = ?`. Si existe → devolver `{success: true, existing_id}`
4. **Correlativo tardío**: mover `getNroComprobante` de Fase 1 → Fase 6 (antes del commit)
5. **Setear key** en la factura antes del commit
6. **Error**: capturar `IntegrityError` en UNIQUE, rollback, retornar factura original si recuperable

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `services/ventas/ventas.py` | Modified | Idempotency check + correlativo tardío |
| `utils/facturacion.py` | Modified | `getNroComprobante` sin commit prematuro |
| `models/ventas.py` | Modified | Campo `idempotency_key` en modelo |
| `templates/ventas/ventas.html` | Modified | Campo oculto UUID |
| *SQL migration* | New | Columna + índices |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Race condition dos POSTs misma key | Low | UNIQUE INDEX como defensa final |
| Correlativo tardío rompe flujos | Medium | Probar Factura A/B, NC, ND, presupuesto, remito |
| UUID nulo desde frontend | Low | Si NULL, saltar validación (backward compat) |

## Rollback Plan

1. Revertir cambios en ventas.py, facturacion.py, ventas.html, models/ventas.py
2. Ejecutar `ALTER TABLE facturav DROP INDEX idx_uq_comprobante, DROP COLUMN idempotency_key`
3. Verificar que `getNroComprobante` retorna a su posición original

## Dependencies

Ninguna. `uuid4` / `secrets` (stdlib Python).

## Success Criteria

- [ ] Dos POSTs mismo `idempotency_key` → una factura (segundo retorna datos existentes)
- [ ] `getNroComprobante` corre tras validaciones — sin números quemados en fallos
- [ ] UNIQUE INDEX rechaza violaciones a nivel BD
- [ ] Clientes sin `idempotency_key` (NULL) siguen funcionando
