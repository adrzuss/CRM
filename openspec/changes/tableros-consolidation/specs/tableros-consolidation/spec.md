# Tableros Consolidation

## Purpose

Unificar los blueprints `tableros.py` y `dashboard_gerencial.py` en un único `bp_tableros`. Refactorización puramente estructural: cero cambios de comportamiento, URLs o lógica de negocio.

---

## Requirements

### R1: Blueprint único registrado

The system SHALL register only `bp_tableros` in `index.py`. The `bp_dashboard_gerencial` import and registration MUST be removed.

#### Scenario: Solo un blueprint de tableros

- GIVEN `index.py` con blueprints registrados
- WHEN la app inicia
- THEN `bp_tableros` está registrado con `url_prefix='/'`
- AND `bp_dashboard_gerencial` NO existe en imports ni en `register_blueprint`

#### Scenario: Rutas dashboard-gerencial accesibles

- GIVEN blueprint consolidado registrado
- WHEN usuario navega a `/dashboard-gerencial`
- THEN responde HTTP 200 con el template del dashboard
- AND todas las API endpoints `/api/dashboard-gerencial/*` responden correctamente

---

### R2: Rutas migradas sin cambio de URL

The system SHALL keep ALL existing route URLs identical. No `/tablero-*`, `/dashboard-gerencial`, `/api/dashboard-gerencial/*`, or `/plan-vencido` URL SHALL change.

#### Scenario: Todas las 26 rutas accesibles

- GIVEN las 5 rutas de `tableros.py` + 21 de `dashboard_gerencial.py`
- WHEN se consolidan en `bp_tableros`
- THEN cada URL existente responde al mismo método (GET) que antes
- AND los parámetros query se procesan igual

#### Scenario: url_for() funciona correctamente

- GIVEN templates que usan `url_for('tableros.dashboard_gerencial')`
- WHEN se resuelve la URL
- THEN devuelve `/dashboard-gerencial`

- GIVEN templates que usan `url_for('tableros.tablero_inicial')`
- WHEN se resuelve la URL
- THEN devuelve `/tablero-inicial`

---

### R3: Template paths actualizados

The system SHALL move templates to `templates/tableros/` and update all `render_template` calls. Old template paths MUST NOT be referenced.

| Template original | Nuevo path |
|-------------------|------------|
| `tablero.html` | `tableros/tablero.html` (or `tableros/gerencial.html`) |
| `tablero-basico.html` | `tableros/tablero-basico.html` |
| `dashboard-gerencial.html` | `tableros/dashboard-gerencial.html` |
| `reportes/reporte-gerencial.html` | `reportes/reporte-gerencial.html` (sin cambio) |
| `plan-vencido.html` | `tableros/plan-vencido.html` |

#### Scenario: Templates se renderizan desde nueva ubicación

- GIVEN blueprint con `template_folder='../templates/tableros'`
- WHEN `tablero_inicial()` hace `render_template('tablero.html', ...)`
- THEN el archivo se resuelve en `templates/tableros/tablero.html`

#### Scenario: reporte-gerencial sin cambio

- GIVEN `tablero_gerencial()` que renderiza `reportes/reporte-gerencial.html`
- WHEN se ejecuta la ruta
- THEN se resuelve correctamente (path absoluto desde templates root)

---

### R4: Helpers migrados

The system SHALL move `_parsear_filtros()` and `_api_respuesta()` from `dashboard_gerencial.py` into `routes/tableros.py`. These are private helpers, not public API.

#### Scenario: Helpers accesibles dentro del mismo módulo

- GIVEN funciones `_parsear_filtros` y `_api_respuesta` en `routes/tableros.py`
- WHEN los 21 endpoints HTMX las invocan
- THEN funcionan igual que antes (mismos parámetros, misma lógica)

---

### R5: Sidebar link actualizado

The system SHALL update the sidebar link for dashboard-gerencial to use `url_for('tableros.dashboard_gerencial')` instead of hardcoded `/dashboard-gerencial`.

#### Scenario: Sidebar link funciona

- GIVEN `_sidebar.html` con link a dashboard-gerencial
- WHEN se renderiza el sidebar
- THEN el href apunta a `/dashboard-gerencial` vía `url_for`
- AND el link funciona correctamente

---

### R6: Servicios sin cambios

The system SHALL NOT modify `services/dashboard_gerencial.py` or any other service file. The service layer has zero overlap with the route consolidation.

#### Scenario: Imports de servicios intactos

- GIVEN `routes/tableros.py` consolidado
- WHEN importa funciones de `services/dashboard_gerencial`
- THEN todos los imports funcionan sin errores

---

### R7: Archivos estáticos compartidos

The system SHALL NOT move any static JS files. The `fondos` module depends on `chart-pie-demo.js` and `chart-bar-demo.js` in `static/js/demo/`.

#### Scenario: Fondos sigue funcionando

- GIVEN módulo fondos que referencia `static/js/demo/chart-pie-demo.js`
- WHEN se carga la página de fondos
- THEN los scripts se cargan correctamente

---

## Migration Rules

| Qué cambia | Qué NO cambia |
|------------|---------------|
| `routes/tableros.py` recibe 21 endpoints + 2 helpers | URLs de todas las rutas |
| `routes/dashboard_gerencial.py` se elimina | Lógica de negocio en servicios |
| Templates se mueven a `templates/tableros/` | Archivos estáticos (JS, CSS, imágenes) |
| `index.py` elimina import/registration de `bp_dashboard_gerencial` | `reportes/reporte-gerencial.html` path |
| `_sidebar.html` usa `url_for` | Parámetros query de cada endpoint |
| `render_template` paths actualizados | Decoradores `@check_session`, `@alertas_mensajes` |

---

## Rollback Criteria

The change MUST be reverted if ANY of the following occurs:

1. Cualquier ruta existente devuelve error 404 o 500
2. `url_for()` con namespace `tableros.*` falla para alguna ruta
3. Templates no se resuelven (Jinja2 `TemplateNotFound`)
4. Fondos module pierde acceso a `chart-pie-demo.js`
5. Sidebar link a dashboard-gerencial deja de funcionar
6. API endpoints HTMX devuelven error de import o función no encontrada

**Rollback method**: `git checkout` de todos los archivos afectados. No hay migraciones de base de datos.

---

## Non-Functional Requirements

| Req | Especificación |
|-----|---------------|
| NF1 | Blueprint `template_folder` apunta a `../templates/tableros` |
| NF2 | Todos los endpoints mantienen `@check_session` y `@alertas_mensajes` donde corresponde |
| NF3 | API endpoints mantienen wrapper `_api_respuesta()` con manejo de errores |
| NF4 | Cero downtime — cambio puramente de código, sin DB migrations |
| NF5 | Líneas totales cambiadas estimadas: ~430 (127 tableros + 309 dashboard_gerencial + index.py + sidebar) |
