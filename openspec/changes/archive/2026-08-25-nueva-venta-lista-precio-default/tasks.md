# Tasks: Auto-select Default Price List on Punto de Venta Selection

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~10 lines (additions + deletions) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | single-pr-default |
| Chain strategy | size-exception (not needed) |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | All 3 surgical edits | PR 1 | Backend + JS + template; ~10 lines total |

---

## Phase 1: Backend — Extend `set_punto_vta` response

- [x] 1.1 In `routes/ventas.py` (~line 83), add `'id_lista_precio': puntoVta.id_lista_precio` to the `return jsonify(...)` dict in `set_punto_vta()`. `None` serializes to `null` automatically — no cast needed.

## Phase 2: Frontend JS — Apply price list in `asignarPuntoVenta()`

- [x] 2.1 In `static/js/nueva_venta.js`, after the line that sets `pos_printer` value (~line 571), insert the `selectLista` block: guard with `if (selectLista)`, set value to `result.id_lista_precio` when truthy, else fall back to `selectLista.options[0].value` when options exist. Do NOT call `recalcularPreciosPorLista()`.

## Phase 3: Template — Fix hardcoded page-load default

- [x] 3.1 In `templates/ventas/nueva_venta.html` (~line 118), replace `{{ 'selected' if lista.id == 1 else '' }}` with `{{ 'selected' if loop.first else '' }}` on the `#idlista` `<option>` tag.

## Phase 4: Manual Verification

- [ ] 4.1 Select a POS with `id_lista_precio = N` → confirm `#idlista` shows `N`.
- [ ] 4.2 Select a POS with `id_lista_precio = null` → confirm `#idlista` shows the first option.
- [ ] 4.3 Load the page fresh → confirm the first list is pre-selected regardless of its DB `id`.
- [ ] 4.4 After auto-select, change `#idlista` manually → confirm `recalcularPreciosPorLista()` fires normally.
