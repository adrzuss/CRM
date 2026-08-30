# Cuentas por Pagar — Specification

## Purpose

KPIs y ranking de proveedores con saldo adeudado. Clasificación por antigüedad usando `fecha` de `cta_cte_prov` (NO hay campo `vencimiento`). Saldo = SUM(debe) - SUM(haber).

---

## Requirements

### F16: KPIs Cuentas por Pagar

The system SHALL calculate 3 metrics from `cta_cte_prov`: saldo total, saldo vencido, saldo por vencer.

**Query base**:
```sql
SELECT
  COALESCE(SUM(cp.debe - cp.haber), 0) AS saldo_total,
  COALESCE(SUM(CASE WHEN cp.fecha < DATE_SUB(CURDATE(), INTERVAL :dias_vencimiento DAY)
    THEN cp.debe - cp.haber ELSE 0 END), 0) AS saldo_vencido,
  COALESCE(SUM(CASE WHEN cp.fecha >= DATE_SUB(CURDATE(), INTERVAL :dias_vencimiento DAY)
    THEN cp.debe - cp.haber ELSE 0 END), 0) AS saldo_por_vencer
FROM cta_cte_prov cp
WHERE (cp.debe - cp.haber) > 0
  [AND cp.idsucursal = :id_sucursal]
```

**Parámetros**: `dias_vencimiento` (default 30, configurable 30/60/90).

**Display**: 3 KPI cards — Saldo Total (danger), Saldo Vencido (danger), Saldo por Vencer (success).

#### Scenario: Cálculo de saldos proveedores

- GIVEN 2 proveedores con saldos: $15000 (fecha 01/06), $5000 (fecha 01/08)
- WHEN `dias_vencimiento = 30` y fecha actual = 01/08/2026
- THEN saldo_total = $20.000
- AND saldo_vencido = $15.000 (fecha 01/06 < 02/07/2026)
- AND saldo_por_vencer = $5.000 (fecha 01/08 >= 02/07/2026)

#### Scenario: Sin datos en cta_cte_prov

- GIVEN tabla `cta_cte_prov` vacía
- WHEN se consultan KPIs
- THEN saldo_total = $0, saldo_vencido = $0, saldo_por_vencer = $0
- AND el widget muestra "No disponible"

---

### F17: Top Proveedores

The system SHALL return the top N providers ranked by saldo (SUM(debe) - SUM(haber)), filtered to saldo > 0.

**Query**:
```sql
SELECT
  p.id AS idproveedor,
  p.nombre,
  p.fantasia,
  COALESCE(SUM(cp.debe - cp.haber), 0) AS saldo
FROM cta_cte_prov cp
JOIN proveedores p ON cp.idproveedor = p.id
WHERE (cp.debe - cp.haber) > 0
  [AND cp.idsucursal = :id_sucursal]
GROUP BY p.id, p.nombre, p.fantasia
ORDER BY saldo DESC
LIMIT :limite
```

**Display**: Tabla con columnas #, Proveedor, Fantasía, Saldo. Ordenado por saldo DESC.

#### Scenario: Top proveedores ordenamiento

- GIVEN 4 proveedores con saldos $20000, $12000, $8000, $3000
- WHEN se piden top 3
- THEN la tabla muestra 3 filas: $20000, $12000, $8000

#### Scenario: Proveedor sin fantasÍa

- GIVEN proveedor con `fantasia = NULL` o vacío
- WHEN aparece en top proveedores
- THEN la columna fantasÍa muestra el campo `nombre` como fallback

#### Scenario: Sin proveedores con deuda

- GIVEN no hay proveedores con saldo > 0
- WHEN se consulta top proveedores
- THEN retorna lista vacía
- AND el widget muestra "No hay proveedores con deuda"
