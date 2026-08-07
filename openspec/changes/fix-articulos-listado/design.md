# Design: fix-articulos-listado

## Technical Approach

Six isolated bugfixes across two files — no new abstractions introduced.
Backend: fix SQLAlchemy JOIN predicate abuse; guard column index out of range.
Frontend: fix DataTables config key typo, remove duplicate `language` block, fix counter API call, define `BASE_URL` via Jinja2.

---

## Architecture Decisions

| # | Decision | Options considered | Chosen | Rationale |
|---|----------|--------------------|--------|-----------|
| 1 | WHERE vs JOIN ON for optional filters | (a) keep ternary in JOIN ON, (b) conditional `.filter()` calls, (c) `outerjoin` + filter | **(b)** keep INNER JOIN, add `.filter()` only when value present | JOIN ON predicates belong to the JOIN semantics, not row filtering. `outerjoin` would change result set semantics (include articles without rubro/marca). Conditional `.filter()` matches existing pattern in `get_listado_stock`. |
| 2 | Column index guard | (a) expand `columns` list with sentinel strings, (b) keep guard `< len(columns)` as-is | **(a)** keep guard as-is — it already works | `order_column` 8/9 ≥ len(columns)=8 → guard triggers → `order_by = 'codigo'`. Guard is correct. Code comment clarifying intent is the only change needed. |
| 3 | `BASE_URL` definition | (a) `{{ request.host_url }}`, (b) `{{ url_for('static', filename='') }}`, (c) Jinja2 global | **(b)** `url_for('static', filename='')` | Returns the static URL prefix relative to the current deployment. No manual string stripping required. Consistent with other `url_for` calls already in the template. |
| 4 | Duplicate `language` key | Remove CDN url block vs remove inline block | **Remove CDN url block** (lines 183–185) — keep inline Spanish | Inline block is complete; CDN adds a network dependency and an extra round-trip. DataTables silently ignores the first `language` key when duplicate — the CDN block was already dead code. |
| 5 | Counter API | `tabla.data().count()` vs `tabla.page.info().recordsTotal` | **`recordsTotal`** | `data().count()` returns rows in the current page buffer only. `recordsTotal` is set by the server-side response (`iTotalRecords`) and reflects the full filtered set. |

---

## File Changes

| File | Action | Lines | Description |
|------|--------|-------|-------------|
| `services/articulos/reportes.py` | Modify | 37–41 | Replace JOIN ternary with `.join(plain)` + conditional `.filter()` |
| `services/articulos/reportes.py` | Modify | 22 | Add clarifying comment on column guard (no logic change) |
| `templates/articulos/articulos.html` | Modify | 127 | Add `const BASE_URL = "{{ url_for('static', filename='') | replace('/static/', '') }}";` — actually use `url_for('static', filename='img/articulos/')` directly in render function |
| `templates/articulos/articulos.html` | Modify | 160 | Replace `${BASE_URL}/static/img/articulos/` with `{{ url_for('static', filename='img/articulos/') }}/` baked as a JS constant |
| `templates/articulos/articulos.html` | Modify | 169 | Fix typo `ordereable` → `orderable` |
| `templates/articulos/articulos.html` | Modify | 183–185 | Remove CDN `language` block |
| `templates/articulos/articulos.html` | Modify | 211 | `tabla.data().count()` → `tabla.page.info().recordsTotal` |

---

## Exact Code Change Approach

### Fix 1 — JOIN filter (reportes.py L37–41)

**Before:**
```python
).join(
    Rubro, and_(Articulo.idrubro == Rubro.id, Rubro.id == idrubro if idrubro else True)
).join(
    Marca, and_(Articulo.idmarca == Marca.id, Marca.id == idmarca if idmarca else True)
)
```

**After:**
```python
).join(
    Rubro, Articulo.idrubro == Rubro.id
).join(
    Marca, Articulo.idmarca == Marca.id
)
# Move optional filters below, after the joins:
if idrubro:
    query = query.filter(Rubro.id == idrubro)
if idmarca:
    query = query.filter(Marca.id == idmarca)
```

Insert the conditional filters immediately after the query block (before the `search_value` block).

---

### Fix 2 — Column index guard (reportes.py L22)

No logic change. Add inline comment:
```python
# columns[0..7]; índices 8 (Imagen) y 9 (Acciones) no son ordenables → fallback 'codigo'
order_by = columns[order_column] if order_column < len(columns) else 'codigo'
```

---

### Fix 3 — BASE_URL (articulos.html L127)

Replace the DataTable init line with a preceding JS constant:
```js
const BASE_URL = "{{ url_for('static', filename='') }}";
```
Then in the imagen render function:
```js
return `<img src="${BASE_URL}img/articulos/${data}" ...>`;
```

`url_for('static', filename='')` returns `/static/` so `${BASE_URL}img/articulos/` → `/static/img/articulos/`.

---

### Fix 4 — Typo orderable (articulos.html L169)

```js
// Before
ordereable: false,
// After
orderable: false,
```

---

### Fix 5 — Duplicate language (articulos.html L183–185)

Remove these 3 lines entirely:
```js
language: {
    url: "//cdn.datatables.net/plug-ins/1.13.4/i18n/es-ES.json"
},
```

---

### Fix 6 — Counter (articulos.html L211)

```js
// Before
let total = tabla.data().count();
// After
let total = tabla.page.info().recordsTotal;
```

---

## Testing Strategy

| Layer | What | Approach |
|-------|------|----------|
| Manual | rubro=None → all articles visible | Load listing without filter, compare count to `SELECT COUNT(*) FROM articulos` |
| Manual | rubro=X → filtered correctly | Select a rubro, verify only matching articles appear |
| Manual | Click Imagen/Acciones header | Should not throw 500 — sort falls back to `codigo` |
| Manual | Counter badge | Should match total records in server response, not page count |
| Manual | Spanish UI | All DataTables labels rendered in Spanish |
| Manual | Delete/Edit buttons | URLs resolve correctly in dev and prod |

No automated tests exist for this view; manual verification matches the project's current test coverage level.

---

## Migration / Rollout

No migration required. Two-file change, no schema or DB dependency. Git revert is sufficient rollback.

---

## Open Questions

- None — all 6 fixes are unambiguous and self-contained.
