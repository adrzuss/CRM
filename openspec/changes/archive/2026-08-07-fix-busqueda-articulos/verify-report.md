# Verification Report

**Change**: fix-busqueda-articulos
**Version**: articulos-api-json (spec.md) — ADDED requirements
**Mode**: Standard (strict TDD deshabilitado — `openspec/config.yaml`: `strict_tdd: false`, `runner: null`; pytest 9.1.1 instalado, checks manuales de API primarios)

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 13 (Fase 1: 1.1–1.5; Fase 2: 2.1–2.2; Fase 3: 3.1–3.5; Fase 4: 4.1) |
| Tasks complete | 13/13 `[x]` |
| Tasks incomplete | 0 |

### Build & Tests Execution

**Build**: ✅ Pasado — aplicación importada y arrancada vía `create_app()` (test client) sin errores de import/sintaxis; `git show eb59aaf` aplica limpio sobre HEAD `02ad8f0`.

**Tests**: ✅ 49 passed (pytest suite de regresión completa)
```text
python -m pytest tests/ -q
49 passed, 2 warnings in ~2.5-3.0s
```
(deprecation warnings de Flask-Migrate `get_engine` — preexistentes, no relacionados)

**Checks manuales (harness runtime, `D:\Temp\opencode\verify_fix_busqueda.py`)**: ✅ 30/30 PASS
```text
RESUMEN: 30/30 PASS
# Escenarios del spec ejecutados contra handlers y services reales (solo capa DB mockeada):
SCE1  Sin query string -> 200 + claves + defaults (draw=1,start=0,length=25,order_column=0)  PASS
SCE2  Búsqueda sin order -> 200 + recordsFiltered=12                                          PASS
SCE3  Fallback 'codigo' (None / 8 / 9 / 0 / 2) en los 4 services, sin TypeError               20/20 PASS
SCE4  Echo draw: draw=3 -> draw=3 (handler y guard vacío)                                   2/2 PASS
SCE6  lst_precios sin idlista -> 200 data:[] recuentos 0, NO llama service                  PASS
SCE7  lst_stock / lst_stock_faltantes sin idmarca/idrubro -> 200 data:[] recuentos 0       2/2 PASS
Regresión order=8|9 (Imagen/Acciones) -> 200 sin 500                                      2/2 PASS
```

**Coverage**: ➖ No disponible (no configurado; no aplica en modo manual-primario)

### Spec Compliance Matrix

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| REQ-1 Respuesta DataTables válida sin `order` (defaults draw=1/start=0/length=25/order_column=0, HTTP 200 nunca 500) | Carga inicial sin query string | harness SCE1: `/api/articulos` GET sin query → 200 + claves `draw/recordsTotal/recordsFiltered/data` + defaults propagados al service | ✅ COMPLIANT |
| REQ-1 idem | Búsqueda sin parámetro de orden | harness SCE2: `search[value]=abc` sin `order` → 200 + `data` y `recordsFiltered=12` | ✅ COMPLIANT |
| REQ-1 idem | Fallback de orden a 'codigo' | harness SCE3: `order_column` `None|8|9` en `get_listado_articulos/stock/stock_faltantes/precios` → `order_by='codigo'` sin TypeError/IndexError; índice válido → columna real (`2`→`marca`) | ✅ COMPLIANT |
| REQ-1 idem | Echo de `draw` | harness SCE4: `draw=3` → `draw=3` en JSON (handler y guard vacío) | ✅ COMPLIANT |
| REQ-1 idem | Recuento de registros | harness SCE5b: con query mockeada `count()=200` → `recordsTotal=200`, `recordsFiltered=200`. ⚠️ **Desviación de escenario**: el spec asume `recordsTotal`=total sin filtro (200) y `recordsFiltered`=filtrado (12); la implementación real cuenta UNA sola vez post-filtro y devuelve el mismo valor en ambos campos (`get_listado_articulos` L77→L99: `return draw, total_records, total_records, data`; ídem los otros 3 services). Comportamiento PREEXISTENTE, no introducido ni modificado por este cambio (scope: solo defaults/guards) | ⚠️ PARTIAL |
| REQ-2 Guards de filtro vacío (lst_precios/lst_stock/lst_stock_faltantes) | Lista precios sin `idlista` | harness SCE6: → 200 `data:[]` `recordsTotal:0` `recordsFiltered:0`; service `get_listado_precios` NO invocado (mock `.called == False`) | ✅ COMPLIANT |
| REQ-2 idem | Stock / faltantes sin `idmarca`/`idrubro` | harness SCE7/7b: 200 `data:[]` recuentos:0; services NO invocados | ✅ COMPLIANT |

**Compliance summary**: 6/7 escenarios compliant, 1/7 partial (rechazos de conteo, preexistente, fuera de alcance).

### Correctness (Static + Runtime Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| Defaults en handler `api_articulos` | ✅ Implementado | `routes/articulos.py:107-114`: `draw=1,start=0,length=25,order_column=0` (dif L104-114) |
| Defaults en 3 endpoints de listado | ✅ Implementado | `routes/articulos.py:427/435`, `:491/498`, `:525/532` (`draw=1, order_column=0`) |
| Guard None en `order_by` services | ✅ Implementado | `reportes.py:23,106,175`; `precios.py:20` (`order_column is not None and order_column < len(columns)`) |
| `return jsonify(response)` en guards vacíos | ✅ Implementado | `routes/articulos.py:446, 509, 540` — misma indentación que el dict; el handler ya no continúa a la consulta |
| Echo de `draw` preservado | ✅ Correcto | default solo cuando falta; valor recibido se replica tal cual |
| Frontend sin alerta `ajax.error` | ✅ Correcto por contrato | con HTTP 200 + JSON válido DataTables, `$.fn.dataTable` ejecuta el success handler; sin driver E2E en el proyecto (no hay forma automatizada — ver SUGGESTION) |

### Coherence (Design)

| Decision (design.md) | Followed? | Notes |
|----------------------|-----------|-------|
| D1 Default `draw` en handler (no en service) | ✅ Yes | `request.args.get('draw', 1, type=int)` en los 4 handlers |
| D2 Double guard handler+service para `order_column` | ✅ Yes | default 0 en handlers + `is not None` en services |
| D3 Fallback de orden = `'codigo'` | ✅ Yes | coincide con doc L22 y con `columns[0]` |
| D4 Echo vs default de `draw` | ✅ Yes | echo del valor recibido; default solo cuando falta |
| D5 Guard vacío → `jsonify(response)` HTTP 200 | ✅ Yes | retorno antes del query subyacente |

### Diff Scope (commit eb59aaf)

| Archivo | En commit | Working tree |
|---------|-----------|--------------|
| `routes/articulos.py` | ✅ (+... -... líneas) | limpio |
| `services/articulos/reportes.py` | ✅ (3 líneas) | limpio |
| `services/articulos/precios.py` | ✅ (1 línea) | limpio |
| `app.log` | ✗ NO staged | ⚠️ dirty pero trackeado; NO en commit |
| `routes/__pycache__/articulos.cpython-311.pyc` | ✗ NO staged | ⚠️ dirty pero trackeado; NO en commit |

Solo los 3 archivos Python previstos (`git show --name-only eb59aaf`). `app.log` y el `.pyc` quedaron modificados en el working tree pero NO fueron incluidos en el staging/commit — se doblan al patrón descrito en tasks.md (4.1: "nunca app.log"), por lo que se considera ⚠️ NOTA INFO, NO fallo. Opcional: `git checkout -- app.log routes/__pycache__/articulos.cpython-311.pyc` para dejar el árbol limpio (ambos están trackeados de antes, `.gitignore:2` tiene `__pycache__` pero git no la remueve una vez trackeada).

### Issues Found

**CRITICAL**: None

**WARNING**:
1. **Spec escenario "Recuento de registros" NO satisfecho en exactitud**: `recordsTotal` y `recordsFiltered` devuelven SIEMPRE el mismo valor (cuenta única post-filtro, preexistente en los 4 services + handlers). El spec espera `recordsTotal`=total sin filtro (200) y `recordsFiltered`=12. No es una regresión de este cambio (ni siquiera se tocó el conteo) y no rompe DataTables (las claves son correctas, draw/reproducidas); es una brecha documental del contrato de comportamiento. Decision úsqueda fix mínimo: registrar como follow-up (SCE fuera del alcance del bugfix y sin cambios en tareas/design).

**SUGGESTION**:
1. **BUG LATENTE FUERA DE ALCANCE (verificado)**: `routes/articulos.py:590-626` `api_lst_stock_sucursales` + `services/articulos/stock.py:119` (`obtener_stock_sucursales`) presentan el MISMO bug que este fix corrige: `order_column = request.args.get('order[0][column]', type=int)` sin default (L602) → `order_column+1` con `None` (`None+1`) → `TypeError` → el handler captura y devuelve HTTP 500 `{'error': str(e)}` (L624-626). Además el guard de filtro vacío (L606-612) construye response pero NO `return` → también ejecuta la consulta con `idmarca=None`. **Corregir con el mismo patrón** (default 0 + return) en un cambio nuevo.
2. **Conteo `recordsTotal`/`recordsFiltered`**: implementar conteo separado (query sin filtros para `recordsTotal` y con filtros para `recordsFiltered`) si la UI/counters lo requieren — comportamiento preexistente, dependente de la decisión del usuario (WARNING-1).
3. **Aceptación manual en navegador pendiente**: sin driver E2E, no se renderizó la tabla en browser real; los checks son lógicos sobre el contrato HTTP. Recomendado: una pasada manual a las pestañas Artículos / Precios / Stock / Stock Faltantes (escribir filtros, ordenar, verificar sin alerta "Ocurrió un error").
4. **Limpieza de working tree**: `app.log` y `routes/__pycache__/articulos.cpython-311.pyc` quedaron modificados; unstaged, no es fallo, pero conviene resolver en el próximo fix de rutina (o añadir `app.log` a `.gitignore`).

### Verdict

**PASS**
Implementación exacta del design aprobado: los 4 endpoints responden HTTP 200 con JSON DataTables válido aunque falten `order`/`draw`/`start`/`length`, fallback `'codigo'` sin `TypeError`, guards vacíos retornan `data: []` sin ejecutar la consulta. Suite pytest 49/49 + harness 30/30 PASS. Sin CRITICAL; 1 WARNING (semántica `recordsTotal` preexistente, la especificación), y 1 SUGGESTION clave: el mismo bug latente en `api_lst_stock_sucursales`/`stock.py:119`.