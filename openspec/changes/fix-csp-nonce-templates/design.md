# Diseño: fix-csp-nonce-templates

> Fase: sdd-design · Modo artefacto: openspec · Proyecto: crm
> Fecha: 2026-08-17 · Base: `exploration.md` + `proposal.md` (lectura completa) · Verificación de código en templates/static/index.py.

## Resumen ejecutivo

Restaurar la funcionalidad bloqueada por la CSP estricta de `219aac2` en dos frentes, sin tocar la política (`index.py` queda intacto):

1. **(a) Nonce**: `nonce="{{ g.nonce }}"` en los 54 `<script>` inline sin nonce (47 archivos).
2. **(b) Handlers**: eliminar los ~143 atributos `on[a-z]+=` (32 archivos) y cablear con `addEventListener` vanilla dentro de los mismos bloques inline que (a) noncea.

La cadena de 7 PRs de la propuesta se mantiene, con **2 desviaciones verificadas en el código** (ver §7): `_modal-cobranzas.html` es código muerto (0 referencias) → se excluye del refactor; y el script inline de `_modal-transacciones.html:764-833` es redundante con `modal-transacciones-universal.js` y además está roto por timing de jQuery → se reemplaza por un bloque mínimo vanilla.

---

## 1. Decisiones de diseño (ADR)

### ADR-1: Patrón nonce estándar

**Contexto**: El patrón ya validado en `base.html:35,132`, `tablero.html:167,203,249,263`, `tablero-basico.html:145`, `articulos.html:125`.

**Decisión**: Todo `<script>` inline sin `src=` y sin `nonce=` recibe `nonce="{{ g.nonce }}"`:

```html
<script nonce="{{ g.nonce }}">
    // ...
</script>
```

**Variante module** (`factura-print.html:41`):

```html
<script type="module" nonce="{{ g.nonce }}">
```

**Racional**: `g.nonce` se setea en `before_request` (`index.py:66`) para TODAS las respuestas, incluidos los partials renderizados server-side con `{% include %}` (mismo contexto Jinja, mismo documento → mismo nonce). El mecanismo ya fue confirmado empíricamente en `fix-tablero-ventas` ("Refused to execute inline script..." desaparece con nonce). Los módulos inline aceptan nonce igual que los clásicos.

### ADR-2: jQuery NO está disponible en parse-time de los scripts inline del body

**Contexto (verificado)**: `base.html:124` carga `vendor/jquery/jquery.min.js` DESPUÉS de `{% block body %}` (`base.html:68-70`). Todos los scripts inline de templates hijos viven dentro del body block → ejecutan **antes** de jQuery. La posición es la misma desde antes de la CSP (verificado en `219aac2~1:templates/base.html:122`).

**Evidencia adicional**: `presupuestos.html:890` ya guarda `typeof $ !== 'undefined'` antes de init de DataTables — el autor ya sabía que `$` puede no existir en ese punto. `ventas.html:494` y `presupuestos.html:960` recargan jQuery al final del template (después de su script inline), confirmando el patrón "jQuery se carga tarde".

**Decisión**:
- El wiring nuevo usa **exclusivamente `addEventListener` vanilla** (nunca `$(el).on(...)`).
- Los callbacks pueden usar `$` libremente (ejecutan en interacción del usuario, cuando jQuery ya cargó).
- Cualquier init que requiera jQuery (DataTables, `$(...).modal('show')`) se deja **dentro de los bloques inline existentes que ya lo hacen** (p.ej. `presupuestos.html:861` DOMContentLoaded + guard `typeof $ !== 'undefined'`), o se conserva tal cual (los templates que recargan jQuery antes de su script, p.ej. `stock-articulos.html:118`).
- **No se mueve jQuery ni se altera el orden de scripts** (fuera de alcance).

### ADR-3: Referencias perezosas a funciones globales (módulos deferred)

**Contexto**: Los módulos (`type="module"`, p.ej. `nueva_venta.js`, `modal-transacciones-universal.js`, `nueva_compra.js`, `seleccion-cuotas-pagos.js`, `permisos-menu.js`) son *deferred* → ejecutan DESPUÉS del parse del documento. Los scripts inline clásicos al final del body ejecutan DURANTE el parse. Por lo tanto `window.abrirModalPagos` **aún no existe** cuando el wiring inline corre en parse-time.

**Decisión**: El wiring referencia funciones globales **de forma perezosa, dentro del callback**:

```js
// ❌ NO: evalúa window.fn en parse-time (undefined con módulos deferred)
btn.addEventListener('click', window.abrirModalPagos);
// ✅ SÍ: referencia perezosa, se resuelve al hacer click (módulos ya cargados)
btn.addEventListener('click', function () {
    window.abrirModalPagos();
});
```

**Racional**: Conserva el patrón `window.*` existente (load-bearing: `modal-transacciones-universal.js:1088` chequea `typeof window.procesarTransaccion === 'function'`; `nueva_venta.js:281`, `nueva_compra.js:537`, `nueva_nota_credito.js:242`, `seleccion-cuotas-pagos.js` exportan sus funciones). Las funciones declaradas con `function f()` en scripts clásicos inline ya son globales por hoisting y pueden llamarse directo en el callback.

### ADR-4: Partials inyectados por HTMX/fetch NO pueden llevar scripts inline

**Contexto (verificado)**:
- `_permisos_tarea.html` se carga por `hx-get` (`permisos-menu.html:30-34`, target `#contenedor-permisos`).
- `_modal-lineas-comprobantes.html` se renderiza en `routes/configs.py:633-640` y se inyecta vía `fetch` + `innerHTML` (`_lst-puntos-ventas.html:111-114`).

**Decisión**: Cualquier script inline dentro de esos partials quedaría bloqueado (el nonce del partial es fresco por request y NO coincide con el nonce del documento principal). Por eso:
- **No se agregan bloques script dentro de partials HTMX/fetch**.
- El wiring se hace por **delegación desde el host** (página/partial que sí se renderiza con el nonce del documento).

### ADR-5: Patrón de wiring — addEventListener vanilla + delegación

**Decisión general** (aplica a todos los archivos con handlers):

1. **Elemento estático con id**: `document.getElementById('x').addEventListener('click', fn)` (o el selector que corresponda), con referencia perezosa si `fn` viene de un módulo.
2. **Elementos repetidos / renderizados dinámicamente** (filas de DataTables, listados): delegación con `closest()`:

```js
document.addEventListener('click', function (e) {
    const btn = e.target.closest('.btn-exportar');
    if (btn) { exportarExcel(); }
});
```

3. **`onfocus="this.select()"` (30 ocurrencias)**: se reemplaza por clase `select-on-focus` en el elemento + **un solo listener delegado `focusin`** por página (dentro del script nonceado del archivo):

```js
document.addEventListener('focusin', function (e) {
    if (e.target.classList && e.target.classList.contains('select-on-focus')) {
        e.target.select();
    }
});
```

**Racional**: `focusin` burbujea (a diferencia de `focus`) → un solo listener cubre todos los inputs, incluso los del modal compartido y los de filas dinámicas. Evita 30 `addEventListener` individuales y duplicados.

4. **Scripts en condicionales Jinja** (`upd-articulos.html:568-571` `{% if colores_articulo or detalles_articulo %}`): el nonce funciona igual (render server-side); el wiring se agrega dentro del mismo bloque condicional.

### ADR-6: `_modal-transacciones.html:764-833` — script inline redundante y roto

**Contexto (verificado)**:
- El script inline usa `$` en parse-time (`L766` `$('#transaccionesModal').on('shown.bs.modal', ...)`) → con jQuery cargado después del body block (ADR-2), **lanza `$ is not defined` y nunca registra nada** (ni el keydown de `L783-831`).
- `modal-transacciones-universal.js` (cargado en las 5 pantallas host: `nueva_venta.html:363`, `nueva_compra.html:285`, `nueva_op.html:105`, `nuevo_gasto.html:226`, `seleccion-cuotas-pago.html:373`) ya cubre: `shown.bs.modal` → foco + `calcSaldo` (`L1057-1066`) y keydown con los atajos Alt+E/T/C/R/B/Q/V + F9 (`L1380-1426`). Es un **superset** del script inline.
- Los 21 handlers del partial (5 `onclick` + 16 `onfocus`) viven en botones/inputs del modal (`L461 buscarVale`, `L580 generarCheque`, `L583 limpiarCheque`, `L682 agregarValor`, `L685 limpiarValores`, y los `onfocus="this.select()"`).

**Decisión**:
- **Reemplazar** el script inline `L764-833` por un bloque mínimo vanilla con el listener delegado `focusin` para `.select-on-focus` (ADR-5). Los atajos de teclado y el foco del modal quedan a cargo del módulo universal (ya funcional).
- Los 5 `onclick` del partial se refactorizan a `addEventListener` vanilla **dentro de ese bloque mínimo** (con referencia perezosa a `window.generarCheque`, etc. — verificado que son exports del módulo universal `L1433+`).
- Los 16 `onfocus="this.select()"` se convierten a `class="... select-on-focus"` (sin listener individual).

**Racional**: Mantener el script inline tal cual + nonce NO lo arregla (sigue lanzando `$ is not defined`); convertirlo a vanilla completo duplicaría los atajos del módulo (doble disparo). El bloque mínimo es el punto medio: wiring local de botones + delegación de foco, sin duplicar lo que el módulo ya hace.

### ADR-7: Handlers en render-strings de DataTables (`articulos.html:175`)

**Contexto**: `articulos.html:175` genera HTML con `onclick="eliminarArticulo(${data})"` dentro de una columna DataTables (string de render). La CSP bloquea handlers inline aunque se generen en runtime (son atributos en el DOM).

**Decisión**: El render string emite un botón con clase + `data-id` (sin `onclick`), y el script nonceado existente (`articulos.html:125`, ya con nonce) agrega delegación sobre el tbody:

```js
document.getElementById('articulosTable').addEventListener('click', function (e) {
    const btn = e.target.closest('.btn-eliminar-articulo');
    if (btn) { window.eliminarArticulo(btn.dataset.id); }
});
```

(`eliminarArticulo` está definido en `static/js/articulos.js:2`.)

### ADR-8: Archivos muertos

**Decisión**:
- `_modal-transacciones-migracion.html` y `_modal-transacciones-ejemplos.html`: **fuera de alcance** (decisión de la propuesta; no se renderizan, quedan como referencia). En PR1 reciben nonce por uniformidad del grep gate (ver §8); **sin refactor de handlers**.
- `_modal-cobranzas.html` (8 handlers, sin script): **verificado muerto** (0 referencias en `templates/**` y `routes/**`). **Se excluye del refactor de handlers** — desviación de la propuesta (que lo incluía en PR2). No requiere nonce (no tiene scripts).
- Bloques vacíos `lst-rendiciones.html:69` y `planes-opciones.html:61` (`<script>\n</script>`): reciben nonce por uniformidad del gate; no tienen handlers.

---

## 2. Patrón de wiring — ejemplo canónico

Dentro del mismo bloque inline que PR1 noncea (al final del body → los elementos del DOM ya existen; ADR-2/ADR-3):

```html
<script nonce="{{ g.nonce }}">
    // ... código existente del bloque (funciones, init) ...

    // Wiring de handlers (agregado en el refactor)
    document.getElementById('btnExportar').addEventListener('click', function () {
        exportarExcel();          // función global del mismo bloque (hoisting)
    });
    document.getElementById('btnAbrirPagos').addEventListener('click', function () {
        window.abrirModalPagos(); // export de módulo deferred (referencia perezosa)
    });
    document.addEventListener('focusin', function (e) {
        if (e.target.classList && e.target.classList.contains('select-on-focus')) {
            e.target.select();
        }
    });
</script>
```

Reglas:
- **Nunca** `$()` en parse-time (ADR-2). **Nunca** `addEventListener('x', window.fn)` directo si `fn` viene de módulo (ADR-3).
- Eliminar el atributo `on[a-z]+=` del HTML y dejar el elemento identificable por `id` o `class` (agregar `id`/`class` si hace falta; los elementos de filas dinámicas usan delegación + `data-*`).
- No remover exports `window.*` existentes (load-bearing).

---

## 3. Alcance por archivo — inventario exacto

### 3.1 Nonce (PR1): 54 scripts · 47 archivos

Inventario completo en `exploration.md:27-125` (tablas por módulo con línea exacta de cada script). Los 47 archivos:

- **ventas (13)**: `nueva_venta.html` (230, 254, 283), `nueva_ncredito.html` (299), `nuevo_remito.html` (326), `nuevo_presupuesto.html` (338), `presupuestos.html` (527), `remitos.html` (390), `ventas.html` (339), `ventas-articulos.html` (318), `ventas-clientes.html` (371), `ventas-tipo-pagos.html` (398), `ventas-vendedores.html` (451), `iva-ventas.html` (302), `factura-print.html` (41, **variante module**).
- **proveedores (6)**: `nuevo_gasto.html` (229), `nueva_op.html` (108), `compras.html` (230), `iva-compras.html` (299), `ordenes_pago.html` (204), `remitos.html` (256).
- **fondos (3)**: `flujo-fondos.html` (62, 101, 141, 187), `rend-cajas.html` (146), `lst-rendiciones.html` (69, bloque vacío).
- **creditos (4)**: `otorgamiento.html` (566), `seleccion-cuotas-pago.html` (376), `ver-credito.html` (752), `simulador-creditos.html` (92).
- **articulos (6)**: `precios-articulos.html` (116), `stock-articulos.html` (121), `stock-articulos-faltantes.html` (122), `stock-sucursales.html` (101), `rubros-marcas.html` (14), `upd-articulos.html` (568, condicional).
- **configuracion (7)**: `abm-sucursales.html` (30), `puntos-venta.html` (38), `configuraciones.html` (336), `planes-opciones.html` (61, bloque vacío), `partials/_configuracion.html` (172), `partials/_lst-puntos-ventas.html` (103), `partials/_modal_config_editar.html` (27).
- **partials (3)**: `_modal-transacciones.html` (764, **se reemplaza** — ADR-6), `_modal-transacciones-migracion.html` (44, 163 — referencia), `_modal-transacciones-ejemplos.html` (108 — referencia).
- **resto (5)**: `entidades/fin-ent-cred.html` (157, 179), `ctactecli/partials/_ctacte-cli.html` (127), `ctacteprov/lst-ctacteprov.html` (51), `reportes/reporte-gerencial.html` (597), `sessions/login.html` (126).

### 3.2 Handlers (PR2-PR7): 143 handlers · 32 archivos

Conteo real verificado (grep `\son[a-z]+\s*=` sobre `templates/**/*.html`, excluyendo falsos positivos tipo `aria-controls`):

| Módulo | Archivo | Handlers | PR |
|---|---|---|---|
| partials | `_modal-transacciones.html` | 21 (5 onclick + 16 onfocus) | PR2 |
| ventas | `presupuestos.html` | 15 | PR3 |
| ventas | `remitos.html` | 13 | PR3 |
| ventas | `ventas-vendedores.html` | 9 | PR3 |
| ventas | `ventas-tipo-pagos.html` | 9 | PR3 |
| ventas | `ventas-clientes.html` | 8 | PR3 |
| ventas | `ventas-articulos.html` | 6 | PR3 |
| ventas | `ventas.html` | 5 | PR3 |
| ventas | `iva-ventas.html` | 3 | PR3 |
| ventas | `nueva_ncredito.html` | 2 | PR3 |
| proveedores | `compras.html` | 4 | PR4 |
| proveedores | `ordenes_pago.html` | 4 | PR4 |
| proveedores | `remitos.html` | 4 | PR4 |
| proveedores | `iva-compras.html` | 3 | PR4 |
| proveedores | `nueva_op.html` | 1 | PR4 |
| proveedores | `nuevo_gasto.html` | 1 | PR4 |
| proveedores | `nueva_compra.html` | 1 | PR4 |
| creditos | `seleccion-cuotas-pago.html` | 5 | PR5 |
| creditos | `ver-credito.html` | 2 | PR5 |
| creditos | `otorgamiento.html` | 1 | PR5 |
| fondos | `rend-cajas.html` | 1 | PR5 |
| articulos | `upd-articulos.html` | 2 | PR6 |
| articulos | `articulos.html` | 1 (render-string) | PR6 |
| ctactecli | `partials/_ctacte-cli.html` | 1 | PR6 |
| configuracion | `partials/_permisos_tarea.html` | 2 (HTMX) | PR7 |
| configuracion | `partials/_lst-puntos-ventas.html` | 1 | PR7 |
| configuracion | `partials/_modal-lineas-comprobantes.html` | 1 (fetch) | PR7 |
| entidades | `fin-ent-cred.html` | 6 | PR7 |
| entidades | `partials/_lst-entidades.html` | 1 | PR7 |
| clientes | `partials/_lst-clientes.html` | 1 | PR7 |
| reportes | `reporte-gerencial.html` | 1 | PR7 |
| creditos | `partials/_modal-cobranzas.html` | 8 — **MUERTO, excluido** | — |

**Caso especial de wiring por tipo de archivo** (ADR-4/ADR-5):

| Archivo | Cómo se renderiza | Dónde va el wiring |
|---|---|---|
| `_permisos_tarea.html` (2) | HTMX (`permisos-menu.html:30`) | Delegación en `permisos-menu.html` (script nonceado del host; `window.seleccionarTodos`/`window.deseleccionarTodos` ya son globales en `permisos-menu.js:19,29`) |
| `_modal-lineas-comprobantes.html` (1) | fetch + innerHTML | Delegación en `_lst-puntos-ventas.html` (script nonceado; `guardarLineasComprobantes` definida en `_lst-puntos-ventas.html:125`) |
| `_lst-clientes.html` (1), `_lst-entidades.html` (1) | `{% include %}` server-side | Bloque nonceado mínimo al final del partial (mismo nonce del documento) |
| `nueva_compra.html` (1) | Página normal | Bloque nonceado mínimo al final del body (o reutilizar el bloque del modal incluido) |
| `articulos.html` (1) | Página normal | Script existente `articulos.html:125` (ya nonceado) — delegación tbody (ADR-7) |
| `_modal-transacciones.html` (21) | `{% include %}` en 5 pantallas | Bloque mínimo vanilla dentro del partial (ADR-6) |

---

## 4. Límites de slices — definición exacta por PR

Cadena `feature-branch-chain` (tracker `feat/csp-nonce-templates` en draft; PR#1 → tracker; hijos → rama del PR inmediato anterior). Cada PR < 400 líneas.

### PR1 — Nonce (fundación)
- **Contenido**: `nonce="{{ g.nonce }}"` en los 54 scripts (47 archivos) de §3.1. Variante `type="module"` en `factura-print.html:41`. Incluye bloques vacíos y archivos de referencia (uniformidad del gate).
- **Archivos**: 47 · **Líneas**: ~54-108.
- **NO toca handlers** (siguen bloqueados; el PR es la base mecánica).

### PR2 — Transversal: modal de pagos (blast radius)
- **Contenido**: refactor handlers + reemplazo del script inline de `partials/_modal-transacciones.html` (ADR-6): 5 onclick → addEventListener vanilla (referencia perezosa a exports del módulo universal), 16 onfocus → clase `select-on-focus` + listener `focusin` delegado; script `L764-833` → bloque mínimo.
- **Archivos**: 1 · **Líneas**: ~40-60.
- **Nota**: `_modal-cobranzas.html` queda FUERA (muerto, ADR-8) — desviación de la propuesta, documentada.

### PR3 — ventas (core comercial)
- **Contenido**: handlers de 9 archivos ventas (§3.2): onclick de listados → `exportarExcel()`, `imprimirTabla()`, `limpiarFiltros()`, selección masiva, cambio de estado; `nueva_ncredito.html` → `grabarNotaCredito()`. Los 30 `onfocus="this.select()"` que viven en estos archivos → patrón `.select-on-focus`.
- **Archivos**: 9 · **Líneas**: ~70-120.

### PR4 — proveedores
- **Contenido**: handlers de 7 archivos proveedores: export/print de listados, `abrirModalPagos()` en `nueva_op.html`, `nuevo_gasto.html`, `nueva_compra.html` (referencia perezosa a `window.abrirModalPagos` — módulos).
- **Archivos**: 7 · **Líneas**: ~50-90.

### PR5 — fondos + creditos
- **Contenido**: `rend-cajas.html` (guard de submit/validación), `otorgamiento.html` (wizard), `seleccion-cuotas-pago.html` (cobranza: `cobrarCuotas()`, `procesarTransaccion()`), `ver-credito.html` (blur cliente, `cargarCuotas()`).
- **Archivos**: 4 · **Líneas**: ~30-60.

### PR6 — articulos + ctacte
- **Contenido**: `articulos.html` (delegación tbody — ADR-7), `upd-articulos.html` (2), `_ctacte-cli.html` (auto-cálculo recibo).
- **Archivos**: 3 · **Líneas**: ~15-30.

### PR7 — resto (configuracion, entidades, clientes, reportes)
- **Contenido**: `_permisos_tarea` (delegación host — ADR-4), `_modal-lineas-comprobantes` (delegación host), `_lst-clientes`, `_lst-entidades`, `fin-ent-cred.html` (6), `reporte-gerencial.html`, `_lst-puntos-ventas.html`.
- **Archivos**: 7 · **Líneas**: ~30-60.

---

## 5. Verificación por slice

Sin runner de tests (config.yaml `testing` vacío; `build_command: python index.py`). Verificación **manual en navegador** + **grep gates**.

### 5.1 Gates globales (aplican a cada PR, sobre `templates/`)

1. **Cero `<script>` inline sin nonce ni src**:
   ```powershell
   Select-String -Path templates\**\*.html -Pattern '^\s*<script(?![^>]*(nonce=|src=))'
   ```
   → 0 resultados. (Excluir del gate únicamente los archivos muertos de referencia si se decide no noncearlos; este diseño los noncea → gate limpio global.)
2. **Cero atributos handler en archivos renderizados**:
   ```powershell
   Select-String -Path templates\**\*.html -Pattern '\son[a-z]+\s*='
   ```
   → 0 resultados en todos los archivos excepto los 3 muertos no renderizados (`_modal-transacciones-migracion.html`, `_modal-transacciones-ejemplos.html`, `_modal-cobranzas.html`). El gate final del PR7 debe listar explícitamente esas excepciones.
3. **Consola sin errores CSP**: cargar cada pantalla tocada por el PR y verificar ausencia de `Refused to execute inline script` / `Refused to execute inline event handler` / `$ is not defined`.

### 5.2 Checklist manual por PR

| PR | Pantallas a cargar y verificar |
|---|---|
| PR1 | Todas las pantallas de §3.1: charts de `flujo-fondos` (4) y `reporte-gerencial` (4) renderizan; DataTables de `stock-articulos`, `precios-articulos`, `stock-articulos-faltantes`, `stock-sucursales`, `rubros-marcas`, `abm-sucursales`, `puntos-venta` cargan filas; impresión de `factura-print` abre la UI; login muestra el logo; wizard de `otorgamiento` avanza; `ver-credito` carga cuotas; `seleccion-cuotas-pago` abre. |
| PR2 | Modal de pagos en las **5 pantallas**: `nueva_venta`, `nueva_compra`, `nueva_op`, `nuevo_gasto`, `seleccion-cuotas-pago`. Verificar: apertura, tabs (efectivo/tarjetas/ctacte/credito/bonif/vales/cheques/valores), `buscarVale`, `generarCheque`/`limpiarCheque`, `agregarValor`/`limpiarValores`, atajos Alt+E/T/C/R/B/Q/V (vía módulo), foco+select al entrar a cada input. |
| PR3 | `presupuestos`, `remitos`, `ventas`, `ventas-articulos`, `ventas-clientes`, `ventas-tipo-pagos`, `ventas-vendedores`, `iva-ventas`: exportar Excel, imprimir, limpiar filtros, selección masiva, cambiar estado; `nueva_ncredito`: guardar NC (`grabarNotaCredito`). |
| PR4 | `compras`, `ordenes_pago`, `remitos`, `iva-compras`: export/print; `nueva_op`, `nuevo_gasto`, `nueva_compra`: abrir modal de pagos y procesar transacción. |
| PR5 | `rend-cajas`: cálculo dinámico de totales + guard de submit; `otorgamiento`: wizard completo; `seleccion-cuotas-pago`: cobrar cuotas; `ver-credito`: blur cliente + cargar cuotas. |
| PR6 | `articulos`: eliminar artículo desde la fila de la tabla (delegación); `upd-articulos`: editar colores/detalles; recibo en `ctacte-cli`: auto-cálculo efectivo/tarjeta + validación total. |
| PR7 | `configuraciones` (logo, sliders, cierre modal htmx), `permisos-menu` (seleccionar/deseleccionar todos tras el hx-get), `puntos-venta` (abrir y guardar líneas de comprobantes tras el fetch), `entidades-cred` (alta de alícuotas), `clientes`/`entidades` (confirmar eliminación), `reporte-gerencial` (4 charts). |

---

## 6. Riesgos y mitigaciones

| Riesgo | Prob. | Mitigación |
|---|---|---|
| Botón muerto por selector que no matchea | Med | Checklist manual por pantalla (tabla §5.2) + gate 2 (cero `on[a-z]+=`) |
| Listeners duplicados (partials en 5 pantallas, módulo + inline) | Bajo | ADR-6 (script inline mínimo, sin duplicar atajos del módulo); `focusin` delegado único por página |
| Wiring antes del DOM | Bajo | Scripts al final del body (patrón actual); `focusin`/delegación no dependen del orden |
| `$ is not defined` en scripts que usan jQuery en parse-time | Bajo | ADR-2: wiring solo vanilla; los bloques que ya usan `$` (DataTables) conservan sus guards/DOMContentLoaded existentes |
| Regresión de atajos del modal | Bajo | Verificación explícita en PR2 checklist (Alt+E/T/C/R/B/Q/V + F9 vía módulo universal) |

---

## 7. Decisiones abiertas para apply

1. **`_modal-cobranzas.html` (8 handlers)**: este diseño lo excluye (verificado muerto). Si apply encuentra cualquier referencia dinámica (p.ej. render desde una ruta no detectada por grep estático), debe incluirlo en PR5. Confirmar en apply con `Select-String -Path routes\*.py, templates\**\*.html -Pattern '_modal-cobranzas'`.
2. **`_modal-transacciones.html:764-833`**: se reemplaza por bloque mínimo (ADR-6). Si el verify de PR2 detectara algún comportamiento del script inline que el módulo universal NO cubre (p.ej. foco específico en `#efectivo` vs. primer input), apply debe replicar ese comportamiento en el bloque mínimo vanilla (no restaurar `$`).
3. **`onfocus="this.select()"`**: patrón clase `.select-on-focus` + listener `focusin` (ADR-5). Alternativa: listener `focus` individual por input. Se elige delegación por simplicidad y cobertura de contenido dinámico.
4. **Bloques vacíos** (`lst-rendiciones:69`, `planes-opciones:61`): se noncean (uniformidad del gate). Alternativa: eliminarlos. Se elige nonce por menor diff y gate global limpio.
5. **`_lst-clientes` / `_lst-entidades`**: bloque nonceado mínimo dentro del partial (mismo nonce por `{% include %}`). Alternativa: delegación desde el host (`clientes.html`, `entidades-cred.html`). Se elige bloque en el partial (autocontenido, no depende del host).

---

## 8. Criterios de éxito (de la propuesta, con método)

- [ ] Consola sin `Refused to execute inline script / inline event handler` en: `nueva_venta`, `presupuestos`, `flujo-fondos`, `stock-articulos`, `rend-cajas`, `seleccion-cuotas-pago`, `nueva_compra`, `nueva_op`, `nuevo_gasto` (checklist §5.2).
- [ ] Gate 1 (cero `<script>` sin nonce/src) y Gate 2 (cero `on[a-z]+=` en renderizados) en 0 resultados al final de la cadena.
- [ ] Modal de pagos abre en las 5 pantallas; export/print/charts/DataTables operativos (§5.2 por PR).