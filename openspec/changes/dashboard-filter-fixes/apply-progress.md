# Apply Progress: Dashboard Filter Fixes

## Summary

All 3 implementation tasks completed. Total changed lines: ~4 (plus 1 import removed).

## Phase 1: SQL Fix — ✅ Done

- **File**: `services/reportes.py:667`
- **Change**: `WHERE baja IS NULL` → `WHERE (baja IS NULL OR baja = '0000-00-00 00:00:00')`
- **Rationale**: Active sucursales with zero-date `baja` (legacy data) were being excluded from the filter dropdown.

## Phase 2: JS Fix — ✅ Done

- **File**: `static/js/dashboard-gerencial.js:637-640`
- **Change**: Added `form.dispatchEvent(new Event('submit'))` after each `setRangoFechas()` call in the keydown handler (Alt+H, Alt+S, Alt+M, Alt+T).
- **Rationale**: Keyboard shortcuts updated date inputs but never triggered the submit handler, so the dashboard didn't reload. Uses `dispatchEvent` (not `form.submit()`) to match the existing pattern at line 596 and respect the HTMX-aware submit listener.

## Phase 3: Model Fix — ✅ Done

- **File**: `models/sucursales.py:21`
- **Change**: `self.baja = timedelta(0)` → `self.baja = None`
- **Bonus**: Removed unused `from datetime import timedelta` import.
- **Rationale**: New sucursales now get proper `NULL` in the database instead of a zero-datetime that conflicts with the query logic.

## Files Changed

| File | Lines Changed | Description |
|------|--------------|-------------|
| `services/reportes.py` | 1 | SQL WHERE clause expanded |
| `static/js/dashboard-gerencial.js` | 4 | Form dispatch after each shortcut |
| `models/sucursales.py` | 2 | baja default + import cleanup |

## Verification Notes

- Manual verification required (no unit test infrastructure):
  - Sucursal dropdown shows branches with NULL and zero-date `baja`
  - Alt+H/S/M/T update dates AND trigger page reload
  - New sucursales via ORM get `baja = NULL` in DB
  - Button-click filter and HTMX refresh unaffected
