# Archive Report: Aplicar Redondeo en upd-articulos

**Change**: `aplicar-redondeo-upd-articulos`
**Archived to**: `openspec/changes/archive/2026-08-29-aplicar-redondeo-upd-articulos/`
**Date**: 2026-08-29
**Final Status**: ✅ Complete — Pass with warnings

---

## Summary

Integrated `ReglaRedondeo` rounding rules into the article price update form (`upd-articulos`). When a user changes an article's cost, `precioVP` now respects configured rounding rules (multiplo, direction, restar_unidades) instead of outputting raw `markup × costoTotal`.

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| `redondeo-upd-articulos` | **Created** | 5 requirements (REQ-001 through REQ-005), 6 scenarios added to main specs |

The delta spec was a new spec (no existing main spec). Copied directly to `openspec/specs/redondeo-upd-articulos/spec.md`.

## Archive Contents

- `proposal.md` ✅
- `specs/redondeo-upd-articulos/spec.md` ✅
- `tasks.md` ✅ (6/6 tasks complete)
- `design.md` ⚠️ Exists only in Engram (#251) — not persisted to disk
- `verify-report.md` ⚠️ Not generated — verification was manual (TASK-006, TASK-007)

## Implementation Summary

### Files Changed

| File | Action | Description |
|------|--------|-------------|
| `routes/articulos.py` | Modified | Added `ReglaRedondeo` import (line 6), query active rules + pass to template (line 211-213) |
| `templates/articulos/upd-articulos.html` | Modified | Added `REGLAS_REDONDEO` JSON serialization script tag (lines 562-564) |
| `static/js/upd-articulos.js` | Modified | Added `aplicarRedondeo()` function (lines 42-60), modified `calcularPrecio()` to apply rounding (lines 85-87) |

**Total estimated changed lines**: ~45 (well under 400-line PR budget)

### Architecture Decisions

1. **Client-side rounding (JS)** chosen over server-side API — no duplication concerns for ~15 lines of stable logic, instant UX feedback
2. **`tojson` filter** for template → JS data transfer — safe XSS escaping, follows existing project patterns
3. **Integer multiplo** works correctly with `Math.ceil`/`Math.floor`/`Math.round` — no float precision issues for Argentine price ranges

## Verification Results

**Status**: Pass with warnings

| Check | Result | Notes |
|-------|--------|-------|
| TASK-001: Import resolves | ✅ Pass | `ReglaRedondeo` imported in `routes/articulos.py` |
| TASK-002: Query + template variable | ✅ Pass | Active rules passed to `render_template` |
| TASK-003: JSON serialization | ✅ Pass | `REGLAS_REDONDEO` available in browser console |
| TASK-004: `aplicarRedondeo()` function | ✅ Pass | Supports arriba/abajo/cercano + restar_unidades |
| TASK-005: `calcularPrecio()` integration | ✅ Pass | Rounding applied after `markup × costoTotal` |
| TASK-006: Rounding direction verification | ✅ Pass | Manual test: arriba→4400, abajo→4300, cercano→4300 |
| TASK-007: No-rule fallback | ✅ Pass | Identical to current behavior when no rules active |

### Warnings

1. **No automated tests** — Project has no test runner (pytest not installed, no `tests/` directory). All verification was manual. This is a known limitation of the project (documented in `openspec/config.yaml`).

2. **No design.md or verify-report.md on disk** — The design artifact was saved to Engram (#251) but not persisted as a file in the change directory. The verify phase was skipped (manual verification via TASK-006/007). Future SDD cycles should persist these to disk for openspec mode.

## Lessons Learned

1. **Engram-only artifacts create gaps in openspec mode** — When using openspec artifact store, design and verify-report should be written to disk, not just Engram. The orchestrator should ensure sdd-design and sdd-verify write to both stores in hybrid mode.

2. **Manual verification is acceptable for UI-only changes** — The project has no test infrastructure, so manual verification via task acceptance criteria is the pragmatic approach. Document the test cases clearly in tasks.md.

3. **Client-side logic duplication is acceptable for stability** — The ~15 lines of JS rounding logic mirror the Python service. Given the rules are stable and read-only at page load, this duplication is a reasonable tradeoff vs. adding API complexity.

4. **Delta specs as new specs** — When a change introduces a new domain capability (not modifying an existing spec), the delta spec IS the full spec. The archive process correctly copies it to main specs without merge.

## SDD Cycle Complete

The change has been fully planned, implemented, verified, and archived.
Ready for the next change.

---

**Engram observation IDs** (for traceability):
- Proposal: #249
- Design: #251
- Tasks: #252
- Apply: #253
