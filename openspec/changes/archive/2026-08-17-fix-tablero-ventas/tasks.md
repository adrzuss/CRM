# Tasks: Fix tablero de ventas — gráficos vacíos por regresión CSP

## Review Workload Forecast

| Campo | Valor |
|-------|-------|
| Líneas estimadas cambiadas | ~100-110 |
| Riesgo presupuesto 400 líneas | Low |
| PR encadenados recomendados | No |
| Split sugerido | PR único |
| Estrategia de entrega | ask-always (ask-on-risk) |
| Estrategia de cadena | pending |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Work Units Sugeridos

| Unidad | Objetivo | PR | Notas |
|--------|----------|----|-------|
| 1 | Restaurar gráficos del tablero gerencial (nonce CSP + código muerto + degradación de reporte) | PR 1 | Un solo commit; verificación manual incluida en la unidad |

## Fase 1: Fix CSP — nonce en scripts inline (`templates/tablero.html`)

- [x] 1.1 L167: `<script>` → `<script nonce="{{ g.nonce }}">` (bloque `mesess`/`eventoss`)
- [x] 1.2 L203: idem (bloque `tipoPagos`/`cantPagos`)
- [x] 1.3 L249: idem (bloque `nombresRubros`/`ventasRubros`)
- [x] 1.4 L263: idem (bloque `nombresRubros`/`cantidadRubros`)

## Fase 2: Limpieza de código muerto (`static/js/demo/chart-bar-demo.js`)

- [x] 2.1 Borrar L120-203 (blanco + bloque `barrasRubros` completo hasta EOF); conservar L1-119 (`myBarChart`, `number_format`, `coloresBarras`)

## Fase 3: Robustez del reporte (`services/ventas/reportes.py`)

- [x] 3.1 `get_vta_rubros` (L275-290): envolver cuerpo en `try:`; `except Exception as e:` → `print('Error calculando ventas por rubros:', str(e))` y devolver `{'rubros': [], 'vtaRubros': [], 'cantRubros': []}` — mismo patrón que `ventas_por_mes` (L241-272)

## Fase 4: Verificación manual (sin runner de tests)

- [ ] 4.1 `/tablero-inicial`: los 3 gráficos muestran datos (barras 6 meses, doughnut ingresos hoy, 2 pies de rubros) — spec "Gráficos con datos bajo CSP"
- [ ] 4.2 Consola limpia: sin "Refused to execute inline script", sin "can't acquire context", sin "length of null" — spec "Carga sin error de consola"
- [ ] 4.3 Degradación (opcional): SP `venta_rubros` roto → HTTP 200 con pies vacíos — spec "Stored procedure de rubros falla"
- [ ] 4.4 Regresión: `/tablero-basico` y `/tablero-gerencial` sin errores nuevos; tarjetas de métricas intactas — spec "Tableros existentes sin regresión"
- [ ] 4.5 Confirmar `/tablero-administrativo`: 500 pre-existente idéntico al pre-fix (no empeora; fuera de alcance)

## Fase 5: Commit (work unit único)

- [x] 5.1 Commit único con los 3 archivos: `fix(tablero): restaurar gráficos del tablero gerencial con nonce CSP` — conventional commit, mensaje en español, sin atribución AI. Rollback: `git revert`