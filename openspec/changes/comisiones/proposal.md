# Proposal: Sistema de Comisiones

## Intent

El ERP no soporta comisiones para vendedores. Los negocios que manejan vendedores necesitan calcular, auditar y liquidar comisiones de forma configurable — sin hardcodear modelos. El módulo permite definir planes con reglas flexibles (% venta, % neto, % margen, por artículo/rubro/marca/descuento), asignarlos a vendedores con vigencia temporal, y generar liquidaciones con trazabilidad completa. Notas de crédito deben restar comisión.

## Scope

### In Scope (v1 — 15 features)
- CRUD de planes de comisión (planes, reglas, tramos)
- Asignación de planes a vendedores con vigencia temporal
- Cálculo por período: % venta, % neto, % margen, por artículo, por rubro, por marca, por descuento
- Costo histórico: ALTER itemsv ADD costo_unitario + captura en transacción de venta
- Notas de crédito → comisión negativa
- Liquidaciones con estados (BORRADOR → CALCULADA → CONFIRMADA → PAGADA → ANULADA)
- Detalle auditable por ítem (regla, base, porcentaje, resultado)
- Reportes: por vendedor, por período, por artículo, por regla
- Motor de cálculo separado de rutas (calculator.py)
- Restricción: liquidaciones confirmadas NO se recalculan
- Restricción: no duplicar comisiones (liquidación + factura + item + regla)
- Prioridad de reglas con flag acumulable
- Acceso por roles: admin/supervisor/vendedor
- Escalas: tasa alcanzada + progresiva (almacenada en plan)
- Validación de asignaciones superpuestas

### Out of Scope (fases 2–4)
- Comisión por lista de precios, tipo de artículo, sucursal, categoría cliente
- Comisión por medio de pago, entidad de tarjeta
- Objetivos, bonificaciones, aceleradores
- Comisión por cobranza diferida / cuenta corriente

## Capabilities

### New Capabilities
- `comisiones-plane`: CRUD de planes, reglas, tramos; asignación a vendedores
- `comisiones-calculo`: Motor de cálculo, contexto de venta, resultado auditable
- `comisiones-liquidacion`: Liquidaciones por período, estados, detalle, reportes
- `comisiones-integracion`: Captura de costo_unitario en itemsv, notas de crédito negativas

### Modified Capabilities
- `ventas-idempotencia`: Extender para cubrir idempotencia de comisiones (misma factura+item+regla no duplica en liquidación)

## Approach

Arquitectura en capas dentro del blueprint `comisiones_bp`:

```
routes/comisiones.py          ← HTTP, validación, permisos, renderizado
services/comisiones/
    __init__.py
    planes.py                 ← CRUD planes, reglas, tramos
    asignaciones.py           ← Asignar/desasignar vendedores
    calculator.py             ← CalculadorComisiones (puro, sin DB)
    liquidaciones.py          ← Procesar período, confirmar, anular
    repositories.py           ← Queries SQL batch (evitar N+1)
    constants.py              ← Tipos de comisión, estados, modos escala
    validators.py             ← Validación de superposición, reglas
```

Modelos ORM para las 6 tablas nuevas. Repositorios con queries batch (una por ventas, una por items, una por artículos). Calculator recibe contexto pre-cargado y devuelve resultado auditado. Transacción única para venta + costo_unitario.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `models/comisiones.py` | **New** | 6 modelos ORM: Planes, Reglas, Tramos, Asignaciones, Liquidaciones, Detalle |
| `models/ventas.py` | **Modified** | Agregar `costo_unitario` al modelo `Item` |
| `routes/comisiones.py` | **New** | Blueprint `bp_comisiones` con ~25 rutas |
| `services/comisiones/` | **New** | 8 archivos: planes, asignaciones, calculator, liquidaciones, repositories, constants, validators |
| `services/ventas/ventas.py` | **Modified** | Capturar `costo_unitario = articulo.costo` en creación de Item |
| `templates/comisiones/` | **New** | 9 templates: index, planes, plan_form, reglas, asignaciones, calcular, liquidaciones, liquidacion_detalle, reportes |
| `static/js/comisiones.js` | **New** | JS para CRUD dinámico, previsualización, expand/collapse |
| `index.py` | **Modified** | Import + register_blueprint (~2 líneas) |
| `templates/partials/_sidebar.html` | **Modified** | Agregar link "Comisiones" al menú |
| `SQL/` | **New** | Script de migración: ALTER itemsv + 6 CREATE TABLE + índices |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Breaking sales flow al modificar itemsv | Med | ALTER solo agrega columna DEFAULT 0; modelo Item mantiene __init__ existente con default; código de ventas unchanged hasta integración |
| N+1 queries en cálculo masivo | Med | Repositories cargan batch: 1 query ventas, 1 items, 1 artículos, 1 clientes; trabajo en memoria |
| Liquidación confirmada recalculada | Baja | Estado CONFIRMADA bloquea recálculo; solo permite ANULAR + nueva |
| Duplicación de comisiones | Baja | UNIQUE constraint: (id_liquidacion, id_factura, id_item, id_regla) |
| Asignaciones superpuestas | Med | Validators.check_superposicion() antes de insertar |
| Performances en períodos grandes | Med | Batch processing + índices en facturav.fecha, facturav.idusuario, itemsv.idfactura |

## Rollback Plan

1. **DB**: Ejecutar script de rollback (`DROP TABLE comisiones_*; ALTER TABLE itemsv DROP COLUMN costo_unitario`)
2. **Code**: Revertir commits del módulo en orden inverso (templates → routes → services → models → index.py)
3. **Sales flow**: Si costo_unitario causa problemas, la columna DEFAULT 0 no afecta ventas existentes; rollback del ALTER es safe
4. **Liquidaciones**: Las liquidaciones confirmadas son inmutables; rollback no borra datos históricos

## Dependencies

- Existing `facturav`, `itemsv`, `articulos`, `usuarios` tables (no changes to structure)
- `@check_session` decorator for auth
- `text()` for raw SQL in repositories (project convention)
- `Decimal` for all monetary values
- MySQL 5.7+ for JSON support (if needed for future rule criteria)

## Success Criteria

- [ ] CRUD de planes funciona: crear, editar, activar/desactivar, duplicar
- [ ] Asignación de vendedores con validación de superposición
- [ ] Cálculo correcto para las 7 modalidades de v1
- [ ] Notas de crédito generan comisión negativa
- [ ] costo_unitario se captura en la misma transacción de venta
- [ ] Liquidación confirmada no se recalcula al modificar planes
- [ ] Detalle auditable muestra regla aplicada, base, porcentaje, resultado
- [ ] Reportes generan datos correctos por vendedor, período, artículo, regla
- [ ] No se duplican comisiones (misma factura+item+regla en misma liquidación)
- [ ] Queries batch evitan N+1 (verificar con 1000+ items)
- [ ] Roles: admin todo, supervisor consulta/previsualización, vendedor solo sus datos
- [ ] Sales flow existente no se rompe (ventas, notas de crédito, presupuestos)
