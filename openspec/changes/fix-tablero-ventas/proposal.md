# Propuesta: fix-tablero-ventas

## Intent

Los 3 gráficos del tablero gerencial (`templates/tablero.html`) — "Ventas últimos 6 meses", "Ingresos de hoy", "Ventas por rubros últimos 6 meses" — se muestran vacíos. Causa raíz: regresión del commit `219aac2` que agregó CSP con nonce (`index.py:127-138`) pero no actualizó los 4 bloques inline `<script>` de `tablero.html` que asignan los datos de los gráficos → el navegador los bloquea y las variables quedan `undefined`. Restaurar el comportamiento esperado (gráficos con datos) y endurecer las dos fallas latentes de la misma superficie.

## Scope

### In Scope
- Agregar `nonce="{{ g.nonce }}"` a los 4 scripts inline de `templates/tablero.html` (L167-170, L203-206, L249-252, L263-266). Patrón ya establecido en `base.html:35,132` y `articulos.html:125`.
- Eliminar el bloque muerto `barrasRubros` en `static/js/demo/chart-bar-demo.js` (L122-126+): referencia a canvas inexistente → `new Chart(null, ...)` lanza error de consola en cada carga.
- Envolver `get_vta_rubros` (`services/ventas/reportes.py:275-290`) en try/except que devuelva listas vacías (mismo patrón que `ventas_por_mes`): evita 500 en `/tablero-inicial`, ruta que este cambio toca (lo llama `routes/tableros.py:44`).

### Out of Scope
- `tablero.html:291-346`: loops sobre `proximosEventos`/`proximasCitas`/`proximasCuotas`/`cuotasVencidas` (vars nunca provistas desde `e6e7d2b`) → follow-up con decisión de producto.
- Contexto incompleto de `tablero_administrativo` (`routes/tableros.py:106`: `saldo_clientes` tupla, sin rubros/sucursales/vendedores/creditos) → follow-up separado.
- Refactor arquitectónico (datos vía JSON+fetch o JS externo único) → no necesario para un bug fix.

## Capabilities

> No existe spec previa del tablero (`openspec/specs/` solo tiene `ventas-idempotencia`, `articulos-api-json`).

### New Capabilities
- `tablero-ventas`: render del tablero gerencial — los gráficos MUST mostrar datos reales; los scripts inline MUST cumplir CSP con nonce; las consultas de reporte MUST degradar a listas vacías sin 500.

### Modified Capabilities
- None

## Approach

Fix directo en 3 archivos (~15 líneas):
1. `tablero.html`: `nonce="{{ g.nonce }}"` en los 4 `<script>` inline (restaura los datos; el JS externo se carga al final de la página, L580-584, por lo que lee las variables ya asignadas).
2. `chart-bar-demo.js`: borrar bloque `barrasRubros` (código muerto, el canvas no existe en el template).
3. `reportes.py`: try/except en `get_vta_rubros` devolviendo `{'rubros': [], 'vtaRubros': [], 'cantRubros': []}`.

`g.nonce` siempre existe (seteado en `before_request`, `index.py:66`). Sin runner de tests (`config.yaml` testing vacío): verificación manual en `/tablero-inicial`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `templates/tablero.html` | Modified | 4 scripts inline con nonce CSP |
| `static/js/demo/chart-bar-demo.js` | Modified | Elimina bloque muerto `barrasRubros` |
| `services/ventas/reportes.py` | Modified | try/except en `get_vta_rubros` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Nonce mal aplicado (script bloqueado) | Low | Mismo patrón exacto que base.html/articulos.html; verificación manual de consola |
| SP `venta_rubros` ausente en algún entorno | Low | try/except → degradación silenciosa (mitiga el 500 actual) |
| Regresión de estilo de código | Low | Sigue patrón existente (Spanish, try-except-rollback) |

## Rollback Plan

Revertir el commit del fix (git revert). Los 3 cambios son independientes entre sí; si uno falla, se revierte solo ese archivo. Sin migraciones ni cambios de esquema.

## Dependencies

- Ninguna. `g.nonce` garantizado por `before_request`. SP `get_vta_desde_hasta`/`venta_rubros` ya existen en BD (externos al repo, `SQL/` gitignored).

## Success Criteria

- [ ] Cargar `/tablero-inicial`: los 3 gráficos muestran datos (barras 6 meses, doughnut ingresos hoy, 2 pies de rubros).
- [ ] Consola del navegador sin errores de CSP ni "Failed to create chart: can't acquire context".
- [ ] `get_vta_rubros` no produce 500 si el SP falla (prueba manual opcional).
- [ ] `tablero_administrativo` y `tablero_basico` siguen renderizando sin errores nuevos.