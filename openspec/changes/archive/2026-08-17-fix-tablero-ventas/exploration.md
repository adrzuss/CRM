# Exploración: fix-tablero-ventas

> Fase: sdd-explore · Modo artefacto: openspec · Proyecto: crm
> Fecha: 2026-08-17 · Solo investigación, sin modificación de código.

## Problema reportado

En `templates/tablero.html` (tablero gerencial/inicial), las tarjetas de gráficos no muestran datos:

1. "Ventas de los últimos 6 meses" — barras, canvas `barrasEventos`, JS vars `mesess`/`eventoss`.
2. "Ingresos de hoy" — doughnut, canvas `myPieChart`, JS vars `tipoPagos`/`cantPagos`.
3. "Ventas por rubros de los últimos 6 meses" — dos pies, canvases `myPieChart2`/`myPieChart3`, JS vars `nombresRubros`/`ventasRubros`/`cantidadRubros`.

## Estado actual (cadena de datos verificada)

### Ruta → Template → JS: NO hay mismatch de nombres

Todos los nombres coinciden exactamente (auditoría línea por línea):

| Ruta (routes/tableros.py:48-53) | Template asigna (tablero.html) | JS consume | ¿Coincide? |
|---|---|---|---|
| `meses` | `mesess = {{ meses\|tojson }}` (L168) | `mesess` (chart-bar-demo.js:37,43) | ✅ |
| `operaciones` | `eventoss = {{ operaciones\|tojson }}` (L169) | `eventoss` (chart-bar-demo.js:38,49) | ✅ |
| `tipoPagoss` | `tipoPagos = {{ tipoPagoss\|tojson }}` (L204) | `tipoPagos` (chart-pie-demo.js:7,43) | ✅ |
| `cantPagoss` | `cantPagos = {{ cantPagoss\|tojson }}` (L205) | `cantPagos` (chart-pie-demo.js:8,45) | ✅ |
| `rubros` | `nombresRubros = {{ rubros\|tojson }}` (L250, L264) | `nombresRubros` (chart-pie-demo.js:14,73,103) | ✅ |
| `vtaRubros` | `ventasRubros = {{ vtaRubros\|tojson }}` (L251) | `ventasRubros` (chart-pie-demo.js:15,75) | ✅ |
| `cantRubros` | `cantidadRubros = {{ cantRubros\|tojson }}` (L265) | `cantidadRubros` (chart-pie-demo.js:16,105) | ✅ |

Las rutas que renderizan `tablero.html`:
- `tablero_inicial` (routes/tableros.py:16-53) — pasa TODAS las variables de gráficos.
- `tablero_administrativo` (routes/tableros.py:89-106) — pasa las mismas vars de gráficos (meses/operaciones/tipoPagoss/cantPagoss) pero **no** rubros/ventasSucursales/ventasVendedores/datos_creditos, y pasa `saldo_clientes` (tupla) en lugar de `saldo_clientes_actual`/`saldo_clientes_vencido` → mismatch solo en esta ruta (pre-existente).

### Servicios de datos: formas correctas

- `ventas_por_mes()` (services/ventas/reportes.py:241-272) → `{'meses': [...], 'operaciones': [...]}` con try/except que devuelve listas vacías.
- `pagos_hoy()` (reportes.py:293-324) → `{'tipo_pago': [...], 'total_pago': [...]}` con try/except.
- `get_vta_rubros(desde, hasta)` (reportes.py:275-290) → `{'rubros': [...], 'vtaRubros': [...], 'cantRubros': [...]}` **SIN try/except** — si el stored procedure `venta_rubros` falla, la página entera da 500.
- Los SP (`get_vta_desde_hasta`, `venta_rubros`, `get_vta_sucursales`) no están versionados en el repo (carpeta `SQL/` gitignored); no se puede verificar su existencia desde el código, pero la página renderiza → existen en la BD.
- Flask 3.0.3 serializa `Decimal` con `|tojson` sin error (verificado empíricamente) → no hay 500 por tojson.

## Causa raíz (regresión del commit HEAD 219aac2)

El commit `219aac2` ("se actualizaron varias funciones generales y se quitaron varios errores menores", 2026-07-29) agregó:

1. **CSP con nonce**: `index.py:127-138` → `script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net https://unpkg.com;`
2. **`g.nonce`** en `before_request` (`index.py:66`).
3. **Nonce en los scripts inline de `base.html`** (base.html:35 y base.html:132).

Pero **`templates/tablero.html` NO fue actualizado**: sus 4 bloques inline `<script>` (L167-170, L203-206, L249-252, L263-266) que asignan `mesess`, `eventoss`, `tipoPagos`, `cantPagos`, `nombresRubros`, `ventasRubros`, `cantidadRubros` **no llevan `nonce="{{ g.nonce }}"`**.

**Efecto**: el navegador BLOQUEA esos scripts inline (CSP sin `unsafe-inline` en script-src + nonce presente ⇒ todo inline sin nonce es bloqueado). Las variables de datos quedan `undefined`. Los scripts externos (chart-bar-demo.js, chart-pie-demo.js) sí se cargan (permitidos por `'self'`), crean los gráficos con `labels: undefined` / `data: undefined` → **gráficos vacíos**. Chart.js 2.x tolera `data: undefined` (`dataset.data || []`) → renderiza vacío, sin excepción visible. Además, `window.onload` de chart-pie-demo.js:34 hace `tipoPagos.length` → TypeError silencioso en consola.

Evidencia adicional: `git log -S "nonce"` → solo `219aac2` tocó templates con nonce; `templates/tablero.html` no se tocó en ese commit (última modificación: `8c89cef`). La misma regresión afecta a cualquier template con scripts inline sin nonce; tablero.html es el caso visible.

## Fallas secundarias (latentes, pre-existentes)

1. **`chart-bar-demo.js:122-126`**: `document.getElementById("barrasRubros")` → canvas inexistente en tablero.html (los rubros ahora son pies `myPieChart2/3`) → `new Chart(null, ...)` lanza "Failed to create chart: can't acquire context from the given item". No rompe el gráfico 1 (ya creado en L40) ni los scripts posteriores (script tags independientes), pero ensucia la consola. Presente desde `6616a3f`.
2. **`tablero.html:291,307,322,335`**: loops sobre `proximosEventos`, `proximasCitas`, `proximasCuotas`, `cuotasVencidas` — **ninguna ruta los pasa** (desde el commit inicial `e6e7d2b`). En Jinja 3.1.4 iterar sobre undefined renderiza vacío (verificado: no lanza) → las 4 tarjetas salen vacías silenciosamente.
3. **`routes/tableros.py:106` (`tablero_administrativo`)**: pasa `saldo_clientes` (tupla de 2) y omite `saldo_clientes_actual`/`saldo_clientes_vencido`, `rubros`/`vtaRubros`/`cantRubros`, `ventasSucursales`, `ventasVendedores`, `datos_creditos`, `desde_sucs`/`hasta_sucs`/`desde_vend`/`hasta_vend` → tarjetas/tablas vacías y inputs de fecha sin valor en ese tablero (pre-existente, no es la regresión reportada).
4. **`get_vta_rubros` (reportes.py:275-290) sin try/except** — si el SP falla, 500 en toda la página.

## Superficie de fix determinada (pregunta 5 del encargo)

- (a) Ruta pasa nombres incorrectos → **NO** (nombres correctos en `tablero_inicial`).
- (b) JS espera nombres distintos a los que asigna el template → **NO** (todos coinciden).
- (c) Consultas de datos rotas / vacías → **NO** (formas correctas; SP existen).
- (d) Combinación → **SÍ, pero la causa real es la CSP del commit 219aac2 + nonce faltante en los scripts inline de tablero.html**. Las fallas secundarias (1-4) son endurecimiento.

## Archivos afectados

- `templates/tablero.html` — L167-170, L203-206, L249-252, L263-266: agregar `nonce="{{ g.nonce }}"` a los 4 scripts inline (fix raíz).
- `index.py` — L127-138: origen de la CSP (no tocar; es correcta).
- `static/js/demo/chart-bar-demo.js` — L122-126: bloque muerto `barrasRubros` (limpiar).
- `services/ventas/reportes.py` — L275-290: `get_vta_rubros` sin try/except (endurecer).
- `routes/tableros.py` — L106: contexto incompleto de `tablero_administrativo` (follow-up).
- `templates/tablero.html` — L291-346: vars nunca provistas (`proximosEventos` etc., follow-up).

## Enfoques

1. **Fix mínimo (nonce en tablero.html)** — Agregar `nonce="{{ g.nonce }}"` a los 4 scripts inline.
   - Pros: 1 archivo, ~4 líneas, restaura los 3 gráficos, cero riesgo.
   - Contras: no toca fallas latentes.
   - Esfuerzo: Bajo.

2. **Fix completo del dashboard (recomendado)** — Opción 1 + limpiar el bloque muerto `barrasRubros` en chart-bar-demo.js + try/except en `get_vta_rubros`.
   - Pros: restaura gráficos y elimina excepción de consola y riesgo de 500; tamaño de cambio pequeño (~15 líneas, dentro del presupuesto de 400).
   - Contras: toca 3 archivos (sigue siendo trivial).
   - Esfuerzo: Bajo-Medio.

3. **Arquitectónico** — Mover la asignación de datos a un archivo JS externo o a un único bloque inline con nonce, o exponer los datos vía endpoint JSON + fetch.
   - Pros: elimina la fragilidad CSP-inline de raíz para este template.
   - Contras: cambio mayor, más superficie de prueba manual, no necesario para un bug fix.
   - Esfuerzo: Medio-Alto.

## Recomendación

**Opción 2** como alcance del cambio `fix-tablero-ventas`: nonce en los 4 scripts inline de `tablero.html` (causa raíz) + limpieza de `barrasRubros` + try/except en `get_vta_rubros`. Dejar los items 2 y 3 de fallas secundarias (vars nunca provistas y contexto de `tablero_administrativo`) como follow-ups separados: son gaps de features pre-existentes, no la regresión reportada.

## Riesgos

- No hay runner de tests (config.yaml: testing vacío); verificación manual: cargar `/tablero-inicial` y verificar que los 3 gráficos muestran datos y que la consola no arroja errores de CSP ni "Failed to create chart".
- Si se usa nonce, `g.nonce` siempre existe (seteado en `before_request`, index.py:66) — sin riesgo.
- Los SP `get_vta_desde_hasta` / `venta_rubros` son externos al repo (SQL/ gitignored): si en algún entorno faltan, `ventas_por_mes` ya devuelve vacío (seguro) y `get_vta_rubros` hoy rompería la página (mitigado por el try/except propuesto).

## Listo para propuesta

Sí. El orchestrator debe indicar en la propuesta: fix raíz = nonce CSP en tablero.html (4 scripts inline); limpieza `barrasRubros`; try/except en `get_vta_rubros`. Recomendar follow-up separado para `proximosEventos`/`proximasCitas`/`proximasCuotas`/`cuotasVencidas` y para el contexto de `tablero_administrativo`.