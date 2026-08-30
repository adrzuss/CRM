# Proposal: Aplicar Redondeo en Cambio de Precio

## Intent

El cambio de precio (cambio-precio) calcula `precio_nuevo` como `precio_actual * (1 + porcentaje/100)` pero no aplica las reglas de redondeo configuradas en `ReglaRedondeo`. Los usuarios necesitan que los precios resultantes respeten los múltiplos y dirección de redondeo definidos en configuración, evitando manuales de ajuste post-cálculo.

## Scope

### In Scope
- Crear `services/articulos/redondeo.py` con funciones `aplicar_redondeo()` y `calcular_precio_comercial()`
- Modificar `obtenerArticulosMarcaRubro()` (línea 305 de `articulos.py`) para consultar reglas activas y aplicar redondeo por artículo
- Actualizar `services/articulos/__init__.py` para exportar nuevas funciones

### Out of Scope
- Cambios en JS/frontend — el precio redondeado llega pre-aplicado
- Modificar el modelo `ReglaRedondeo` (ya existe y es funcional)
- Cambios en la UI de configuración de reglas

## Capabilities

### New Capabilities
- `redondeo-cambio-precio`: Aplicación de reglas de redondeo comercial al calcular precios nuevos en el endpoint de cambio de precio por marca/rubro

### Modified Capabilities
- None — `reglas-redondeo` spec exists but its requirements (CRUD) don't change; this change adds consumers of those rules

## Approach

1. **Crear `services/articulos/redondeo.py`** con las dos funciones proporcionadas por el usuario:
   - `aplicar_redondeo(precio_base, multiplo, tipo, restar)` — redondeo comercial puro
   - `calcular_precio_comercial(precio_lista, porcentaje, reglas_db)` — lógica de selection + aplicación

2. **Modificar `obtenerArticulosMarcaRubro()`** (articulos.py línea 305):
   - Query a `ReglaRedondeo` con `activo=True` una vez por request (antes del loop)
   - Para cada artículo, tras calcular `precio_nuevo`, buscar regla aplicable por rango (`desde_precio <= precio_nuevo <= hasta_precio`)
   - Si regla encontrada: aplicar redondeo con `aplicar_redondeo()`
   - Si no: dejar `precio_nuevo` sin cambios (fallback seguro)

3. **Exportar** desde `__init__.py`

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `services/articulos/redondeo.py` | NEW | Funciones de redondeo comercial |
| `services/articulos/articulos.py:305` | MODIFY | Loop de cálculo de precio_nuevo ahora consulta reglas |
| `services/articulos/__init__.py` | MODIFY | Agregar exports de redondeo |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Performance: query a ReglaRedondeo por request | Low | Query única antes del loop, cachear si escala. Reglas son pocas (<20 típicamente) |
| Sin regla aplicable para un rango de precio | Low | Fallback: dejar precio_nuevo sin redondear (comportamiento actual) |
| Precios con decimales inesperados | Medium | Usar `Decimal` consistente, testear con casos edge (multiplo=0.50, precio=99.99) |

## Rollback Plan

1. Revertir cambios en `articulos.py` (restaurar línea 305 original)
2. Eliminar `services/articulos/redondeo.py`
3. Revertir exports en `__init__.py`
4. No hay migraciones DB — el modelo `ReglaRedondeo` ya existe

## Dependencies

- Modelo `ReglaRedondeo` existente en `models/configs.py:287-305`
- Reglas de redondeo deben estar configuradas en DB para que el feature tenga efecto

## Success Criteria

- [ ] `precio_nuevo` en respuesta de cambio-precio refleja redondeo cuando existe regla activa aplicable
- [ ] Sin regla aplicable, comportamiento es idéntico al actual (sin regressión)
- [ ] Tests unitarios para `aplicar_redondeo()` cubren: arriba, abajo, cercano, con restar
- [ ] Test de integración verifica flujo completo: regla DB → aplicar → precio redondeado en response
