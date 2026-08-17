# Diseño: fix-tablero-ventas

## Enfoque técnico

Fix directo de ~15 líneas en 3 archivos, sin migraciones ni cambios de esquema:

1. **`templates/tablero.html`** — agregar `nonce="{{ g.nonce }}"` a los 4 `<script>` inline (L167, L203, L249, L263). Causa raíz: la regresión `219aac2` (CSP con nonce) bloquea estos scripts → las variables globales (`mesess`, `eventoss`, `tipoPagos`, `cantPagos`, `nombresRubros`, `ventasRubros`, `cantidadRubros`) quedan `undefined` y Chart.js renderiza vacío. El JS externo (L580-584) se carga al final del body y lee esas variables ya asignadas.
2. **`static/js/demo/chart-bar-demo.js`** — eliminar el bloque muerto `barrasRubros` (L120-203): el canvas `barrasRubros` no existe en ningún template → `new Chart(null, ...)` lanza "Failed to create chart: can't acquire context" en cada carga de `/tablero-inicial`.
3. **`services/ventas/reportes.py`** — envolver `get_vta_rubros` (L275-290) en try/except que devuelva listas vacías, mismo patrón que `ventas_por_mes`/`pagos_hoy` del mismo archivo.

## Decisiones de arquitectura

| Decisión | Opciones | Tradeoff | Elección |
|----------|----------|----------|----------|
| Nonce por script | 1 por request vs. 1 por script | El nonce es por-request (`index.py:66` `secrets.token_hex(16)`, usado también por el header CSP en `after_request`) | Los 4 scripts usan `{{ g.nonce }}` (mismo valor por respuesta) — patrón idéntico a `base.html:35,132` y `articulos.html:125`; sin problemas de caché (nonce y header se regeneran por request) |
| Manejo de error `get_vta_rubros` | Re-raise vs. degradar silenciosa | Re-raise → 500 en `/tablero-inicial` si el SP `venta_rubros` falta en algún entorno | Degradar: `print` en español + dict con listas vacías, replicando `ventas_por_mes` (L265-272) y `pagos_hoy` (L317-324). Sin `rollback`: consultas de solo lectura, patrón del archivo no lo usa |
| Eliminación código muerto | Borrar bloque completo vs. dejarlo | El bloque L120-203 usa canvas inexistente; `nombresRubros`/`ventasRubros` (L123-124) se redeclaran en `chart-pie-demo.js:14-16` | Borrar L120-203 (bloque completo hasta EOF). `number_format`, `coloresBarras` y `myBarChart` (L1-119) se conservan: los usa el gráfico de barras |
| Alcance `tablero_administrativo` | Parchear ruta vs. dejarla | La ruta (L106) ya 500a hoy: renderiza `tablero.html` sin `ventasSucursales`/`ventasVendedores` → `{% for %}` sobre Undefined | Fuera de alcance (pre-existente, no es regresión CSP). Verificado por análisis estático; no empeora con este fix |

## Flujo de datos

```
GET /tablero-inicial
  routes/tableros.py:44 ──► get_vta_rubros(fecha_inicio, fecha_hoy)
      │  try:  db.session.execute(text("CALL venta_rubros(:desde,:hasta)"))
      │  except: print('Error calculando ventas por rubros:') → {'rubros':[],'vtaRubros':[],'cantRubros':[]}
      ▼
  render_template('tablero.html', ...)   ──►  <script nonce="{{ g.nonce }}"> asignan vars globales
      ▼
  JS externo (L580-584): chart-pie-demo.js crea myPieChart2/3 con esas vars
  Header CSP (after_request, index.py:130) autoriza los inline con el mismo nonce
```

Listas vacías son toleradas por Chart.js (`labels: []` / `data: []` → pies vacíos sin error de consola); `null` no lo sería, por eso la degradación devuelve listas y no `None`.

## Cambios de archivos

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `templates/tablero.html` | Modificar | `<script>` → `<script nonce="{{ g.nonce }}">` en L167, L203, L249, L263 (solo la línea de apertura, respetando indentación) |
| `static/js/demo/chart-bar-demo.js` | Modificar | Borrar L120-203 (blanco + bloque `barrasRubros` completo hasta EOF); queda el gráfico `myBarChart` |
| `services/ventas/reportes.py` | Modificar | `get_vta_rubros`: envolver cuerpo en `try:`; `except Exception as e:` → `print('Error calculando ventas por rubros:', str(e))` y `return {'rubros': [], 'vtaRubros': [], 'cantRubros': []}` |

## Interfaces / Contratos

`get_vta_rubros` (contrato estable): devuelve siempre `{'rubros': list, 'vtaRubros': list, 'cantRubros': list}` — con datos o vacías. Los consumidores (`routes/tableros.py:52`, template L250-251/264-265) no cambian.

## Estrategia de pruebas

| Capa | Qué probar | Cómo |
|------|-----------|------|
| Manual (no hay runner; `config.yaml` testing vacío) | `/tablero-inicial`: 3 gráficos con datos | Checklist: barras 6 meses con datos; doughnut ingresos hoy; 2 pies de rubros |
| Manual | Consola sin errores | Sin violaciones CSP (Refused to execute inline script), sin "can't acquire context", sin "length of null" |
| Manual | Degradación | Probar `/tablero-inicial` con SP roto (opcional) → página 200 con pies vacíos |
| Manual (regresión) | `/tablero-basico` y rutas que usan chart scripts | `chart-bar/pie-demo.js` solo los carga `tablero.html` (grep verificado); `flujo-fondos.html` solo menciona en comentario → sin impacto |

## Migración / Rollout

No aplica: sin migraciones, sin flags, sin cambios de esquema. Rollback: `git revert` del commit del fix; los 3 cambios son independientes.

## Preguntas abiertas

- [ ] **`tablero_administrativo` pre-existente**: 500a hoy por contexto incompleto (fuera de alcance según propuesta). Recomendación: mantener fuera; verificar solo que el 500 es el mismo pre-fix (no empeora). ¿Confirmar en apply que no se toca?
- [ ] **CSP sistémico**: 40+ templates tienen `<script>` inline sin nonce (grep). Fuera de alcance; recomendar follow-up de auditoría CSP.