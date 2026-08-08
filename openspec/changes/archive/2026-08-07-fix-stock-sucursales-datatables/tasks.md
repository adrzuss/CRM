# Tasks: fix-stock-sucursales-datatables

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~85–120 (4 líneas prod + ~70 test) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-always (orquestador) |
| Chain strategy | pending |

```
Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low
```

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Fix 3 sitios + tests + commit único | PR 1 | 2 archivos prod, base main; rollback `git revert` |

## Fase 1: Implementación

- [x] 1.1 `routes/articulos.py` L595: `draw = request.args.get('draw', 1, type=int)` — default `draw`=1
- [x] 1.2 `routes/articulos.py` L602: `order_column = request.args.get('order[0][column]', 0, type=int)` — default `0`
- [x] 1.3 `routes/articulos.py` L606–612: agregar `return jsonify(response)` al final del guard de filtro vacío (antes de `try:` L613); sin tocar el typo `resposne` (L617)
- [x] 1.4 `services/articulos/stock.py` L119: guard `order_column is not None and order_column+1 < len(columns_names)`, fallback `'codigo'` (offset `+1` por columna oculta `id`, diseño AD-3; test 4)

## Fase 2: Verificación — pytest

- [x] 2.1 `tests/test_articulos.py`, patrón `test_api_articulos_datatables` (L87) con mocks `get_alertas`/`get_mensajes`/`obtener_stock_sucursales`: sin query string → 200, `draw`=1, `data:[]`; assert service NO invocado (corta en guard)
- [x] 2.2 Idem: con `idmarca`+`idrubro`, sin `order[0][column]` → assert la mock `obtener_stock_sucursales` recibe `order_column=0`
- [x] 2.3 Regresión completa: `pytest tests/` verde

## Fase 3: Verificación — Manual y diff

- [x] 3.1 `client.get('/articulos/api/lst_stock_sucursales?idmarca=1&idrubro=1&draw=1')` sin `order` → 200, orden `'codigo'`
- [x] 3.2 Borde: `order[0][column]=N` (última sucursal, `len-1`, `len`) → 200, fallback `'codigo'`, sin `TypeError`/`IndexError`
- [x] 3.3 Filtro vacío: sin `idmarca`/`idrubro` → 200 `{draw, recordsTotal:0, recordsFiltered:0, data:[]}` (spec: "Stock por sucursal sin filtros")
- [x] 3.4 Nota UI: `templates/articulos/stock-sucursales.html` L134–159 — carga inicial con filtros "TODOS" → 200 `data:[]`, sin `ajax.error` (L144–146); "Consultar" recarga; sin rediseño
- [x] 3.5 `git status`/`git diff` previo al commit: stage SOLO `routes/articulos.py` + `services/articulos/stock.py` + `tests/test_articulos.py`; **NO stage `app.log` ni `routes/__pycache__/*.pyc`** (suciedad de un change previo, fuera de scope) — commit `461fabd`