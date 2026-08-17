# Verificación: fix-tablero-ventas

> Fase: sdd-verify · Modo artefacto: openspec · Proyecto: crm
> Fecha: 2026-08-17 · Modo SDD: Standard (sin runner de tests — `config.yaml` testing vacío, strict_tdd false). No TDD.

## Verification Report

**Change**: fix-tablero-ventas
**Version**: N/A (spec sin versión)
**Mode**: Standard

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 12 |
| Tasks complete | 7 |
| Tasks incomplete | 5 (todas de verificación manual en navegador — 4.1 a 4.5) |

### Build & Tests Execution

**Build**: ✅ Passed (checks estáticos ejecutados localmente)

```text
$ python -m py_compile services/ventas/reportes.py   → OK (PY_COMPILE_OK)
$ node --check static/js/demo/chart-bar-demo.js       → OK (NODE_CHECK_OK)
$ node --check static/js/demo/chart-pie-demo.js       → OK (NODE_CHECK_PIE_OK)
$ git show --stat 65df9a2 → 8 archivos: 3 fuente (tablero.html, chart-bar-demo.js, reportes.py) + 5 openspec. Sin cambios fuera de alcance.
```

**Tests**: ➖ 0 ejecutados — no existe runner (`config.yaml` testing vacío). La verificación de escenarios es manual en navegador y NO se puede ejecutar desde este entorno (no hay navegador ni acceso a la BD). No se fabrican resultados.

**Coverage**: ➖ Not available (sin runner).

### Spec Compliance Matrix

Los 7 escenarios quedan `UNTESTED` a nivel runtime por límite del entorno (sin runner + sin navegador contra la BD). Cada uno tiene evidencia estática fuerte (anotada en "Correctness"). Ninguno se marca como verificado.

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| REQ-1 Scripts inline autorizados por la CSP | Gráficos con datos bajo CSP | (sin runner — manual 4.1/4.2) | ❌ UNTESTED — evidencia estática: 4 nonces presentes |
| REQ-1 | Período sin ventas | (sin runner — manual 4.2) | ❌ UNTESTED — evidencia estática: `tojson` tolera listas vacías |
| REQ-2 Degradación del reporte de rubros | Stored procedure de rubros falla | (sin runner — manual 4.3 opcional) | ❌ UNTESTED — evidencia estática: try/except con retorno de listas vacías |
| REQ-2 | Consulta de rubros exitosa | (sin runner — manual 4.1) | ❌ UNTESTED — evidencia estática: cadena nombres ruta→template→JS coincide |
| REQ-3 Sin gráfico sobre canvas inexistente | Carga sin error de consola | (sin runner — manual 4.2) | ❌ UNTESTED — evidencia estática: bloque muerto eliminado, sin referencias colgantes |
| REQ-4 Tableros existentes sin regresión | Tableros administrativo y básico intactos | (sin runner — manual 4.4/4.5) | ❌ UNTESTED — evidencia estática: rutas no tocadas, diff minimal |
| REQ-4 | Tarjetas de métricas sin cambios | (sin runner — manual 4.4) | ❌ UNTESTED — evidencia estática: diff +4/-4 solo en apertura de `<script>` |

Nota: el encargo mencionaba "8 escenarios"; la spec vigente contiene 7 bloques de scenario (2+2+1+2). Se verifica contra el contenido real de `spec.md`.

**Compliance summary**: 0/7 scenarios con test runtime aprobado (pendientes de verificación manual; no hay runner en el proyecto).

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| REQ-1: nonce en los 4 scripts inline | ✅ Implemented | `tablero.html` L167, L203, L249, L263: `<script nonce="{{ g.nonce }}">` — patrón idéntico a `base.html:35` y `base.html:132`. `g.nonce` garantizado por `before_request` (`index.py:66`); header CSP `script-src 'self' 'nonce-{nonce}' ...` (`index.py:130`) autoriza los inline con el mismo valor. Los 4 scripts externos (L577-584) son `'self'`/CDN y no requieren nonce. |
| REQ-2: degradación de `get_vta_rubros` | ✅ Implemented | `reportes.py:275-301`: cuerpo envuelto en `try:`; `except Exception as e:` → `print('Error calculando ventas por rubros:', str(e))` + retorno `{'rubros': [], 'vtaRubros': [], 'cantRubros': []}`. Patrón idéntico a `ventas_por_mes` (L241-272) y `pagos_hoy` (L304-335). Sin `rollback` (solo lectura, coherente con el archivo). La ruta `tablero_inicial` (`routes/tableros.py:44,52`) siempre recibe el dict → sin 500 posible por esta consulta. |
| REQ-3: sin gráfico sobre canvas inexistente | ✅ Implemented | `chart-bar-demo.js` queda en 119 líneas: `number_format`, `coloresBarras`, `myBarChart` intactos. El bloque `barrasRubros` (84 líneas, `var ctx2 = document.getElementById("barrasRubros")` + `myBarChartRubros`) eliminado hasta EOF. Grep repo-wide: cero referencias a `barrasRubros`/`myBarChartRubros` en código (solo menciones en docs openspec). `nombresRubros`/`ventasRubros`/`cantidadRubros` se redeclaran en `chart-pie-demo.js:14-16` → sin vars colgantes. `tablero_gerencial.js` no referencia vars de gráficos (solo fetch de sucursales/vendedores). |
| REQ-4: sin regresión en tableros compartidos | ✅ Implemented | `routes/tableros.py` no se tocó. `tablero-basico` usa `tablero-basico.html` (template distinto, intacto). `tablero-administrativo` renderiza el mismo `tablero.html`: su 500 es pre-existente (contexto incompleto, `routes/tableros.py:106`) y el nonce no puede alterar el render server-side (`g.nonce` se setea para TODA request). Tarjetas de métricas: el diff de `tablero.html` es +4/-4 solo en la línea de apertura de los `<script>`; el markup de tarjetas no cambió. `get_vta_hoy`/`get_vta_semana`/`get_datos_creditos`/saldos no fueron tocados. |

### Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| Nonce por request, mismo `{{ g.nonce }}` en los 4 scripts | ✅ Yes | `index.py:66` + header CSP regenerados por request; patrón `base.html:35,132`. |
| `get_vta_rubros`: degradar silenciosa (print español + listas vacías), sin rollback | ✅ Yes | Réplica exacta de `ventas_por_mes`/`pagos_hoy`. |
| Eliminar bloque muerto completo hasta EOF; conservar `number_format`, `coloresBarras`, `myBarChart` | ✅ Yes | Diff: -84 líneas, solo el bloque `barrasRubros`. |
| `tablero_administrativo` fuera de alcance (500 pre-existente) | ✅ Yes | No se tocó; no empeora (nonce no afecta el render server-side). |
| Contrato `get_vta_rubros` estable: dict con 3 listas (datos o vacías) | ✅ Yes | Consumidores (`routes/tableros.py:52`, template L250-251/264-265) sin cambios. |
| Rollback `git revert 65df9a2` | ➖ N/A | No ejecutado (no requerido; los 3 cambios son independientes). |

### Issues Found

**CRITICAL**: None (sin defectos de implementación detectados por evidencia estática).

**WARNING**:
1. **Verificación runtime pendiente** — Los 7 escenarios de spec y las tareas 4.1-4.5 no tienen test runtime aprobado (no hay runner en el proyecto y este entorno no puede ejecutar navegador contra la BD). Deben completarse de forma manual antes de declarar el cambio plenamente verificado. Instrucciones en "Pendientes manuales" más abajo.

**SUGGESTION**:
1. **Auditoría CSP sistémica** (follow-up): grep confirma 40+ templates con `<script>` inline sin nonce (p.ej. `fondos/flujo-fondos.html:62,101,141,187`, `ctactecli/partials/_ctacte-cli.html:127`, `fondos/rend-cajas.html:146`, `creditos/*.html`). Misma regresión CSP que este fix puede afectarlos.
2. **`tablero_administrativo`** (follow-up): 500 pre-existente por contexto incompleto (`routes/tableros.py:106` — `saldo_clientes` tupla, faltan rubros/sucursales/vendedores/creditos).
3. **Vars nunca provistas en `tablero.html:291-346`** (follow-up): `proximosEventos`/`proximasCitas`/`proximasCuotas`/`cuotasVencidas` → tarjetas vacías silenciosas desde `e6e7d2b`.
4. **Guard defensivo opcional** en `chart-pie-demo.js:34`: `window.onload` accede a `tipoPagos.length` sin chequeo; `Array.isArray(tipoPagos)` evitaría TypeError silencioso si algún inline no corre en el futuro.
5. **Nota menor**: el encargo indicaba "8 escenarios"; la spec tiene 7 (2+2+1+2). Alinear conteo si se quiere.

### Pendientes manuales (tareas 4.1-4.5 — PENDING-MANUAL)

Ejecutar en entorno con navegador + app corriendo contra la BD (venv activo, `python index.py`):

- **4.1** — Navegar a `/tablero-inicial` autenticado. Verificar: barras "Ventas de los últimos 6 meses" con datos, doughnut "Ingresos de hoy" con datos, y los 2 pies "Ventas por rubros" (monto y cant. de productos) con datos. → REQ-1 S1, REQ-2 S2.
- **4.2** — Consola DevTools limpia: sin `Refused to execute inline script because it violates the following Content Security Policy directive`, sin `Failed to create chart: can't acquire context from the given item`, sin `length of null`/`tipoPagos is not defined`. → REQ-1 S2, REQ-3 S1. (Opcional: probar un período sin ventas → gráficos vacíos sin errores.)
- **4.3** (opcional) — Degradación: romper/renombrar el SP `venta_rubros` → recargar `/tablero-inicial` → HTTP 200, pies vacíos, tarjetas y demás gráficos normales, y en consola del servidor el print `Error calculando ventas por rubros:`. → REQ-2 S1.
- **4.4** — Regresión: `/tablero-basico` y `/tablero-gerencial` sin errores nuevos; en `/tablero-inicial` las tarjetas de ventas hoy/semana, créditos, saldos de clientes/proveedores muestran sus valores. → REQ-4 S1/S2.
- **4.5** — `/tablero-administrativo`: confirmar que el 500 (o render incompleto) es idéntico al pre-fix (no empeora; fuera de alcance). → REQ-4 S1.

### Verdict

**PASS WITH WARNINGS** — Implementación correcta y completa según evidencia estática (nonce CSP, código muerto eliminado sin referencias colgantes, degradación de `get_vta_rubros` con patrón del repo, diff sin cambios fuera de alcance, commit único `65df9a2`). El único bloqueante de verificación plena es la confirmación manual en navegador (4.1-4.5), pendiente por límite del entorno.