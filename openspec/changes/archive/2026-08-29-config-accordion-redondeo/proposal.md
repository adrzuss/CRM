# Proposal: Config Accordion + Reglas de Redondeo

## Intent

The configuraciones page has 12 stacked `div.card.m-3` sections (357 lines) creating visual clutter and poor scroll UX. Additionally, there's no way to configure rounding rules for prices — a business need for controlling how amounts are rounded in invoices and reports.

## Scope

### In Scope
- Wrap all 12 existing sections in a Bootstrap 5.3.3 accordion (`#configAccordion`)
- Split Tipo IVAs / Tipo Documentos from side-by-side into two separate accordion items (total: 13 items)
- Configuración general expanded by default (`show` class)
- Icons on accordion buttons for visual hierarchy
- Flatten inner nested cards into subtle bordered sections
- New `ReglaRedondeo` model (full DB table)
- New CRUD: HTMX add form, table partial, modal edit form, delete
- Routes: `htmx_add_regla_redondeo`, `htmx_get_regla_redondeo`, `htmx_update_regla_redondeo`, `htmx_delete_regla_redondeo`

### Out of Scope
- Applying rounding rules to invoice calculation logic (separate change)
- Migrating existing sections to HTMX-only patterns
- Changing the stored procedure or business logic layer

## Capabilities

### New Capabilities
- `reglas-redondeo`: CRUD for rounding rule configuration — price range → multiple/ direction mapping

### Modified Capabilities
None

## Approach

**Accordion**: Replace the 12 `div.card.m-3` wrappers with `<div class="accordion" id="configAccordion">` containing `accordion-item` elements. Each section's `<h4>` becomes an `accordion-button` inside `accordion-header`. The existing `card-body` content becomes `accordion-collapse` → `accordion-body`. HTMX `hx-target` / `hx-swap` attributes are unchanged — they target elements inside the accordion body, not the accordion itself.

**Reglas de Redondeo**: Follow the Alícuotas IVA pattern exactly — model in `models/configs.py`, routes in `routes/configs.py`, table partial + form partial in `templates/configuracion/partials/`. The new section appears as the last accordion item.

**DB**: `CREATE TABLE reglas_redondeo` with the user-provided schema. Model class `ReglaRedondeo` in `models/configs.py`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `templates/configuracion/configuraciones.html` | Modified | Accordion wrapper, split Tipo sections, new redondeo section |
| `models/configs.py` | Modified | New `ReglaRedondeo` model class |
| `routes/configs.py` | Modified | New HTMX routes + query in main route |
| `templates/configuracion/partials/_tabla_reglas_redondeo.html` | New | Table partial for HTMX list |
| `templates/configuracion/partials/_form_edit_regla_redondeo.html` | New | Modal edit form partial |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| HTMX targets break inside accordion DOM | Low | `hx-target` uses IDs inside accordion body — unaffected by wrapper change |
| Accordion collapse hides active HTMX forms | Low | No forms outside accordion body; all content renders inside `accordion-body` |
| New table without existing data | Low | Empty table is valid; users add rules on demand |

## Rollback Plan

1. Revert `configuraciones.html` to the pre-accordion version (restore `div.card.m-3` structure)
2. Remove `ReglaRedondeo` model from `models/configs.py`
3. Remove HTMX routes from `routes/configs.py`
4. Delete partial templates `_tabla_reglas_redondeo.html` and `_form_edit_regla_redondeo.html`
5. Drop table: `DROP TABLE IF EXISTS reglas_redondeo`

## Dependencies

- Bootstrap 5.3.3 (already loaded via CDN in `base.html`)
- No new Python packages

## Success Criteria

- [ ] All 13 sections render as accordion items with expand/collapse
- [ ] Configuración general expanded by default on page load
- [ ] Tipo IVAs and Tipo Documentos are separate accordion items
- [ ] HTMX add/edit/delete for reglas redondeo works without page reload
- [ ] Table partial refreshes after add/update/delete via HTMX
- [ ] No regression in existing CRUD sections (alícuotas, categorías, etc.)
