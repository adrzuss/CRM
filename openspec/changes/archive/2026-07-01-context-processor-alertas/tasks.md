# Tasks: Context Processor para Alertas y Mensajes

## Task 1: Agregar context_processor en index.py

- [x] Agregado `inject_alertas()` con `@app.context_processor` en index.py (líneas 95-103)

- [x] **File**: index.py
- **Action**: Agregar función `inject_alertas()` con `@app.context_processor` que retorne `dict(alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)`
- **Where**: Dentro de `create_app()`, antes del `return app`
- **Verification**: `python index.py` arranca sin errores

## Task 2: Eliminar variables repetidas de routes/

- [x] Eliminadas 6 ocurrencias del bloque de 4 vars en 5 archivos: configs.py (1), articulos.py (1), fondos.py (1), ofertas.py (2), tableros.py (1)
- [x] 9 archivos ya no tenían las 4 variables juntas: clientes.py, creditos.py, bancos.py, ctacteprov.py, entidades_cred.py, ctactecli.py, proveedores.py, ventas.py, sessions.py

- [x] **Files**: routes/clientes.py, routes/creditos.py, routes/bancos.py, routes/configs.py, routes/ctacteprov.py, routes/entidades_cred.py, routes/articulos.py, routes/fondos.py, routes/ctactecli.py, routes/ofertas.py, routes/proveedores.py, routes/ventas.py, routes/tableros.py, routes/sessions.py (+ routes/reportes.py)
- **Action**: En cada archivo, eliminar TODAS las ocurrencias de `, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes` dentro de llamadas a `render_template()`
- **Pattern**: `, alertas=g\.alertas, cantidadAlertas=g\.cantidadAlertas, mensajes=g\.mensajes, cantidadMensajes=g\.cantidadMensajes`
- **Edge case**: Algunas líneas tienen `alertas=g.alertas` pero sin las otras 3 variables (tableros.py línea 88, fondos.py línea 126, ofertas.py líneas 120 y 244, configs.py línea 700, articulos.py línea 778). Esas NO se tocan — solo eliminar el bloque completo de 4.
- **Edge case**: Tableros.py línea 110 tiene `alertas=g.alertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes` (sin cantidadAlertas). Dejar igual.
- **Verification**: `rg 'alertas=g\.alertas' routes/` solo debe mostrar ocurrencias fuera de render_template() o los edge cases documentados

## Verification

- `python index.py` arranca sin errores
- `pytest tests/ -v` — todos los tests pasan
- Las aplicaciones web siguen funcionando (las variables se inyectan via context processor)
