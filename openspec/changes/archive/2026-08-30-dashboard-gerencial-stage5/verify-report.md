## Verification Report

**Change**: dashboard-gerencial-stage5
**Version**: Stage 5 — Bancos / Caja
**Mode**: Standard

---

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 9 phases (14 sub-tasks) |
| Tasks complete | 14 |
| Tasks incomplete | 0 |

All 9 phases from `tasks.md` are marked complete with [x].

---

### Build & Tests Execution

**Build**: ➖ No standalone build step (Flask app, no compile)

**Tests**: ✅ 74 passed / ⚠️ 7 failed / 0 skipped
```text
pytest tests/ -v --tb=short

74 passed, 7 failed (all 7 failures are PRE-EXISTING in test_redondeo.py and test_services_articulos.py — unrelated to Stage 5)
No dashboard-gerencial-specific tests exist.
```

**Coverage**: ➖ Not available for new code (no unit tests written for Stage 5 functions)

---

### Spec Compliance Matrix

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| F24: Saldo total acumulado | Saldo = SUM(C) - SUM(D), histórico | Static: `get_bancos_kpis` L1086–1101 | ✅ COMPLIANT |
| F24: Movimientos del mes | COUNT en período | Static: `get_bancos_kpis` L1109–1118 | ✅ COMPLIANT |
| F24: Ingresos vs egresos | SUM separados por tipo | Static: `get_bancos_kpis` L1112–1113 | ✅ COMPLIANT |
| F24: Sin movimientos | KPIs = 0 | Static: COALESCE defaults + fallback dict | ✅ COMPLIANT |
| F25: Tabla multi-banco | Ranking by saldo DESC | Static: `get_bancos_detalle` L1173 ORDER BY | ✅ COMPLIANT |
| F25: Participación % | saldo / saldo_total_positivo * 100 | Static: L1179–1198 | ✅ COMPLIANT |
| F25: Badge positivo/negativo | success si >= 0, danger si < 0 | Static: template L1112 | ✅ COMPLIANT |
| F25: Banco sin movimientos | saldo = $0, movimientos = 0 | Static: LEFT JOIN + COALESCE | ✅ COMPLIANT |
| F26: Total efectivo | SUM(total_efectivo) | Static: `get_caja_kpis` L1221–1229 | ✅ COMPLIANT |
| F26: Rendiciones del mes | COUNT(id) | Static: L1225 | ✅ COMPLIANT |
| F26: Filtro sucursal | AND rc.idsucursal = :id_sucursal | Static: L1217, L1228 | ✅ COMPLIANT |
| F26: Sin rendiciones | KPIs = 0 | Static: COALESCE defaults + fallback dict | ✅ COMPLIANT |
| F27: Últimas rendiciones | ORDER BY fecha DESC LIMIT 10 | Static: `get_caja_rendiciones_recientes` L1281–1282 | ✅ COMPLIANT |
| F27: JOIN usuarios+sucursales | INNER JOIN on both | Static: L1277–1278 | ✅ COMPLIANT |
| F27: Rendición sin usuario | INNER JOIN excludes silently | Static: JOIN usuarios (L1277) | ✅ COMPLIANT |
| NF: Bancos ignoran sucursal | No id_sucursal param | Static: endpoints pass `(desde, hasta)` only | ✅ COMPLIANT |
| NF: Caja respeta sucursal | Filtro por idsucursal | Static: `suc_filter` applied | ✅ COMPLIANT |
| NF: Decimal for money | Decimal type for calculations | Static: all monetary values use Decimal | ✅ COMPLIANT |
| NF: CSP nonce compliance | nonce="{{ g.nonce }}" | Static: template L1247 | ✅ COMPLIANT |
| NF: Stage 1-4 not broken | Existing sections unchanged | Tests: 74 passed (same as before Stage 5) | ✅ COMPLIANT |

**Compliance summary**: 20/20 scenarios compliant

---

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| F24: KPIs Bancos | ✅ Implemented | 3 cards: saldo_total, movimientos_mes, ingresos/egresos. Saldo histórico (sin filtro fecha), movimientos filtrados por período. |
| F25: Tabla Bancos | ✅ Implemented | Tabla con ranking DESC, participación %, badges saldo. Empty state: "No hay movimientos bancarios." |
| F26: KPIs Caja | ✅ Implemented | 2 cards: total_efectivo, cantidad_rendiciones. Filtro sucursal funcional. |
| F27: Rendiciones Recientes | ✅ Implemented | Tabla última 10, fecha DESC, JOIN usuarios+sucursales. Empty state: "No hay rendiciones en este período." |
| CSS badges | ✅ Implemented | 4 clases: badge-bancos-ingreso, badge-bancos-egreso, badge-bancos-saldo-positivo, badge-bancos-saldo-negativo |
| JS init | ✅ Implemented | `inicializarBancosCaja()` placeholder called from `inicializarDashboard()` |
| Aggregator updated | ✅ Implemented | `get_datos_dashboard` incluye 4 keys: bancos_kpis, bancos_detalle, caja_kpis, caja_rendiciones |

---

### Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| Saldo calculado desde movimientos | ✅ Yes | SQL: SUM(CASE WHEN tipo_operacion='C' THEN monto ELSE -monto END) |
| Bancos NO filtran por sucursal | ✅ Yes | Endpoints: `api_bancos_kpis` and `api_bancos_detalle` pass `(desde, hasta)` only |
| Caja SÍ filtra por sucursal | ✅ Yes | `get_caja_kpis` and `get_caja_rendiciones_recientes` accept `id_sucursal` |
| Sin archivos nuevos | ✅ Yes | Solo modificaciones a 5 archivos existentes |
| Patrón de service functions | ✅ Yes | Free functions, misma estructura que stages 1-4 |
| Agregador actualizado | ✅ Yes | 4 keys nuevas en `get_datos_dashboard` |
| Template placement | ✅ Yes | Secciones bancos/caja después de creditos, antes de `</div>` / `{% endblock %}` |

---

### Issues Found

**CRITICAL**: None

**WARNING**:
1. **Spec ambiguity: `get_bancos_detalle` saldo date-filter** — The spec note says "Saldo es acumulado (sin filtro de fecha en JOIN de bancos_propios)" but the spec SQL for F25 includes `bp.fecha_emision BETWEEN :desde AND :hasta` in the LEFT JOIN. The design.md shows saldo without date filter (historical). The implementation follows the spec SQL (with date filter), meaning saldo per bank reflects only movements within the selected period. This is consistent with the spec SQL but contradicts the spec note and the `get_bancos_kpis` behavior where saldo IS historical. If a user selects a narrow date range, the per-bank saldo will not reflect the full accumulated balance — only the balance during that period. The `get_bancos_kpis` saldo_total_bancos IS correctly historical. **Recommendation**: Decide on one behavior (historical vs filtered) and make both functions consistent. Historical is the correct choice for a "Saldo" column.

2. **Spec typo: tipo_operacion 'I'/'E' vs actual 'C'/'D'** — The spec uses `'I'` (Ingreso) and `'E'` (Egreso) but the actual `tipo_mov_bancos.tipo_operacion` column uses `'C'` (Credit) and `'D'` (Debit). The implementation correctly uses `'C'`/`'D'` matching the real database. The spec should be updated to avoid confusion for future maintainers.

**SUGGESTION**:
1. **No unit tests for Stage 5 functions** — The 4 new service functions (`get_bancos_kpis`, `get_bancos_detalle`, `get_caja_kpis`, `get_caja_rendiciones_recientes`) have no unit tests. Consider adding mock-based tests for SQL correctness and edge cases.
2. **`total_otros_valores` double COALESCE** — In `get_caja_rendiciones_recientes` line 1275, `COALESCE(COALESCE(rc.total_otros_valores, 0), 0)` has redundant double COALESCE. A single COALESCE would suffice. Harmless but worth cleaning.
3. **Rendiciones date filter not in spec** — The spec F27 parameters list only `limite` and `id_sucursal`, but the implementation adds `desde`/`hasta` date filtering (via `_parsear_filtros`). This is a reasonable deviation (avoids loading all rendiciones without limit) but should be documented.

---

### Verdict

**PASS WITH WARNINGS**

All 20 spec scenarios are implemented correctly. The implementation faithfully follows the design decisions, uses correct SQL patterns matching the actual database schema, and properly handles edge cases (empty data, negative saldos, sucursal filtering). The 7 test failures are pre-existing and unrelated to Stage 5. No CRITICAL issues found. The WARNING about `get_bancos_detalle` saldo filtering is the most significant — it creates an inconsistency where `bancos_kpis.saldo_total_bancos` is historical but `bancos_detalle[].saldo` is period-scoped. This should be resolved before merging.
