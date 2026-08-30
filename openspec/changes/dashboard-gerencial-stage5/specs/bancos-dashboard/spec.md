# Bancos Dashboard — Specification (Stage 5)

## Purpose

KPIs y tabla de saldos bancarios en el dashboard gerencial. Saldo = SUM(ingresos) - SUM(egresos) acumulado desde todos los movimientos. Bancos NO filtran por sucursal (tabla `bancos_propios` no tiene `idsucursal`).

---

## Requirements

### F24: KPIs Bancos

The system SHALL compute 3 metrics from `bancos_propios` JOIN `tipo_mov_bancos`:

| KPI | Formula |
|-----|---------|
| Saldo total bancos | `SUM(CASE WHEN tipo_operacion='I' THEN monto ELSE -monto END)` — acumulado de TODOS los movimientos |
| Movimientos del mes | `COUNT(bancos_propios)` en período (desde/hasta) |
| Ingresos vs egresos | SUM separados por `tipo_operacion` ('I'/'E') en período |

**Parámetros**: `desde`, `hasta` (período para movimientos del mes). Saldo total NO se filtra por período — es acumulado.

**Query saldo total** (sin filtro de fecha):
```sql
SELECT COALESCE(SUM(CASE WHEN tmb.tipo_operacion = 'I' THEN bp.monto ELSE -bp.monto END), 0) AS saldo_total
FROM bancos_propios bp
JOIN tipo_mov_bancos tmb ON bp.tipo_movimiento = tmb.id
WHERE bp.baja = '1900-01-01'
```

**Query movimientos del mes** (con filtro de fecha):
```sql
SELECT
  COUNT(bp.id) AS movimientos_mes,
  COALESCE(SUM(CASE WHEN tmb.tipo_operacion = 'I' THEN bp.monto ELSE 0 END), 0) AS ingresos_mes,
  COALESCE(SUM(CASE WHEN tmb.tipo_operacion = 'E' THEN bp.monto ELSE 0 END), 0) AS egresos_mes
FROM bancos_propios bp
JOIN tipo_mov_bancos tmb ON bp.tipo_movimiento = tmb.id
WHERE bp.baja = '1900-01-01'
  AND bp.fecha_emision BETWEEN :desde AND :hasta
```

**Display**: 3 KPI cards — Saldo Total (badge: success si >= 0, danger si < 0), Movimientos del Mes (count), Ingresos vs Egresos (dos sub-valores).

#### Scenario: Saldo total acumulado

- GIVEN banco con 3 movimientos: +$100000 (ingreso), -$30000 (egreso), +$50000 (ingreso)
- WHEN se calcula saldo total
- THEN saldo_total = $120.000,00 (acumulado, sin filtro de período)

#### Scenario: Movimientos del mes con filtro período

- GIVEN período 01/08/2026 - 31/08/2026 con 5 movimientos (3 ingresos, 2 egresos)
- WHEN se consultan movimientos del mes
- THEN movimientos_mes = 5
- AND ingresos_mes = SUM(3 ingresos)
- AND egresos_mes = SUM(2 egresos)

#### Scenario: Sin movimientos bancarios

- GIVEN tabla `bancos_propios` vacía
- WHEN se consultan KPIs
- THEN saldo_total = $0, movimientos_mes = 0, ingresos_mes = $0, egresos_mes = $0
- AND widget muestra "No hay movimientos bancarios"

---

### F25: Tabla Bancos por Banco

The system SHALL return per-bank breakdown with saldo, movimientos del período, and participación %.

**Query**:
```sql
SELECT
  b.nombre AS banco,
  b.id AS id_banco,
  COALESCE(SUM(CASE WHEN tmb.tipo_operacion = 'I' THEN bp.monto ELSE -bp.monto END), 0) AS saldo,
  COUNT(bp.id) AS movimientos
FROM bancos b
LEFT JOIN bancos_propios bp ON b.id = bp.id_banco AND bp.baja = '1900-01-01'
  AND bp.fecha_emision BETWEEN :desde AND :hasta
LEFT JOIN tipo_mov_bancos tmb ON bp.tipo_movimiento = tmb.id
WHERE b.baja = '1900-01-01'
GROUP BY b.id, b.nombre
ORDER BY saldo DESC
```

**Nota**: Saldo es acumulado (sin filtro de fecha en JOIN de bancos_propios). Movimientos son del período.

**Participación %**: `(saldo_banco / saldo_total_positivo) * 100`. Si saldo total = 0, participación = 0%.

**Display**: Tabla con columnas #, Banco, Saldo ($), Movimientos, Participación (%). Badge: success si saldo >= 0, danger si saldo < 0.

#### Scenario: Tabla multi-banco

- GIVEN 3 bancos con saldos: $500000, $200000, -$50000
- WHEN se muestra la tabla
- THEN 3 filas ordenadas por saldo DESC
- AND participaciones: 66.7%, 26.7%, 0% (saldos negativos no contribuyen al total positivo)

#### Scenario: Banco sin movimientos

- GIVEN banco activo sin registros en `bancos_propios`
- WHEN se muestra la tabla
- THEN fila con saldo = $0, movimientos = 0

---

## Edge Cases

| Case | Behavior |
|------|----------|
| Sin movimientos en período | movimientos_mes = 0, ingresos/egresos = $0; saldo total sigue mostrando acumulado |
| Banco con saldo negativo | Badge danger, participación = 0% en tabla |
| Solo un banco activo | Tabla con 1 fila, participación = 100% |
| `bancos_propios` vacía | KPIs = 0, tabla sin filas |
