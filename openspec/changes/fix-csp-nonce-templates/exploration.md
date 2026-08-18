# Exploración: fix-csp-nonce-templates

> Fase: sdd-explore · Modo artefacto: openspec · Proyecto: crm
> Fecha: 2026-08-17 · Solo investigación, sin modificación de código.

## Problema

El commit `219aac2` (2026-07-29, "se actualizaron varias funciones generales...") agregó una política CSP estricta en `index.py:127-138`:

```python
script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net https://unpkg.com;   # SIN 'unsafe-inline'
style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com;
```

- `g.nonce` se setea por request en `before_request` (`index.py:66`).
- El único template que recibió nonce en ese commit fue `base.html` (L35, L132). Todos los demás scripts inline del proyecto quedaron bloqueados por el navegador (regresión silenciosa: charts vacíos, tablas sin init, botones muertos).
- El fix de `tablero.html` (cambio archivado `fix-tablero-ventas`, commit `65df9a2`) y `tablero-basico.html` (`d1047ac`) corrigieron 5 scripts. El verify de ese cambio sugirió explícitamente una auditoría sistémica ("40+ templates con `<script>` inline sin nonce") → este cambio.

## Estado actual (verificado en código)

- **CSP sin `unsafe-inline` en script-src**: TODO `<script>` inline sin nonce es bloqueado (comportamiento estándar CSP3; el mecanismo ya fue confirmado empíricamente en el exploration de `fix-tablero-ventas`: "Refused to execute inline script...").
- **`style-src` SÍ tiene `unsafe-inline`** → los estilos inline (`style=""`) y los bloques `<style>` NO están bloqueados. **No requieren auditoría.**
- **`connect-src 'self'`** → fetch/AJAX same-origin OK (DataTables serverSide, fetch de líneas de comprobantes) una vez que el script que los dispara corra.
- **Sin `javascript:` URLs** en templates (grep = 0). **Sin `eval()`/`new Function`** en `static/js` (grep = 0) → no hay problema de `unsafe-eval`.
- **Patrón establecido confirmado**: `<script nonce="{{ g.nonce }}">` en `base.html:35,132`, `tablero.html:167,203,249,263`, `tablero-basico.html:145`, `articulos.html:125`. `g.nonce` se inyecta a TODAS las plantillas (before_request global) → funciona igual en partials incluidas con `{% include %}` (render server-side, mismo contexto).

## Inventario completo: scripts inline SIN nonce (54 bloques · 47 archivos)

Patrón de búsqueda: `^\s*<script>` (sin `src=`, sin `nonce=`) + `templates/ventas/factura-print.html:41` (`<script type="module">` inline, variante que el grep base no captura).

### ventas — 15 scripts / 13 archivos (ALTO impacto, flujo comercial core)

| Archivo | Línea(s) | Qué hace | Estado |
|---|---|---|---|
| `ventas/nueva_venta.html` | 230 | Asigna `window.PRESUPUESTO` (precarga de presupuesto en la venta) | Funcional |
| `ventas/nueva_venta.html` | 254 | Asigna `window.REMITO` (precarga de remito en la venta) | Funcional |
| `ventas/nueva_venta.html` | 283 | `sincronizarTotal`, fila "no items", animación total | Funcional |
| `ventas/nueva_ncredito.html` | 299 | `sincronizarTotal`, ocultar spinner, sync total | Funcional |
| `ventas/nuevo_remito.html` | 326 | `limpiarFormulario`, `mostrarEstadoVacio`, total, foco cliente | Funcional |
| `ventas/nuevo_presupuesto.html` | 338 | Ídem nuevo_remito | Funcional |
| `ventas/presupuestos.html` | 527 | `limpiarFiltros`, `exportarExcel`, `imprimirTabla`, selección masiva, cambiar estado | Funcional |
| `ventas/remitos.html` | 390 | Ídem patrón listado (filtros/export/print/masivo) | Funcional |
| `ventas/ventas.html` | 339 | Filtros/export/imprimir listado de facturas | Funcional |
| `ventas/ventas-articulos.html` | 318 | Reporte artículos vendidos (filtros/export/print) | Funcional |
| `ventas/ventas-clientes.html` | 371 | Reporte ventas por cliente (filtros/export/print) | Funcional |
| `ventas/ventas-tipo-pagos.html` | 398 | `openTab` (tabs) + filtros/export | Funcional |
| `ventas/ventas-vendedores.html` | 451 | Reporte vendedores (filtros/export/print) | Funcional |
| `ventas/iva-ventas.html` | 302 | Filtros/export/imprimir libro IVA ventas | Funcional |
| `ventas/factura-print.html` | 41 | **`<script type="module">`** — UI impresora térmica/sistema completa (import de `invoice_handler.js`) | Funcional |

### proveedores — 6 scripts / 6 archivos (ALTO: pagos y OPs)

| Archivo | Línea(s) | Qué hace | Estado |
|---|---|---|---|
| `proveedores/nuevo_gasto.html` | 229 | `abrirModalPagos()` + `procesarTransaccion()` (modal de pagos del gasto) | Funcional |
| `proveedores/nueva_op.html` | 108 | `abrirModalPagos()` + `procesarTransaccion()` + `sincronizarCheques()` | Funcional |
| `proveedores/compras.html` | 230 | Export/imprimir listado de compras | Funcional |
| `proveedores/iva-compras.html` | 299 | Filtros/export/imprimir libro IVA compras | Funcional |
| `proveedores/ordenes_pago.html` | 204 | Export/imprimir órdenes de pago | Funcional |
| `proveedores/remitos.html` | 256 | Export/imprimir remitos de compra | Funcional |

### fondos — 6 scripts / 3 archivos (ALTO: charts y rendiciones)

| Archivo | Línea(s) | Qué hace | Estado |
|---|---|---|---|
| `fondos/flujo-fondos.html` | 62 | Chart data `leyendasFlujos`/`totalesFlujos` → gráfico vacío | Funcional |
| `fondos/flujo-fondos.html` | 101 | Chart data `tipoPagos`/`cantPagos` → gráfico vacío | Funcional |
| `fondos/flujo-fondos.html` | 141 | Chart data `detCtasCtes`/`saldosCtasCtes` → gráfico vacío | Funcional |
| `fondos/flujo-fondos.html` | 187 | Chart data `det_gastos`/`total_gastos` → gráfico vacío | Funcional |
| `fondos/rend-cajas.html` | 146 | Cálculo dinámico totales de rendición de caja + guard de submit | Funcional |
| `fondos/lst-rendiciones.html` | 69 | **Bloque VACÍO** (`<script>\n</script>`) | **Muerto** |

### creditos — 4 scripts / 4 archivos (ALTO: otorgamiento y cobranzas)

| Archivo | Línea(s) | Qué hace | Estado |
|---|---|---|---|
| `creditos/otorgamiento.html` | 566 | Wizard de pasos (`actualizarPasoActual`) del otorgamiento | Funcional |
| `creditos/seleccion-cuotas-pago.html` | 376 | `procesarTransaccion()` cobranza (usa funciones universales) | Funcional |
| `creditos/ver-credito.html` | 752 | `creditoData` + `cuotasReales` + `cargarCuotas()` + blur cliente | Funcional |
| `creditos/simulador-creditos.html` | 92 | `datos_plan` + autofill al cambiar plan | Funcional |

### articulos — 6 scripts / 6 archivos (ALTO: tablas de stock no cargan)

| Archivo | Línea(s) | Qué hace | Estado |
|---|---|---|---|
| `articulos/precios-articulos.html` | 116 | DataTables serverSide AJAX (`api_lst_precios`) → tabla vacía | Funcional |
| `articulos/stock-articulos.html` | 121 | DataTables serverSide AJAX (`api_lst_stock`) → tabla vacía | Funcional |
| `articulos/stock-articulos-faltantes.html` | 122 | DataTables serverSide AJAX (`api_lst_stock_faltantes`) → tabla vacía | Funcional |
| `articulos/stock-sucursales.html` | 101 | DataTables con columnas dinámicas (`{{ columnas|tojson }}`) → tabla vacía | Funcional |
| `articulos/rubros-marcas.html` | 14 | DataTables init (marcas y rubros, cliente) | Funcional |
| `articulos/upd-articulos.html` | 568 | Init colores/detalles al editar (`{% if colores_articulo or detalles_articulo %}`) | Funcional |

### configuracion — 7 scripts / 7 archivos (MEDIO)

| Archivo | Línea(s) | Qué hace | Estado |
|---|---|---|---|
| `configuracion/abm-sucursales.html` | 30 | DataTables init (búsqueda/orden client-side) | Funcional |
| `configuracion/puntos-venta.html` | 38 | DataTables init | Funcional |
| `configuracion/configuraciones.html` | 336 | Slider `dias_vto_cc` + cierre modal htmx | Funcional |
| `configuracion/planes-opciones.html` | 61 | **Bloque VACÍO** | **Muerto** |
| `configuracion/partials/_configuracion.html` | 172 | Preview/upload de logo + range | Funcional |
| `configuracion/partials/_lst-puntos-ventas.html` | 103 | fetch modal líneas de comprobantes por punto de venta | Funcional |
| `configuracion/partials/_modal_config_editar.html` | 27 | Cierre modal htmx + notificaciones flash | Funcional |

### partials — 4 scripts / 3 archivos (CRÍTICO: modal de pagos)

| Archivo | Línea(s) | Qué hace | Estado |
|---|---|---|---|
| `partials/_modal-transacciones.html` | 764 | Atajos de teclado (Alt+E/T/C/R/B/Q/V) + foco en campo efectivo del modal | Funcional — **incluido en 5 pantallas**: `nueva_venta.html:69`, `nueva_compra.html:275`, `nueva_op.html:102`, `nuevo_gasto.html:223`, `seleccion-cuotas-pago.html:157` |
| `partials/_modal-transacciones-migracion.html` | 44 | Doc de migración ("ANTES/DESPUÉS") | **Muerto** — archivo NO incluido en ninguna página |
| `partials/_modal-transacciones-migracion.html` | 163 | `abrirModalPagos()` para compras (referencia) | **Muerto** — archivo NO incluido |
| `partials/_modal-transacciones-ejemplos.html` | 108 | Ejemplo de apertura del modal | **Muerto** — archivo NO incluido |

### resto — 6 scripts / 6 archivos

| Archivo | Línea(s) | Qué hace | Estado |
|---|---|---|---|
| `entidades/fin-ent-cred.html` | 157 | `contadorFilas = {{ financiamiento|length }}` (data) | Funcional |
| `entidades/fin-ent-cred.html` | 179 | Alta dinámica de filas de alícuotas + guardado | Funcional |
| `ctactecli/partials/_ctacte-cli.html` | 127 | Auto-cálculo efectivo/tarjeta + validación total del recibo | Funcional |
| `ctacteprov/lst-ctacteprov.html` | 51 | Toggle debe/haber + `checkMovCtaCte()` (validación movimiento) | Funcional |
| `reportes/reporte-gerencial.html` | 597 | `datosReporte` (4 charts) + `inicializarGraficos` → charts vacíos | Funcional |
| `sessions/login.html` | 126 | `APP_PREFIX` + logo en el fondo del login | Funcional |

**Totales**: 54 bloques inline sin nonce en 47 archivos. **49 funcionales** (44 archivos) · **5 muertos** (lst-rendiciones:69, planes-opciones:61, migracion:44+163, ejemplos:108 — 4 de ellos en archivos que no se renderizan).

## Categorización de riesgo (impacto visible por módulo)

- **ALTO / core**: ventas (precarga presupuesto/remito, sincronización de total, listados con export/print, UI de impresión), proveedores (modal de pagos de gastos/OPs), fondos (charts de flujo + rendiciones de caja), creditos (otorgamiento, cobranza, ver crédito), articulos (4 tablas de stock/precios no cargan), ctactecli/ctacteprov (recibos y movimientos), reporte-gerencial (charts).
- **CRÍTICO transversal**: `_modal-transacciones.html:764` — atajos de teclado y foco del modal de pagos que comparten ventas, compras, OPs, gastos y cobranzas.
- **MEDIO**: configuracion (DataTables de sucursales/PV, logo, sliders), entidades, login (solo logo).
- **BAJO / muerto**: lst-rendiciones:69, planes-opciones:61, `_modal-transacciones-migracion.html`, `_modal-transacciones-ejemplos.html` (documentación/referencia, no renderizadas).

## OTRO contenido bloqueado por la CSP (hallazgo clave)

**Los inline event handlers (`onclick=`, `onchange=`, `onfocus=`, `onsubmit=`, etc.) TAMBIÉN están bloqueados.** La CSP actual tiene `script-src 'self' 'nonce-{nonce}'` sin `unsafe-inline` ni `unsafe-hashes`; según CSP3, los atributos de handler inline requieren `unsafe-inline` o `unsafe-hashes` (el nonce NO aplica a handlers, solo a elementos `<script>`). El bloqueo es independiente de los bloques `<script>`.

- **~143 handlers inline en 33 archivos** (grep `\son[a-z]+\s*=`).
- Ejemplos críticos: `nueva_compra.html:240`, `nuevo_gasto.html:188`, `nueva_op.html:80`, `seleccion-cuotas-pago.html:165,351` → `onclick="abrirModalPagos()"`; `nueva_ncredito.html:279` → `onclick="grabarNotaCredito()"` (no se puede guardar una NC); `creditos/partials/_modal-cobranzas.html:125` → `onclick="cobrarCuotas()"`; `partials/_modal-transacciones.html:580-685` → `generarCheque()`, `limpiarCheque()`, `agregarValor()`, `limpiarValores()`, `buscarVale()`; listados de ventas/presupuestos/remitos/compras/OPs → `exportarExcel()`, `imprimirTabla()`, `limpiarFiltros()`.
- **7 archivos con handlers pero SIN script inline** (solo se arreglan con la parte de handlers): `creditos/partials/_modal-cobranzas.html` (8), `clientes/partials/_lst-clientes.html` (1), `configuracion/partials/_permisos_tarea.html` (2), `configuracion/partials/_modal-lineas-comprobantes.html` (1), `proveedores/nueva_compra.html` (1), `entidades/partials/_lst-entidades.html` (1), `articulos/articulos.html` (1 — su script ya tiene nonce).
- **Consecuencia**: agregar nonce a los 54 scripts NO restaura los botones con `onclick=` (quedan muertos aunque la función exista). Para que la app quede funcional completa hay que resolver los handlers por separado (refactor a `addEventListener` o relajar la CSP — ver Enfoques).

**No bloqueado**: estilos inline y `<style>` (style-src con `unsafe-inline`), `javascript:` (0 ocurrencias), `eval` (0 ocurrencias), imágenes data: (img-src `data:`).

## Consistencia del patrón (pregunta 4)

- El patrón correcto es siempre `<script nonce="{{ g.nonce }}">` (idéntico a `base.html:35,132` y a los 5 scripts ya corregidos).
- Para `factura-print.html:41` el patrón es `<script type="module" nonce="{{ g.nonce }}">` (mismo mecanismo, el nonce funciona con módulos inline).
- Los partials incluidos con `{% include %}` (p.ej. `_modal-transacciones.html`, `_configuracion.html`, `_lst-puntos-ventas.html`, `_modal_config_editar.html`, `_ctacte-cli.html`) se renderizan server-side con el mismo contexto → `g.nonce` disponible. **Sin diferencia de comportamiento.**
- `g.nonce` siempre existe (before_request, index.py:66) — mismo argumento ya validado en el fix de tablero.

## Historia git (pregunta 6)

- **`219aac2` agregó la CSP desde cero** (`git show 219aac2 -- index.py`: todo `+`; antes NO existía header CSP). Por lo tanto TODOS los scripts inline y handlers funcionaban antes de ese commit → **regresión limpia, no features pre-rotas**.
- `219aac2` tocó 11 templates pero solo nonceó `base.html` (L35, L132). **Dejó sin nonce scripts inline en archivos que ÉL MISMO modificó**: `partials/_modal-transacciones.html:764`, `sessions/login.html:126`, `ventas/nueva_ncredito.html:299`, `ventas/nueva_venta.html:230/254/283`, `ventas/nuevo_presupuesto.html:338`, `ventas/nuevo_remito.html:326` → fix incompleto en el propio commit de la regresión.
- Los 39 archivos restantes con scripts inline son features viejas (flujo-fondos 2025-06, stock-sucursales 2025-12, ver-credito 2025-12, puntos-venta 2026-03, reporte-gerencial 2026-05) → rotas por el cambio de política, no por cambios propios recientes.
- El cambio archivado `fix-stock-sucursales-datatables` (2026-08-07, posterior a la CSP) tocó `stock-sucursales.html` pero no el nonce: su script inline L101 siguió bloqueado — la verificación fue con pytest (sin navegador) y no detectó el bloqueo CSP. Refuerza la narrativa de regresión silenciosa.

## Alcance estimado (pregunta 5)

**Solo scripts (nonce):**
- 49 bloques funcionales en 44 archivos → ~49 líneas cambiadas (+1 por tag).
- Incluyendo los 5 muertos: 54 líneas / 47 archivos.
- **Muy por debajo de las 400 líneas** → un solo PR viable por tamaño. La superficie de review es ancha (44-47 archivos) pero mecánica (~1 línea por archivo). Aún así, se puede encadenar por módulo si se quiere review más fino (ventas 15 · articulos+config 13 · fondos+creditos+resto 16).
- Riesgo: bajo (mismo cambio que el fix de tablero, ya validado).

**Handlers inline (refactor a addEventListener):**
- ~143 handlers en 33 archivos → estimación 350-550 líneas totales (2-4 líneas por handler + movimientos de definiciones) → **supera las 400 líneas → requiere PRs encadenados por módulo** (ventas ~70 · proveedores+creditos+ctacte ~45 · partials+entidades+config+fondos+articulos+reportes ~28).

## Enfoques

| Enfoque | Pros | Contras | Esfuerzo |
|---|---|---|---|
| **A. Nonce en los 54 scripts (este cambio)** | Restaura charts, DataTables, lógica de formularios, atajos de teclado, validaciones, precargas; patrón ya establecido; ~54 líneas; riesgo bajo | NO restaura los ~143 `onclick=` (botones siguen muertos); 47 archivos de superficie | Bajo |
| **B. A + refactor de handlers a `addEventListener` (PRs encadenados por módulo)** | App completa funcional; alineado con el propósito de 219aac2 (endurecer XSS) | Esfuerzo alto (33 archivos, 143 handlers); riesgo de romper flujos si la función no queda accesible desde el script con nonce | Alto |
| **C. A + `'unsafe-inline'` en script-src manteniendo nonce** | Un cambio de 1 línea en index.py desbloquea todos los handlers; los `<script>` sin nonce SIGUEN bloqueados (la presencia de nonce anula unsafe-inline para elementos script) | Vuelve a habilitar vectores XSS vía atributos de handler (contradice el propósito del commit); requiere decisión explícita del usuario como tradeoff de seguridad | Bajo |
| **D. `'unsafe-hashes'` con hashes de cada handler** | Sin refactor, sin re-habilitar todo unsafe-inline | Impracticable: 143 hashes frágiles (cualquier cambio de template invalida el hash) | Alto |

## Recomendación

**Enfoque A como alcance de `fix-csp-nonce-templates`**: agregar `nonce="{{ g.nonce }}"` a los 54 scripts inline (49 funcionales + 5 muertos por uniformidad, o excluir los 4 de archivos de referencia no renderizados — decisión menor). Un solo PR (~54 líneas), mismo patrón y mismo riesgo que el fix de tablero ya validado.

**Decisión obligatoria para el orchestrator/usuario**: la app NO queda totalmente funcional solo con A, porque los ~143 handlers inline (`onclick=` etc.) siguen bloqueados por la CSP (el nonce no aplica a handlers). Opciones reales: **B** (refactor a `addEventListener`, PRs encadenados por módulo, alineado con el endurecimiento) o **C** (re-habilitar handlers vía `unsafe-inline` + nonce, tradeoff de seguridad que debe aprobar el usuario). Recomiendo B como camino correcto a largo plazo; C como mitigación temporal si el usuario necesita la app usable ya y acepta el tradeoff. La propuesta debe dejar explícito este fork.

## Riesgos

- **Riesgo principal del enfoque A: casi nulo** (atributo agregado, `g.nonce` garantizado, mismo fix ya aplicado en 3 templates).
- Si se elige C: regresión parcial de seguridad (handlers inline vuelven a ejecutarse) — mitigado por el nonce que sigue protegiendo los bloques `<script>`.
- Si se elige B: cada archivo debe verificar que las funciones llamadas por los handlers queden en scope del script con nonce (la mayoría ya lo están: `exportarExcel`, `imprimirTabla`, `abrirModalPagos`, etc. se definen en el mismo bloque inline).
- Sin runner de tests (config.yaml testing vacío): verificación manual en navegador — cargar pantallas clave (nueva_venta, presupuestos, flujo-fondos, stock-articulos, rend-cajas, seleccion-cuotas-pago) y revisar consola sin "Refused to execute inline script/event handler".
- `{{ ...|tojson }}` y `|safe` dentro de los scripts (p.ej. `reporte-gerencial.html:601-613`, `upd-articulos.html:574`) siguen funcionando igual con nonce (no cambia el render server-side).

## Listo para propuesta

Sí. El orchestrator debe indicar en la propuesta:
1. Alcance del cambio: nonce en los 54 scripts inline (o 49 funcionales excluyendo muertos/referencias).
2. Incluir `factura-print.html:41` con `<script type="module" nonce="{{ g.nonce }}">`.
3. **Fork explícito a resolver con el usuario**: handlers inline (~143 en 33 archivos) → refactor B (encadenado por módulo) vs relajación C (`unsafe-inline` + nonce) vs diferir. No se puede declarar "app funcional completa" sin resolver los handlers.
4. No hay tests; verificación manual por pantalla (listar en tasks).