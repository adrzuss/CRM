# Dashboard Gerencial ERP — Créditos (Etapa 4)

## Purpose

KPIs de cartera de créditos y ranking de deudores por crédito en el dashboard gerencial. Complementa las secciones de cuentas por cobrar/pagar (Etapa 3) con análisis específico del módulo de créditos.

---

## Requirements

### F22: KPIs de Cartera de Créditos

The system SHALL compute 4 metrics from `creditos`, `vencimientos_creditos`, and `pagos_credito`:

| KPI | Formula |
|-----|---------|
| Créditos activos | `COUNT(creditos WHERE estado = 'ACTIVO' AND idsucursal filter)` |
| Créditos vencidos | Count credits with ≥1 installment where `fecha_vencimiento < CURDATE()` and no payment in `pagos_credito` for that installment |
| Monto total cartera | `SUM(creditos.monto)` for active credits |
| % Morosidad | `creditos_vencidos / creditos_activos * 100`. If activos = 0, show 0% |

**Saldo per credit**: `SUM(vencimientos.monto) - SUM(pagos.monto)`. A credit with saldo > 0 has outstanding debt.

**Vencido definition**: An installment (cuota) is vencida when `vencimientos_creditos.fecha_vencimiento < CURDATE()` and no payment exists in `pagos_credito` for that specific `idvencimiento`.

#### Scenario: Morosidad con 10 créditos activos, 3 con cuota vencida

- GIVEN 10 créditos activos, 3 have at least 1 installment with `fecha_vencimiento < CURDATE()` and unpaid
- WHEN KPIs are computed
- THEN creditos_activos = 10, creditos_vencidos = 3, morosidad = 30%

#### Scenario: Sin créditos activos

- GIVEN no active credits in the system
- WHEN KPIs are computed
- THEN all KPIs = 0, morosidad = 0%
- AND section shows "No hay datos de créditos disponibles"

#### Scenario: Filtro multi-sucursal

- GIVEN credits across 2 branches (id_sucursal 1 and 2)
- WHEN `id_sucursal = 1`
- THEN only credits from branch 1 are counted

---

### F23: Top Deudores por Crédito

The system SHALL return top N clients ranked by saldo impago across all their credits.

**Query logic**:
```sql
SELECT c.id, c.nombre, c.documento,
  SUM(v.monto) - COALESCE(p.total_pagos, 0) AS saldo
FROM creditos cr
JOIN clientes c ON cr.idcliente = c.id
JOIN vencimientos_creditos v ON cr.id = v.idcredito
LEFT JOIN (SELECT idcredito, SUM(monto) AS total_pagos
           FROM pagos_credito GROUP BY idcredito) p ON cr.id = p.idcredito
WHERE cr.estado = 'ACTIVO' AND saldo > 0
  [AND cr.idsucursal = :id_sucursal]
GROUP BY c.id, c.nombre, c.documento
ORDER BY saldo DESC
LIMIT :limite
```

**Display**: Table with columns #, Cliente, Documento, Saldo. Ordered by saldo DESC.

#### Scenario: Top deudores ordenamiento

- GIVEN 5 clients with saldos: $50000, $30000, $20000, $10000, $5000
- WHEN top 3 requested
- THEN table shows 3 rows: $50000, $30000, $20000

#### Scenario: Cliente sin documento

- GIVEN client with `documento = NULL`
- WHEN appears in top deudores
- THEN documento column shows "N/D"

#### Scenario: Sin deudores con saldo

- GIVEN no credits with saldo > 0
- WHEN query runs
- THEN returns empty list
- AND section shows "No hay deudores por crédito registrados"

---

## API Specification

### `GET /api/dashboard-gerencial/creditos-kpis`

**Parameters**: `id_sucursal` (optional)

**Response JSON**:
```json
{
  "success": true,
  "data": {
    "creditos_activos": 45,
    "creditos_vencidos": 8,
    "monto_total_cartera": "$ 12.500.000,00",
    "monto_total_cartera_raw": 12500000.00,
    "morosidad": 17.8
  }
}
```

### `GET /api/dashboard-gerencial/creditos-top`

**Parameters**: `limite` (optional, default 10), `id_sucursal` (optional)

**Response JSON**:
```json
{
  "success": true,
  "data": [
    { "nombre": "...", "documento": "...", "saldo": "$ 50.000,00", "saldo_raw": 50000.00 }
  ]
}
```

---

## Edge Cases

| Case | Behavior |
|------|----------|
| No active credits | All KPIs = 0, section "No hay datos de créditos disponibles" |
| All credits fully paid | creditos_vencidos = 0, morosidad = 0% |
| `pagos_credito` empty | All credits show full monto as saldo |
| Client with multiple credits | Aggregated saldo across all credits in top deudores |
| Filtro sucursal = NULL | All branches included |
