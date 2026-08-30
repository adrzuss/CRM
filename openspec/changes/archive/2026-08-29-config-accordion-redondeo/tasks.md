# Tasks: config-accordion-redondeo

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 320–380 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Full implementation | PR 1 | Single PR — DB + model + routes + templates + CSS; under 400 lines |

## Phase 1: Database

- [x] 1.1 Create DDL script `SQL/reglas_redondeo.sql` — `CREATE TABLE reglas_redondeo` with columns: `id` INT PK AUTO_INCREMENT, `nombre` VARCHAR(50) NOT NULL, `desde_precio` DECIMAL(12,2) NOT NULL, `hasta_precio` DECIMAL(12,2) NOT NULL, `multiplo` INT NOT NULL, `tipo_redondeo` ENUM('arriba','abajo','cercano') DEFAULT 'cercano', `restar_unidades` INT DEFAULT 0, `activo` BOOLEAN DEFAULT TRUE
- [x] 1.2 Execute DDL against dev database

## Phase 2: Model

- [x] 2.1 Append `ReglaRedondeo` class to `models/configs.py` — fields: `id`, `nombre`, `desde_precio` (Numeric 12,2), `hasta_precio` (Numeric 12,2), `multiplo` (Integer), `tipo_redondeo` (Enum), `restar_unidades` (Integer), `activo` (Boolean)
- [x] 2.2 Verify model instantiates and commits to test DB

## Phase 3: Routes

- [x] 3.1 Add `from models.configs import ReglaRedondeo` to `routes/configs.py`
- [x] 3.2 Add `render_tabla_reglas_redondeo()` helper — queries all `ReglaRedondeo`, returns `_tabla_reglas_redondeo.html` partial
- [x] 3.3 Add `htmx_add_regla_redondeo` route (POST) — validate `desde < hasta` and `multiplo > 0`, create record, commit, return rendered table partial. Return 400 with error HTML on validation failure
- [x] 3.4 Add `get_regla_redondeo(id)` route (GET) — fetch record, return `_form_edit_regla_redondeo.html` modal partial
- [x] 3.5 Add `update_regla_redondeo(id)` route (POST) — validate same rules, update fields, commit, return table partial
- [x] 3.6 Add `delete_regla_redondeo(id)` route (POST) — delete record, commit, return table partial
- [x] 3.7 Add `reglas_redondeo = ReglaRedondeo.query.all()` to `configuraciones()` query and pass `reglas_redondeo=reglas_redondeo` to template context

## Phase 4: Templates — Accordion

- [x] 4.1 Rewrite `templates/configuracion/configuraciones.html` — replace 12 stacked `div.card.m-3` with `<div class="accordion" id="configAccordion">` wrapper containing 13 `accordion-item` elements
- [x] 4.2 Each `accordion-item`: `accordion-header` with `accordion-button` (icon + title), `accordion-collapse` with `data-bs-parent="#configAccordion"`, `accordion-body` wrapping existing content
- [x] 4.3 Configuración general: `accordion-collapse` gets class `show` so it is expanded by default
- [x] 4.4 Split Tipo IVAs and Tipo Documentos into two separate `accordion-item` elements (currently col-6 inside one card)
- [x] 4.5 Remove outer `div.card.m-3` wrapper from each section — keep inner `div.card` around form/table as-is
- [x] 4.6 Add FontAwesome icons to each accordion button per design icon mapping (fa-cog, fa-percent, fa-building, fa-tags, fa-tasks, fa-book, fa-file-invoice, fa-id-card, fa-users, fa-money-bill-wave, fa-palette, fa-list-ul, fa-ruler-combined)

## Phase 5: Templates — Reglas de Redondeo

- [x] 5.1 Create `templates/configuracion/partials/_tabla_reglas_redondeo.html` — HTMX table partial with columns: nombre, desde, hasta, múltiplo, tipo, restar unidades, activo, acciones (editar/eliminar). Empty state: "Sin resultados"
- [x] 5.2 Create `templates/configuracion/partials/_form_edit_regla_redondeo.html` — Bootstrap modal edit form following `_form_edit_alc_iva.html` pattern. Fields: nombre, desde_precio, hasta_precio, multiplo, tipo_redondeo (dropdown: arriba/abajo/cercano), restar_unidades (checkbox), activo (checkbox)
- [x] 5.3 Add inline add form inside accordion body for Reglas de Redondeo — fields: nombre, desde_precio, hasta_precio, multiplo, tipo_redondeo (dropdown), restar_unidades (checkbox). Button "Agregar" with `hx-post="/htmx/add_regla_redondeo"` targeting `#tabla-reglas_redondeo`
- [x] 5.4 Wire edit button in table: `hx-get="/htmx/get_regla_redondeo/{id}"` targeting modal. Wire delete button: `hx-post="/htmx/delete_regla_redondeo/{id}"` with confirmation

## Phase 6: CSS

- [x] 6.1 Add accordion-specific styles to `static/css/main.css` if needed — override BS5 default accordion borders, ensure `accordion-body` spacing matches existing card-body padding. Minimize: try without custom CSS first, add only if visual QA reveals issues

## Phase 7: Verification

- [ ] 7.1 Load `/configuraciones` — verify 13 accordion items render, Configuración general expanded by default
- [ ] 7.2 Click accordion headers — verify mutual exclusion (only one open at a time)
- [ ] 7.3 Expand Reglas de Redondeo — verify inline form visible, table shows empty state
- [ ] 7.4 Add a regla — verify table updates, form resets
- [ ] 7.5 Edit via modal — verify changes persist
- [ ] 7.6 Delete — verify row removed
- [ ] 7.7 Test validation: desde >= hasta returns error HTML; multiplo <= 0 returns error HTML
- [ ] 7.8 Verify existing HTMX functionality intact in all other accordion sections (Alícuotas IVA, etc.)