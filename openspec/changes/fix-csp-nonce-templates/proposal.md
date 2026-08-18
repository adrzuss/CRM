# Propuesta: fix-csp-nonce-templates

## Intención

La CSP estricta agregada en `219aac2` (`index.py:127-138`, `script-src 'self' 'nonce-...'` sin `unsafe-inline`) bloquea 54 `<script>` inline sin nonce y ~143 handlers inline (`onclick=`, `onchange=`, etc.) → regresión silenciosa (charts vacíos, tablas sin init, botones muertos). Restaurar la funcionalidad **sin relajar la política** (decisión de usuario: refactor a `addEventListener`, NO `unsafe-inline`).

## Alcance

### In Scope
- **(a) Nonce**: `nonce="{{ g.nonce }}"` en los 54 scripts inline (47 archivos). `factura-print.html:41` usa `<script type="module" nonce=...>`. Mismo patrón ya validado en tablero.
- **(b) Refactor handlers**: eliminar ~143 atributos `on[a-z]+=` y cablear con `addEventListener`, en PRs encadenados por módulo (feature-branch-chain).

### Out of Scope
- Modificar `index.py` / la política CSP.
- `unsafe-inline`, `unsafe-hashes`.
- Archivos muertos no renderizados (`_modal-transacciones-migracion.html`, `_modal-transacciones-ejemplos.html`): quedan como referencia, sin refactor de handlers.

## Capacidades

- **Nueva — `csp-nonce`**: requisitos de cumplimiento CSP de templates (todo `<script>` inline con nonce; sin atributos de handler inline; funciones globales alcanzables).
- **Modificadas**: None (refactor puro; ninguna spec existente describe handlers inline).

## Enfoque

- **PR1**: nonce a los 54 scripts (fundación; ~54-108 líneas, mecánico, riesgo bajo).
- **Refactor handlers**: quitar `onclick=`/`onchange=`/etc. y cablear con `addEventListener` **dentro del mismo bloque script inline** (que PR1 ya noncea, al final del body → DOM listo).
- **Funciones globales**: conservar los exports `window.*` existentes (ya presentes en `modal-transacciones-universal.js`, `nueva_venta.js`, `nueva_compra.js`, `nueva_nota_credito.js`, `seleccion-cuotas-pagos.js`; las funciones top-level de scripts clásicos ya son globales). **No remover exports** (el patrón `window.procesarTransaccion` es override load-bearing).
- **Tradeoff**: wiring en inline (recomendado) vs en JS de módulo → inline garantiza consistencia en partials compartidos por 5 pantallas con módulos distintos (`_modal-transacciones`), evita mover ~150 definiciones de funciones de listados, y no arriesga load-order; JS de módulo reduce JS inline a largo plazo pero duplica riesgo en partials multi-host. Partials sin bloque propio (`_lst-clientes`, `_permisos_tarea`, etc.) → bloque nonceado mínimo o wiring desde el JS del host (decisión de sdd-design).

## Orden de slices (feature-branch-chain)

| PR | Contenido | Archivos | Líneas est. | Base |
|----|-----------|----------|-------------|------|
| 1 | Nonce 54 scripts | 47 | ~54-108 | tracker |
| 2 | Transversal: `_modal-transacciones` (5 pantallas) + `_modal-cobranzas` | 2 | ~40-60 | PR1 |
| 3 | ventas (15 scripts: NC, remito, presupuesto, listados, factura-print) | 13 | ~70-120 | PR2 |
| 4 | proveedores (gasto, OP, compras, listados) | 7 | ~50-90 | PR3 |
| 5 | fondos + creditos (charts, rendiciones, otorgamiento, ver-credito) | 8 | ~60-100 | PR4 |
| 6 | articulos + ctactecli/ctacteprov (stock, recibos, movimientos) | 8 | ~40-80 | PR5 |
| 7 | resto (configuracion, entidades, reportes, sessions, clientes) | 8 | ~30-60 | PR6 |

**Justificación**: PR2 primero por blast radius (modal de pagos en 5 pantallas); luego core comercial (ventas → proveedores); fondos/creditos (charts y cobranzas); articulos/ctacte (stock y recibos); resto al final. Cada slice < 400 líneas → cumple presupuesto de review (≤60 min/PR). Solo el tracker (draft, no-merge) se integra a main.

## Áreas afectadas

| Área | Impacto | Descripción |
|------|---------|-------------|
| `templates/**` (47+ archivos) | Modificado | Nonce en scripts inline + refactor handlers |
| `static/js/*.js` | Sin cambio (solo lectura) | Exports `window.*` ya existentes se conservan |
| `index.py` | Sin cambio | Política CSP intacta |

## Riesgos

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Botón muerto por selector que no matchea | Med | Checklist manual por pantalla en tasks + grep de `on[a-z]+=` restantes |
| Listeners duplicados (partials incluidos varias veces) | Bajo | Delegación/guards en sdd-design |
| Wiring antes del DOM | Bajo | Scripts al final del body (patrón actual) |

## Rollback

Cada PR = commit revertible independiente; revertir un hijo no afecta la cadena. Ningún PR empeora el estado actual (hoy todo está bloqueado por CSP). Tracker se mergea solo al completar la cadena.

## Dependencias

Ninguna externa. Decisión de usuario: **feature-branch-chain** (tracker `feat/csp-nonce-templates` en draft; PR #1 → tracker; hijos → rama del PR inmediato anterior).

## Criterios de éxito

- [ ] Consola sin "Refused to execute inline script / inline event handler" en pantallas clave (nueva_venta, presupuestos, flujo-fondos, stock-articulos, rend-cajas, seleccion-cuotas-pago, nueva_compra, nueva_op, nuevo_gasto).
- [ ] grep: 0 `<script>` sin nonce/src; 0 atributos `on[a-z]+=` en archivos renderizados.
- [ ] Modal de pagos abre en las 5 pantallas; export/print/charts/DataTables operativos.