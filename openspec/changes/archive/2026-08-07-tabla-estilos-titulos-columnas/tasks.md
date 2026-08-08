# Tasks: Estilos de títulos y encabezados de columnas en tablas

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~5 (1 archivo: `static/css/main.css`) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-always |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Header teal oscuro + texto blanco en las 3 tablas `.table-modern` | PR 1 | `static/css/main.css` (L1625, L1630); sin templates, sin tests |

## Phase 1: Implementación CSS

- [x] 1.1 `static/css/main.css:1625` — `.table-modern .table-header`: cambiar `background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);` → `background: linear-gradient(135deg, #00808a 0%, #005f66 100%);` y `border-bottom: 2px solid #dee2e6;` → `border-bottom: 2px solid #005f66;`
- [x] 1.2 `static/css/main.css:1630` — `.table-modern .table-header th`: cambiar `color: #495057;` → `color: #ffffff;` (solo `color`; NO tocar tipografía uppercase/0.85rem/600, ni padding/bordes, ni la media-query L1770)

## Phase 2: Verificación

- [ ] 2.1 Arranque: `python index.py` sin errores (verify build = `config.yaml` → `build_command`)
- [ ] 2.2 Visual: navegar a las 3 vistas `.table-modern` y comprobar header con gradiente teal `#00808a→#005f66` y texto blanco:
  - listado artículos → `templates/articulos/partials/_lst-articulos.html`
  - listado entidades → `templates/entidades/partials/_lst-entidades.html`
  - crédito de entidades → `templates/entidades/fin-ent-cred.html:78`
- [ ] 2.3 Contraste: verificar WCAG AA — blanco sobre `#00808a` = 4.71:1, sobre `#005f66` ≈ 7:1 (ambos ≥ 4.5:1)
- [ ] 2.4 Regresión: inspeccionar una tabla sin `table-modern` → sin cambios (selector acotado, ~60 tablas Bootstrap intactas)
- [ ] 2.5 `git diff`: solo 2 líneas editadas en 1 archivo; NO se creó archivo CSS nuevo
