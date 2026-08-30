# Cuentas por Cobrar — Specification

## Purpose

KPIs y ranking de clientes con saldo adeudado. Clasificación por antigüedad usando `fecha` de `cta_cte_cliente` (NO hay campo `vencimiento`). Saldo = SUM(debe) - SUM(haber).

---

## Requirements

### F14: KPIs Cuentas por Cobrar

The system SHALL calculate 4 metrics from `cta_cte_cliente`: saldo total, saldo vencido, saldo por vencer, cantidad de clientes con deuda.

**Query base**:
```sql
SELECT
  COALESCE(SUM(cc.debe - cc.haber), 0) AS saldo_total,
  COALESCE(SUM(CASE WHEN cc.fecha < DATE_SUB(CURDATE(), INTERVAL :dias_vencimiento DAY)
    THEN cc.debe - cc.haber ELSE 0 END), 0) AS saldo_vencido,
  COALESCE(SUM(CASE WHEN cc.fecha >= DATE_SUB(CURDATE(), INTERVAL :dias_vencimiento DAY)
    THEN cc.debe - cc.haber ELSE 0 END), 0) AS saldo_por_vencer,
  COUNT(DISTINCT CASE WHEN (cc.debe - cc.haber) > 0 THEN cc.idcliente END) AS clientes_con_deuda
FROM cta_cte_cliente cc
WHERE (cc.debe - cc.haber) > 0
  [AND cc.idsucursal = :id_sucursal]
```

**Parámetros**: `dias_vencimiento` (default 30, configurable 30/60/90).

**Display**: 3 KPI cards — Saldo Total (danger), Saldo Vencido (danger), Saldo por Vencer (success). Badge con cantidad de deudores.

#### Scenario: Cálculo de saldos

- GIVEN 3 clientes con saldos: $5000 (fecha 01/07), $3000 (fecha 15/07), $2000 (fecha 01/08)
- WHEN `dias_vencimiento = 30` y fecha actual = 01/08/2026
- THEN saldo_total = $10.000
- AND saldo_vencido = $5.000 (fecha 01/07 < 01/07/2026)
- AND saldo_por_vencer = $5.000 (fechas 15/07 y 01/08 >= 02/07/2026)
- AND clientes_con_deuda = 3

#### Scenario: Sin datos en cta_cte_cliente

- GIVEN tabla `cta_cte_cliente` vacía
- WHEN se consultan KPIs
- THEN saldo_total = $0, saldo_vencido = $0, saldo_por_vencer = $0
- AND clientes_con_deuda = 0
- AND el widget muestra "No disponible"

#### Scenario: Filtrado por sucursal

- GIVEN 2 sucursales con saldos $8000 y $2000
- WHEN `id_sucursal = 1`
- THEN saldo_total = $8.000
- AND no incluye saldos de sucursal 2

---

### F15: Top Deudores

The system SHALL return the top N clients ranked by saldo (SUM(debe) - SUM(haber)), filtered to saldo > 0.

**Query**:
```sql
SELECT
  c.id AS idcliente,
  c.nombre,
  c.documento,
  COALESCE(SUM(cc.debe - cc.haber), 0) AS saldo
FROM cta_cte_cliente cc
JOIN clientes c ON cc.idcliente = c.id
WHERE (cc.debe - cc.haber) > 0
  [AND cc.idsucursal = :id_sucursal]
GROUP BY c.id, c.nombre, c.documento
ORDER BY saldo DESC
LIMIT :limite
```

**Display**: Tabla con columnas #, Cliente, Documento, Saldo. Ordenado por saldo DESC.

#### Scenario: Top deudores ordenamiento

- GIVEN 5 clientes con saldos $10000, $8000, $5000, $3000, $1000
- WHEN se piden top 3
- THEN la tabla muestra 3 filas ordenadas: $10000, $8000, $5000

#### Scenario: Cliente sin documento

- GIVEN cliente con `documento = NULL` o vacío
- WHEN aparece en top deudores
- THEN la columna documento muestra "N/D"

#### Scenario: Sin deudores

- GIVEN no hay clientes con saldo > 0
- WHEN se consulta top deudores
- THEN retorna lista vacía
- AND el widget muestra "No hay deudores registrados"
