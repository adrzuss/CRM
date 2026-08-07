# Tasks: fix-articulos-listado

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~30–40 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | All 6 bugfixes in both files | PR 1 | Self-contained; no migrations |

---

## Phase 1: Backend Fixes (`services/articulos/reportes.py`)

- [x] 1.1 **Fix JOIN filter bug** — Replace ternary predicates in `join(Rubro, ...)` and `join(Marca, ...)` with plain FK equality; add conditional `.filter(Rubro.id == idrubro)` / `.filter(Marca.id == idmarca)` calls after the joins. *(Satisfies: JOIN Filter Must Not Restrict Unfiltered Results — ~8 lines changed)*
- [x] 1.2 **Add column guard comment** — Add inline comment on the `order_by` guard line clarifying that indices 8 (Imagen) and 9 (Acciones) fall back to `'codigo'`. *(Satisfies: Column Index Guard Must Cover All Non-DB Columns — ~1 line changed)*

## Phase 2: Frontend Fixes (`templates/articulos/articulos.html`)

- [x] 2.1 **Define BASE_URL constant** — Add `const BASE_URL = "{{ url_for('static', filename='') }}";` before the DataTable init block; update the `imagen` render function to use `${BASE_URL}img/articulos/${data}`. *(Satisfies: BASE_URL MUST Be Defined Before DataTable Initialisation — ~3 lines changed)*
- [x] 2.2 **Fix `orderable` typo** — Change `ordereable: false` → `orderable: false` in the Acciones column definition. *(Satisfies: Acciones Column MUST Disable Sorting — 1 line changed)*
- [x] 2.3 **Remove duplicate CDN language block** — Delete the 3-line `language: { url: "//cdn.datatables.net/..." }` block. *(Satisfies: DataTable Language MUST Use Inline Spanish Definition — 3 lines removed)*
- [x] 2.4 **Fix record counter** — Replace `tabla.data().count()` with `tabla.page.info().recordsTotal` in the `draw` event handler. *(Satisfies: Record Counter MUST Reflect Total Filtered Records — 1 line changed)*

## Phase 3: Verification

- [ ] 3.1 Load listing with no filters → verify all active articles appear (no silent rubro/marca=1 restriction).
- [ ] 3.2 Apply a rubro filter → verify only matching articles are returned.
- [ ] 3.3 Click Imagen column header → confirm no 500 error; sort falls back to `codigo`.
- [ ] 3.4 Click Acciones column header → confirm column does not trigger sort.
- [ ] 3.5 Check `#contadorArticulos` on page load → must match server `recordsTotal`, not page row count.
- [ ] 3.6 Check `#contadorArticulos` after applying a filter → must update to filtered total.
- [ ] 3.7 Verify DataTable labels render in Spanish without CDN language request.
- [ ] 3.8 Verify image thumbnails and delete/edit button URLs resolve correctly.
