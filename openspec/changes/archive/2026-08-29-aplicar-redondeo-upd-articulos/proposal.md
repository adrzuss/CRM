# Proposal: Aplicar Redondeo en upd-articulos

## Intent

Cuando el costo de un artículo cambia en upd-articulos.html, `precioVP` se calcula como `markup × costoTotal` (línea 65 de upd-articulos.js) sin aplicar las reglas de redondeo configuradas en `ReglaRedondeo`. Los usuarios necesitan que los precios de venta respeten los múltiplos y dirección de redondeo definidos en configuración, evitando ajustes manuales post-cálculo.

## Scope

### In Scope
- Backend: Consultar reglas `ReglaRedondeo` activas en `update_articulo` GET, pasar al template
- Template: Serializar reglas a JSON para acceso desde JavaScript
- JS: Implementar función `aplicarRedondeo()` + aplicar después de `markup × costoTotal`

### Out of Scope
- Modificar el modelo `ReglaRedondeo` (ya existe y es funcional)
- Cambios en la UI de configuración de reglas
- Modificar otros cálculos de precio fuera de upd-articulos

## Capabilities

### New Capabilities
- `redondeo-upd-articulos`: Aplicación de reglas de redondeo comercial al calcular precioVP en el formulario de edición de artículos

### Modified Capabilities
- None — `reglas-redondeo` spec exists but its requirements (CRUD) don't change; this change adds un nuevo consumidor de esas reglas

## Approach

1. **Backend (`routes/articulos.py`)**: En `update_articulo` GET, consultar `ReglaRedondeo` con `activo=True` y pasar al template como variable

2. **Template (`templates/articulos/upd-articulos.html`)**: Serializar reglas a JSON usando `{{ reglas_redondeo | tojson }}` en un script tag

3. **JavaScript (`static/js/upd-articulos.js`)**:
   - Implementar función `aplicarRedondeo(precio, reglas)` que busque regla aplicable por rango y aplique redondeo
   - Modificar `calcularPrecio()` para aplicar redondeo después de calcular precioVP
   - Reutilizar lógica similar a `services/articulos/redondeo.py` pero en JavaScript

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `routes/articulos.py:141-211` | MODIFY | Agregar query de ReglaRedondeo y pasar al template |
| `templates/articulos/upd-articulos.html` | MODIFY | Serializar reglas a JSON para JS |
| `static/js/upd-articulos.js:42-67` | MODIFY | Implementar redondeo en calcularPrecio() |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Duplicación de lógica JS/Python (~15 líneas) | Low | Función simple y estable; considerar extraer a shared module si evoluciona |
| Precisión de float en JavaScript | Medium | Usar `toFixed(2)` consistente, testear con casos edge (multiplo=0.50, precio=99.99) |
| Reglas no configuradas en DB | Low | Fallback: sin reglas = comportamiento actual (sin redondeo) |

## Rollback Plan

1. Revertir cambios en `routes/articulos.py` (restaurar query original)
2. Revertir cambios en template (remover serialización JSON)
3. Revertir cambios en JS (restaurar cálculo original línea 65)
4. No hay migraciones DB — el modelo `ReglaRedondeo` ya existe

## Dependencies

- Modelo `ReglaRedondeo` existente en `models/configs.py:287-305`
- Reglas de redondeo deben estar configuradas en DB para que el feature tenga efecto
- Servicio `services/articulos/redondeo.py` existe como referencia para lógica de redondeo

## Success Criteria

- [ ] `precioVP` en upd-articulos refleja redondeo cuando existe regla activa aplicable
- [ ] Sin reglas activas, comportamiento es idéntico al actual (sin regressión)
- [ ] Función `aplicarRedondeo()` en JS cubre: arriba, abajo, cercano, con restar
- [ ] Test manual verifica: cambiar costo → precioVP redondeado según regla configurada