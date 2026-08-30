## Exploration: Configuraciones.html Visual Redesign — Accordion Pattern

### Current State

The `configuraciones.html` template is a **357-line monolithic template** containing **12 configuration sections**, each rendered as a stacked `div.card.m-3`. Every section has an `<h4>` title inside the card, followed by a `card-body` with the section content.

**Section inventory (in order):**

| # | Section | Pattern | HTMX Add Route | Partial Table |
|---|---------|---------|----------------|---------------|
| 1 | Configuración general | Standalone form (no table) | N/A (POST form) | N/A |
| 2 | Alícuotas de IVA | Form (col-5) + Table (col-7) | `htmx_add_alc_iva` | `_tabla_alc_iva.html` |
| 3 | Alícuotas de Ing. Brutos | Form (col-5) + Table (col-7) | `htmx_add_alc_ib` | `_tabla_alc_ib.html` |
| 4 | Listas de precios | Form (col-5) + Table (col-7) | `htmx_add_lista_precio` | `_tabla_listas_precios.html` |
| 5 | Listas de tareas | Form (col-5) + Table (col-7) | `htmx_add_tarea` | `_tabla_tareas.html` |
| 6 | Plan de cuentas | Form (col-5) + Table (col-7) | `htmx_add_planCta` | `_tabla_plan_ctas.html` |
| 7 | Tipo IVAs + Tipo Documentos | **Side-by-side** (col-6 + col-6), table-only | N/A (edit-only) | `_tabla_tipo_ivas.html` + `_tabla_tipo_docs.html` |
| 8 | Categorías de clientes | Form (col-5) + Table (col-7) | `htmx_add_categoria` | `_tabla_categorias.html` |
| 9 | Monedas y billetes | Form (col-5) + Table (col-7) | `htmx_add_monedabillete` | `_tabla_monedas_billetes.html` |
| 10 | Colores | Form (col-5) + Table (col-7) | `htmx_add_color` | `_tabla_colores.html` |
| 11 | Detalle | Form (col-5) + Table (col-7) | `htmx_add_detalle_articulo` | `_tabla_detalles_articulos.html` |

**Existing consistent pattern (9 of 12 sections):**
```html
<div class="card m-3">
    <h4 class="m-3">Title</h4>
    <div class="card-body">
        <div class="row">
            <div class="col-md-5">
                <div class="card">
                    <div class="card-body">
                        <h6>Ingreso de ...</h6>
                        <form hx-post="..." hx-target="#tabla-xxx" hx-swap="innerHTML" ...>
                            <!-- form fields -->
                            <button class="btn btn-exito" type="submit">Grabar</button>
                        </form>
                    </div>
                </div>
            </div>
            <div class="col-md-7">
                <div class="card" id="tabla-xxx">
                    {% include 'partials/_tabla_xxx.html' %}
                </div>
            </div>
        </div>
    </div>
</div>
```

**Non-standard section:**
- **Tipo IVAs + Tipo Documentos** (line 182-202): A single card containing two side-by-side `col-6` columns, each with just a table (no add form). These are edit-only sections.

### Affected Areas

- `templates/configuracion/configuraciones.html` — Main template, needs complete restructuring to accordion layout
- `templates/configuracion/partials/_configuracion.html` — Configuración general section (included as-is, no structural change needed beyond accordion wrapping)
- `templates/configuracion/partials/_tabla_alc_iva.html` — Alícuotas IVA table partial
- `templates/configuracion/partials/_tabla_alc_ib.html` — Alícuotas IB table partial
- `templates/configuracion/partials/_tabla_listas_precios.html` — Listas precios table partial
- `templates/configuracion/partials/_tabla_tareas.html` — Tareas table partial
- `templates/configuracion/partials/_tabla_plan_ctas.html` — Plan cuentas table partial
- `templates/configuracion/partials/_tabla_tipo_ivas.html` — Tipo IVAs table partial
- `templates/configuracion/partials/_tabla_tipo_docs.html` — Tipo Documentos table partial
- `templates/configuracion/partials/_tabla_categorias.html` — Categorías table partial
- `templates/configuracion/partials/_tabla_monedas_billetes.html` — Monedas/billetes table partial
- `templates/configuracion/partials/_tabla_colores.html` — Colores table partial
- `templates/configuracion/partials/_tabla_detalles_articulos.html` — Detalles table partial
- `routes/configs.py` — Needs new route/model for "Reglas de redondeo" section
- `models/configs.py` — Needs new model for "Reglas de redondeo" if not exists
- `static/css/main.css` — May need additional accordion-specific styles

### Bootstrap 5 Accordion Availability

**YES — Bootstrap 5.3.3 is fully available:**
- CSS CDN: `https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css` (line 25 of base.html)
- JS Bundle (includes Popper): `https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js` (line 117 of base.html)

The Bootstrap 5 accordion component requires NO additional dependencies. It uses standard Bootstrap CSS classes (`accordion`, `accordion-item`, `accordion-header`, `accordion-button`, `accordion-collapse`, `accordion-body`) and data attributes (`data-bs-toggle="collapse"`, `data-bs-target="..."`).

### HTMX Integration Consideration

HTMX partials render table content into `#tabla-xxx` divs. The accordion pattern is compatible because:
- The `hx-target` and `hx-swap` attributes reference the table container divs, which will still exist inside accordion bodies
- Bootstrap 5 accordion collapse/expand is CSS-driven and won't interfere with HTMX DOM swaps
- The existing `hx-on::after-request="if(event.detail.successful) this.reset()"` pattern works unchanged

### Partials That Need Modification

**Table partials (11 files)** — These are fine as-is since HTMX swaps their innerHTML. The only change is that their parent containers will now be inside accordion bodies instead of standalone cards. No changes needed to the partials themselves.

**The main template (`configuraciones.html`)** — This is where ALL the structural change happens. Each `<div class="card m-3">` section wraps into an `accordion-item`.

### Sections with Non-Standard Layouts

1. **Configuración general** (section 1) — Standalone form, no table, no HTMX. This is a complex multi-section form with sub-sections. Should probably be the **first accordion item, expanded by default**.

2. **Tipo IVAs + Tipo Documentos** (section 7) — Single card with two side-by-side `col-6` sections, each with only a table (no add form). These are edit-only. Could be split into two accordion items or kept as one with internal tabs.

### Approach: Bootstrap 5 Accordion

**Structure per section:**
```html
<div class="accordion-item">
    <h2 class="accordion-header">
        <button class="accordion-button collapsed" type="button" 
                data-bs-toggle="collapse" data-bs-target="#collapse-xxx">
            <i class="fas fa-icon me-2"></i> Section Title
        </button>
    </h2>
    <div id="collapse-xxx" class="accordion-collapse collapse" data-bs-parent="#configAccordion">
        <div class="accordion-body">
            <!-- existing section content (form+table row) -->
        </div>
    </div>
</div>
```

**Recommendation:**
- Wrap all 12 sections in a single `<div class="accordion" id="configAccordion">`
- Each section becomes an `accordion-item`
- First item (Configuración general) should be expanded by default (`accordion-button` without `collapsed` class, `accordion-collapse show`)
- Use `data-bs-parent="#configAccordion"` for mutual exclusion (only one open at a time)
- Add section icons to accordion buttons for visual distinction
- For "Tipo IVAs + Tipo Documentos", split into two separate accordion items for better UX
- Add CSS for accordion button styling to match the project's design system (gradients, custom colors)

**Pros:**
- Bootstrap 5 native — no new dependencies
- Reduces visual clutter — only one section visible at a time
- Consistent with Bootstrap ecosystem already in use
- HTMX partials work unchanged
- Minimal JS needed (Bootstrap handles collapse behavior)

**Cons:**
- Users can only see one section at a time (may slow down users who frequently jump between sections)
- The existing nested card-inside-card pattern may look odd inside accordion body — need to flatten the inner cards or style them as bordered sections

### Risks

- **HTMX + Accordion interaction**: If a user expands a section, submits via HTMX, the partial swap works. But if they collapse and re-expand, the previously swapped content persists (which is correct behavior). No risk here.
- **Inner nested cards**: The existing pattern has a `card` inside the accordion `accordion-body` (the form card and the table card). These should be restyled to remove the outer card border or kept as subtle sections to avoid visual nesting.
- **"Reglas de redondeo" section**: Requires new model, route, partial, and form. This is a new feature addition on top of the visual redesign.

### Ready for Proposal

Yes — the exploration is complete. The orchestrator should:
1. Confirm the accordion approach (single accordion, one open at a time)
2. Decide whether "Tipo IVAs + Tipo Documentos" should be one or two accordion items
3. Clarify what "Reglas de redondeo" should contain (fields, validation, behavior)
4. Proceed to SDD proposal phase
