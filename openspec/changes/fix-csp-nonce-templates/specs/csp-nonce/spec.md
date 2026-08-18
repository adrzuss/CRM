# Especificación CSP Nonce en Templates

## Propósito

La CSP estricta (`script-src 'self' 'nonce-…'` sin `unsafe-inline`, `index.py:127-138`) bloquea 54 `<script>` inline y ~143 handlers inline en templates. Esta spec define el cumplimiento CSP de templates: todo script inline autorizado por nonce, cero handlers inline (refactor a `addEventListener`), superficie `window.*` preservada y política CSP intacta. Sin test runner → verificación manual por pantalla y por slice de PR (feature-branch-chain, 7 PRs).

## Requirements

### Requirement: Nonce en todo script inline renderizado

El sistema MUST renderizar cada `<script>` inline de plantillas renderizadas (54 bloques · 47 archivos) con `nonce="{{ g.nonce }}"`, incluyendo partials incluidos con `{% include %}` (mismo contexto, `g.nonce` global). El bloque de `factura-print.html:41` MUST usar `<script type="module" nonce="{{ g.nonce }}">`. Archivos no renderizados (`_modal-transacciones-migracion.html`, `_modal-transacciones-ejemplos.html`) y bloques vacíos (`lst-rendiciones.html:69`, `planes-opciones.html:61`) MAY quedar sin nonce.

#### Scenario: Carga de pantalla sin violaciones CSP

- GIVEN un template con script inline nonceado (p.ej. `ventas.html:339`)
- WHEN se carga la pantalla en navegador
- THEN la consola no muestra "Refused to execute inline script"
- AND filtros/export/imprimir del listado operan

#### Scenario: Variante módulo

- GIVEN `factura-print.html:41`
- WHEN se abre la UI de impresión
- THEN `invoice_handler.js` importa y la impresora opera sin error CSP

### Requirement: Refactor de handlers inline a addEventListener

El sistema MUST NOT renderizar atributos `on[a-z]+=` en plantillas renderizadas (~143 handlers · 33 archivos) y MUST cablear cada handler con `addEventListener` dentro del mismo bloque script inline nonceado (al final del body, DOM listo), sin cambiar el comportamiento (botones, modales, atajos de teclado, submit). Archivos de referencia no renderizados quedan excluidos del refactor.

#### Scenario: Botón refactorizado opera igual

- GIVEN `nueva_ncredito.html:279` sin atributo `onclick`
- WHEN se confirma la nota de crédito
- THEN `grabarNotaCredito()` ejecuta y guarda

#### Scenario: Modal de pagos en 5 pantallas

- GIVEN `_modal-transacciones.html` refactorizado
- WHEN se abre el modal desde venta, compra, OP, gasto o cobranza
- THEN `abrirModalPagos()` abre y `generarCheque`, `agregarValor`, `buscarVale` responden

#### Scenario: Atajos de teclado conservados

- GIVEN `_modal-transacciones.html:764` nonceado
- WHEN se presiona Alt+E/T/C/R/B/Q/V con el modal abierto
- THEN se activa el método de pago correspondiente

#### Scenario: Sin listeners duplicados

- GIVEN un partial incluido más de una vez en la página
- WHEN se dispara el evento
- THEN el handler se ejecuta una sola vez

### Requirement: Superficie global window.* preservada

El sistema MUST conservar los exports `window.*` existentes (`window.procesarTransaccion` override, `window.PRESUPUESTO`, `window.REMITO`, `window.BASE_URL`, `window.CSRF_TOKEN`) y las funciones top-level de scripts clásicos deben seguir globales y alcanzables desde el wiring.

#### Scenario: Override load-bearing

- GIVEN `window.procesarTransaccion` definido por el host
- WHEN el modal de pagos procesa una transacción
- THEN se invoca el override del host, no el default

### Requirement: Política CSP intacta

El sistema MUST NOT modificar `index.py` ni relajar `script-src` (queda prohibido `unsafe-inline` y `unsafe-hashes`).

#### Scenario: Header estricto

- GIVEN una respuesta de cualquier pantalla
- WHEN se inspecciona el header `Content-Security-Policy`
- THEN `script-src` contiene `'self' 'nonce-…'` sin `unsafe-inline`

### Requirement: Verificación manual por slice

Cada slice de PR (feature-branch-chain, 7 PRs) MUST verificarse manualmente por pantalla (sin test runner). Los greps de invariante MUST dar 0 resultados: `<script>` inline sin nonce ni `src`, y `on[a-z]+=` en archivos renderizados.

#### Scenario: Slice transversal (PR2)

- GIVEN PR2 aplicado
- WHEN se abre el modal de pagos en las 5 pantallas (venta, compra, OP, gasto, cobranza)
- THEN el modal abre y procesa sin errores de consola

#### Scenario: Slice ventas (PR3)

- GIVEN PR3 aplicado
- WHEN se cargan nueva_venta, nueva_ncredito, nuevo_remito, nuevo_presupuesto, presupuestos, remitos, ventas, ventas-articulos, ventas-clientes, ventas-tipo-pagos, ventas-vendedores, iva-ventas y factura-print
- THEN consola limpia y precargas, listados y UI de impresión operativos

#### Scenario: Slice proveedores (PR4)

- GIVEN PR4 aplicado
- WHEN se cargan nuevo_gasto, nueva_op, compras, iva-compras, ordenes_pago y remitos
- THEN consola limpia; modal de pagos, cheques y export/print operativos

#### Scenario: Slice fondos + creditos (PR5)

- GIVEN PR5 aplicado
- WHEN se cargan flujo-fondos, rend-cajas, otorgamiento, seleccion-cuotas-pago, ver-credito y simulador-creditos
- THEN charts, rendiciones y cobranzas operativos

#### Scenario: Slice articulos + ctacte (PR6)

- GIVEN PR6 aplicado
- WHEN se cargan precios-articulos, stock-articulos, stock-faltantes, stock-sucursales, rubros-marcas, upd-articulos, _ctacte-cli y lst-ctacteprov
- THEN DataTables y recibos operativos

#### Scenario: Slice resto (PR7)

- GIVEN PR7 aplicado
- WHEN se cargan configuracion (abm-sucursales, puntos-venta, configuraciones, partials), entidades (fin-ent-cred), reporte-gerencial y login
- THEN DataTables, logo, sliders y charts operativos

#### Scenario: Grep de invariantes finales

- GIVEN la cadena completa aplicada
- WHEN se grepea `^\s*<script>` sin `nonce` ni `src` y `on[a-z]+=` en templates renderizados
- THEN 0 resultados