# Design: Dashboard Filter Fixes

## Technical Approach

Three targeted bug fixes in existing files, addressing root causes identified in exploration:
1. SQL query excludes active sucursales with zero-date `baja`
2. Keyboard shortcuts update dates but don't trigger form submission
3. Model defaults `baja` to `timedelta(0)` instead of `None`

All changes are minimal line-level edits with no new files or interfaces.

## Architecture Decisions

### Decision: SQL WHERE clause for active sucursales

**Choice**: `WHERE (baja IS NULL OR baja = '0000-00-00 00:00:00')`
**Alternatives considered**: 
- Cast zero-date to NULL via `COALESCE` — rejected, adds unnecessary complexity
- Filter in Python after fetch — rejected, wastes DB roundtrip
**Rationale**: Handles both legacy zero-date rows and new NULL rows explicitly. Simple OR condition, no performance impact.

### Decision: Form dispatch method

**Choice**: `form.dispatchEvent(new Event('submit'))`
**Alternatives considered**:
- `form.submit()` — rejected, bypasses event listeners and HTMX handling
- `form.requestSubmit()` — rejected, not supported in all browsers
**Rationale**: `dispatchEvent` triggers the existing submit handler which does `e.preventDefault()` + AJAX reload. Matches existing button-click behavior.

### Decision: Model default for baja field

**Choice**: `self.baja = None`
**Alternatives considered**:
- `self.baja = timedelta(0)` with SQL fix only — rejected, perpetuates inconsistent data
- Default at column level — rejected, existing rows unaffected
**Rationale**: New sucursales get proper `NULL` in DB. Combined with SQL fix #1, both NULL and zero-date rows are included.

## Data Flow

```
User presses Alt+H → JS keydown handler
    ↓
setRangoFechas(0) updates date inputs
    ↓
form.dispatchEvent(new Event('submit')) fires
    ↓
Existing submit handler captures event
    ↓
AJAX reload with new date params
    ↓
Backend query includes sucursales with baja = NULL OR '0000-00-00 00:00:00'
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `services/reportes.py:667` | Modify | SQL WHERE clause: add `OR baja = '0000-00-00 00:00:00'` |
| `static/js/dashboard-gerencial.js:637-640` | Modify | Add `form.dispatchEvent(new Event('submit'))` after each `setRangoFechas()` call |
| `models/sucursales.py:22` | Modify | Change `self.baja = timedelta(0)` to `self.baja = None` |

## Interfaces / Contracts

No new interfaces. Existing patterns preserved:
- SQL uses `text()` with raw query (no parameter binding needed for static string)
- JS uses existing `form` variable from closure scope
- Model `__init__` signature unchanged

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Manual | Sucursal dropdown shows active branches | Load dashboard, verify dropdown populated |
| Manual | Keyboard shortcuts reload dashboard | Press Alt+H, verify page reloads with new dates |
| Manual | New sucursales have NULL baja | Create via ORM, check DB directly |
| Unit | N/A | No test infrastructure in place |

## Migration / Rollout

No migration required. Existing rows with `baja = '0000-00-00 00:00:00'` are handled by SQL fix. New rows default to `NULL`.

## Open Questions

- [ ] None — all decisions resolved with clear rationale
