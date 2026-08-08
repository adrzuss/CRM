## Verification Report

**Change**: fix-stock-sucursales-datatables
**Version**: delta spec `openspec/changes/fix-stock-sucursales-datatables/specs/articulos-api-json/spec.md` (v1)
**Mode**: Standard (no Strict TDD configured)

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 8 checkboxes (1.1–1.4, 2.1–2.3, 3.1–3.5) |
| Tasks complete | 8 |
| Tasks incomplete | 0 |

### Build & Tests Execution
**Build**: ➖ N/A (proyecto Flask, sin paso de build; `git show 461fabd` compila el diff como fuente válida)
**Tests**: ✅ 51 passed (0 failed, 0 skipped) — 2.56s
```text
$ venv\Scripts\python.exe -m pytest tests/ -q
...................................................                      [100%]
51 passed, 2 warnings in 2.56s
```
**Coverage**: ➖ Not available (sin configuración de cobertura en el repo; no exigida por la task).

### Evidencia runtime adicional (test client real sobre el handler)
Script de verificación ejecutado contra la app (SQLite in-memory, decoradores reales `@check_session`/`@alertas_mensajes` parcheados igual que en los tests):
- `GET /articulos/api/lst_stock_sucursales` sin query string → **200**, `draw=1`, `recordsTotal:0`, `recordsFiltered:0`, `data:[]`
- `GET ...` con `idrubro=""` (filtro vacío) → **200**, `data:[]` (guard retorna, nunca 500)
- Guard de `order_by` (mlr expresión exacta del commit, `columns_names` len=7): `order_column` `None` → `'codigo'`; `0` → `'codigo'`; última sucursal (5) → columna `S2` sin `IndexError`; borde `6` (`order_column+1 == len`) → `'codigo'`; fuera de rango `7`, `999` → `'codigo'`. 11/11 checks runtime PASS.

### Spec Compliance Matrix
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| REQ-1 Contrato DataTables `api_lst_stock_sucursales` | Carga inicial sin query string | `tests/test_articulos.py > test_api_lst_stock_sucursales_sin_parametros` | ✅ COMPLIANT |
| REQ-1 | Búsqueda sin `order[0][column]` | `tests/test_articulos.py > test_api_lst_stock_sucursales_sin_order_column` (assert `order_column=0` pasa al service) | ✅ COMPLIANT |
| REQ-1 | Orden por la última sucursal (dentro del rango) | sin pytest dedicado; runtime-expr (check B2) + task 3.2 manual | ⚠️ PARTIAL |
| REQ-1 | Orden fuera de rango (borde del índice) | sin pytest dedicado; runtime-expr (checks B3/B4, `None`) + task 3.2 manual | ⚠️ PARTIAL |
| REQ-1 | Respuesta plana con `id` oculto | handler testea shape plana; flatten real en service (estático, stock.py L133–141); sin pytest del service | ⚠️ PARTIAL |
| REQ-2 Guard filtro vacío retorna respuesta vacía | Stock por sucursal sin filtros | `test_api_lst_stock_sucursales_sin_parametros` (assert `mock_service.assert_not_called()` + `data:[]`) + runtime check A | ✅ COMPLIANT |
| REQ-2 | Lista de precios sin `idlista` | guard verificado estático (`routes/articulos.py` L446 `return jsonify`) ; suite regresión 51/51 | ⚠️ PARTIAL (estático) |
| REQ-2 | Stock sin `idmarca` o sin `idrubro` (lst_stock/faltantes) | guard verificado estático (`routes/articulos.py` L509, L543 `return`); suite regresión 51/51 | ⚠️ PARTIAL (estático) |

**Compliance summary**: 4/8 directamente cubiertos y activados (test dedicado o runtime real del handler); 4/8 PARTIAL — sin pytest dedicado, pero con evidencia estática + ejecución de la expresión exacta del guard y suite de regresión verde. La brecha de cobertura está en escenarios que el plan (Fase 2/3) asignó explícitamente a verificación manual, no a pytest.
**Echo de `draw`**: cubierto por `test_api_lst_stock_sucursales_sin_order_column` (request `draw=1` → response `draw=1`) + runtime check A (`draw` default 1).

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|------------|--------|-------|
| Default `draw=1` en handler (L595) | ✅ Implemented | `request.args.get('draw', 1, type=int)` — confirma diff `git show 461fabd` |
| Default `order_column=0` en handler (L602) | ✅ Implemented | `request.args.get('order[0][column]', 0, type=int)` |
| `return jsonify(response)` en guard de filtro vacío (L613) | ✅ Implemented | El guard retorna antes del `try:`; nunca ejecuta `obtener_stock_sucursales` |
| Guard `order_column is not None && order_column+1 < len(columns_names)` (stock.py:119) | ✅ Implemented | Acepta índice máx `len-1`; fallback `'codigo'`; elimina `TypeError`/`IndexError` |
| Fallback `'codigo'` (primera columna visible) | ✅ Implemented | `columns_names[0]=Articulo.id` oculto → offset `+1` correcto, AD-3 |
| Respuesta JSON plana `{draw, recordsTotal, recordsFiltered, data}` | ✅ Implemented | `jsonify(resposne)` happy path (L624); guard con `data:[]` |

### Coherence (Design)
| Decision (design.md) | Followed? | Notes |
|----------|-----------|-------|
| AD-1 Defaults `draw`/`order_column` en handler | ✅ Yes | Patrón de los 4 hermanos replicado; `start`/`length` ya tenían default |
| AD-2 `None`-guard en service (defensa en profundidad) | ✅ Yes | `stock.py:119` cumple `is not None` |
| AD-3 Offset `+1` por columna oculta `id` | ✅ Yes | `order_column+1 < len(columns_names)`; verificado que `columns_names[0]` es `Articulo.id.label("id")` |
| AD-4 Fallback `'codigo'` | ✅ Yes | coincide con diff |
| AD-5 Guard filtro vacío → HTTP 200 `data:[]` (no 404) | ✅ Yes | `return jsonify(response)` antes de `try:` |
| AD-6 Typo `resposne` (L618/L624) no se toca | ✅ Yes | diff no alcanza esas líneas; permanece tal cual |

### Issues Found
**CRITICAL**: None
**WARNING**:
1. **Delivery risk (branch coordination)** — el commit `461fabd` está en `style/table-header-colors` (NO en `main`). La rama está 3 commits adelante de `main` (merge-base `d7e89c0`): `02ad8f0 style(articulos)…`, `eb59aaf fix(articulos) endpoints DataTables…` (cambio previo fix-busqueda-articulos, ya archivado en `openspec/changes/archive/2026-08-07-fix-busqueda-articulos/`), `461fabd` (este fix). Además `origin/style/table-header-colors` está 2 commits detrás (nada pusheado). Es un problema de coordinación de entrega (merge/cherry-pick a `main`), No es falla de código ni de tests.
**SUGGESTION** (no se toca código en verificación):
1. Typo `responso` en `routes/articulos.py` L618 (define) / L624 (usa) — funcional (define+y usa), fuera de scope, documentado en la spec (AD-6). Corregir en un sweep futuro.
2. Los 2 escenarios de borde de orden (última sucursal / fuera de rango) no tienen pytest dedicado; aunque la tarea 3.2 los verifica manualmente y evidencé runtime la expresión, convendría un test pequeño del guard (`order_by`) para congelar el comportamiento (opcional).
3. No quedó pendiente el paso de **archive** (sync de la delta spec a la main spec con los ya citados 5 endpoints + enunciar `api_lst_stock_sucursales`).

### Verdict
**PASS WITH WARNINGS**
Código y tests en contra: las 4 zonas del fix están implementadas exactamente como spec/design/tasks, 51/51 pytest verde, y el runtime del handler + guard del service probado; la única advertencia es la ubicación del commit (branch `style/table-header-colors`, entrega pendiente de rebase/merge a `main`), que es coordinación, no calidad del cambio.

*Skill Resolution: `fallback-registry` — cargó `sdd-verify/SKILL.md` + `_shared/sdd-phase-common.md` + `references/report-format.md` desde el path inyectado; el `_atl/skill-registry.md` del proyecto no lista skill propia para verificación.*