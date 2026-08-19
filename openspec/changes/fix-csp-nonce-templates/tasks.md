# Tasks: fix-csp-nonce-templates

## Review Workload Forecast

| Campo | Valor |
|---|---|
| Líneas totales estimadas | ~300–530 (7 PRs) |
| Máximo por slice | ~120 |
| Riesgo 400 líneas por PR | Bajo |
| PRs encadenados | Sí — 7 |
| Estrategia de entrega | ask-on-risk |
| Estrategia de cadena | feature-branch-chain |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: Medium

### Work Units

| PR | Contenido | Base | Líneas est. |
|---|---|---|---|
| 1 | Nonce 54 scripts (47 arch.) | tracker | 54–108 |
| 2 | Modal pagos (21 handlers, ADR-6) | PR1 | 40–60 |
| 3 | ventas (70 handlers) | PR2 | 70–120 |
| 4 | proveedores (18 handlers) | PR3 | 50–90 |
| 5 | fondos+créditos (9 handlers) | PR4 | 30–60 |
| 6 | artículos+ctacte (4 handlers) | PR5 | 15–30 |
| 7 | resto (13 handlers) | PR6 | 30–60 |

## Fase 0: Cadena y ramas

- [x] 0.1 Crear tracker `feat/csp-nonce-templates` desde `d1047ac` (punto del fix CSP; tablero fixes ya commiteados); PR draft no-merge pendiente de push (sin push/PR en este run)
- [ ] 0.2 Rama por slice con base en el PR inmediato anterior (PR2→PR1 … PR7→PR6)

## Fase 1: PR1 — Nonce (fundación)

- [x] 1.1 `nonce="{{ g.nonce }}"` en los 54 `<script>` inline (47 archivos, design §3.1); `factura-print:41` → `type="module" nonce`; incluir vacíos (`lst-rendiciones:69`, `planes-opciones:61`) y referencias (`migracion:44,163`, `ejemplos:108`); sin tocar handlers
- [x] 1.2 Commit `fix(csp): nonce en 54 scripts inline`
- [x] 1.3 Verificar: gate 1 = 0 (design §5.1) + checklist §5.2/PR1 (gate OK; checklist manual de navegador pendiente)

## Fase 2: PR2 — Modal de pagos (transversal)

- [x] 2.1 Reemplazar `_modal-transacciones.html:764-833` por bloque mínimo vanilla (ADR-6): `focusin` delegado `.select-on-focus`; sin duplicar atajos del módulo
- [x] 2.2 5 `onclick` (L461, 580, 583, 682, 685) → `addEventListener` con referencia perezosa a `window.*`
- [x] 2.3 16 `onfocus="this.select()"` → clase `select-on-focus`
- [x] 2.4 Verificar foco `#efectivo` al abrir (decisión abierta #2): cubierto por módulo (primer input no readonly = `#efectivo`) + clase `select-on-focus` restaura el select; sin replicación extra
- [x] 2.5 Commit `fix(csp): handlers modal pagos a addEventListener`
- [x] 2.6 Verificar: gate 2 = 0 + gate 1 = 0 (OK); sin duplicados (OK, revisión estática); checklist manual de navegador PENDIENTE (modal en 5 pantallas + atajos Alt+E/T/C/R/B/Q/V)

## Fase 3: PR3 — Ventas

- [x] 3.1 Refactor handlers en 9 archivos ventas (design §3.2) → `addEventListener` en bloque nonceado; delegación en filas dinámicas (ADR-5). NOTA: 69 handlers reales (design decía 70; el "13°" de remitos era el selector JS `button[onclick="seleccionarTodos()"]` en L638, actualizado a clase); NO hay `onfocus` en los 9 archivos ventas (los 14 onfocus viven en fin-ent-cred/rend-cajas/_modal-cobranzas, PR5/PR7)
- [x] 3.2 Conservar `window.*`; referencias perezosas a funciones de módulos (ADR-3): `btnGrabarNC` → `window.grabarNotaCredito()` (lazy); `buscar_comprobante_original` ya lo wirea `nueva_nota_credito.js:1597` (sin listener duplicado)
- [x] 3.3 Commit `fix(csp): handlers ventas a addEventListener`
- [x] 3.4 Verificar: gate 1 = 0 + gate 2 = 0 en templates/ventas (OK); sin duplicados (OK, revisión estática); checklist manual de navegador PENDIENTE (presupuestos/remitos/ventas/NC + botones de fila dinámicos)

## Fase 4: PR4 — Proveedores

- [x] 4.1 Refactor 18 handlers en 7 archivos proveedores (design §3.2): export/print; `abrirModalPagos()` perezosa (módulos)
- [x] 4.2 Commit `fix(csp): handlers proveedores a addEventListener`
- [ ] 4.3 Verificar §5.2/PR4: export/print; modal abre y procesa en nueva_op, nuevo_gasto, nueva_compra (gates OK; checklist manual de navegador PENDIENTE)

## Fase 5: PR5 — Fondos + créditos

- [x] 5.1 Refactor 9 handlers en 4 archivos (design §3.2) → `addEventListener`: rend-cajas (1 onfocus→`select-on-focus` + focusin delegado; submit/validation guard ya estaba como addEventListener en el script nonceado), otorgamiento (1 `buscarCliente` → id `btn-buscar-cliente`), seleccion-cuotas-pago (5: `abrirModalPagos`×2 perezosa vía `window.*`, `seleccionarTodas`/`seleccionarVencidas`/`limpiarSeleccion` directas — ids nuevos en botones), ver-credito (2: `buscarCliente` condicional con guard, `buscarGarante` delegación `closest()` + `data-indice`)
- [x] 5.2 Confirmar `_modal-cobranzas.html` sin referencias: grep `_modal-cobranzas` en `routes/**` + `templates/**` = 0 resultados → excluido (ADR-8, decisión #1 confirmada)
- [x] 5.3 Commit `fix(csp): handlers fondos y creditos`
- [ ] 5.4 Verificar §5.2/PR5: gates OK (gate 1 = 0 recursivo, gate 2 = 0 en los 4 archivos); checklist manual de navegador PENDIENTE (rend-cajas submit/validación, otorgamiento wizard, seleccion-cuotas-pago cobrar cuotas, ver-credito cargar cuotas + blur cliente)

## Fase 6: PR6 — Artículos + ctacte

- [x] 6.1 `articulos.html:175`: render-string sin `onclick` (clase + data-id) + delegación tbody en script existente (ADR-7)
- [x] 6.2 Refactor `upd-articulos` (2, condicional Jinja) y `_ctacte-cli` (1) → `addEventListener`
- [x] 6.3 Commit `fix(csp): handlers articulos y ctacte`
- [ ] 6.4 Verificar §5.2/PR6 (gates OK; checklist manual de navegador PENDIENTE)

## Fase 7: PR7 — Resto

- [x] 7.1 `_permisos_tarea` (2, HTMX) y `_modal-lineas-comprobantes` (1, fetch) → delegación desde host (ADR-4): host `permisos-menu.html` (bloque nonceado nuevo + `window.seleccionarTodos`/`deseleccionarTodos` perezosas, `data-accion` en los 2 botones) y host `_lst-puntos-ventas.html` (listener delegado `.btn-guardar-lineas` → `guardarLineasComprobantes`)
- [x] 7.2 Refactor `fin-ent-cred` (6 onfocus→`select-on-focus` + focusin delegado; 3 estáticos + 3 en render-string), `_lst-clientes` (1 confirm→delegación `btn-eliminar-cliente`), `_lst-entidades` (1 confirm→delegación `btn-eliminar-entidad`), `reporte-gerencial` (1 `window.print`→`btnImprimir`), `_lst-puntos-ventas` (1 `abrirModalLineas`→delegación `.btn-lineas-ticket` + data-*) — partials con bloque mínimo nonceado (ADR-5)
- [x] 7.3 Commit `fix(csp): handlers resto a addEventListener`
- [x] 7.4 Verificar §5.2/PR7 (gates OK: gate 1 = 0 recursivo, gate 2 = 0 en los 7 archivos; full-tree solo restan los 2 archivos muertos; checklist manual de navegador PENDIENTE)

## Fase 8: Gates finales e integración

- [ ] 8.1 Gate 1 = 0; gate 2 = 0 en renderizados (excepciones: `_modal-transacciones-migracion`, `_modal-transacciones-ejemplos`, `_modal-cobranzas`)
- [ ] 8.2 Verificación integrada: consola limpia en 9 pantallas clave (proposal); modal en 5; export/print/charts/DataTables OK
- [ ] 8.3 Revisar diffs por PR (sin líneas de otros slices); mergear cadena al tracker; tracker → main