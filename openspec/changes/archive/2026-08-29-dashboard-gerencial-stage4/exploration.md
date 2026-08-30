# Exploration: Dashboard Gerencial — Etapa 4 (Créditos)

**Date**: 2026-08-29
**Status**: COMPLETE

---

## 1. Table Structures

### creditos

**Model**: `models/creditos.py` — class `Creditos`
**Table name**: `creditos`

```sql
CREATE TABLE creditos (
  id              INT NOT NULL AUTO_INCREMENT,
  idsucursal      INT NOT NULL DEFAULT 0,
  idcliente       INT NOT NULL,
  idplan          INT NOT NULL,
  cuotas          INT NOT NULL,
  monto_total     DECIMAL(20,6) NOT NULL,
  estado          INT NOT NULL,
  fecha_solicitud DATE NOT NULL,
  fecha_inicio    DATE NOT NULL,
  fecha_fin       DATE NOT NULL,
  idfactura       INT DEFAULT NULL,
  observaciones   VARCHAR(500) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY idcliente (idcliente),
  KEY idplan (idplan),
  KEY estado (estado),
  KEY idfactura (idfactura),
  KEY creditos_ibfk_5 (idsucursal)
);
```

**CRITICAL: No `saldo` field exists.** The saldo must be calculated from `vencimientos_creditos` and `pagos_creditos`.

### vencimientos_creditos

**Model**: `models/creditos.py` — class `VencimientosCreditos`

```sql
CREATE TABLE vencimientos_creditos (
  id                 INT NOT NULL AUTO_INCREMENT,
  idcredito          INT NOT NULL,
  numero_cuota       INT NOT NULL,
  fecha_vencimiento  DATE NOT NULL,
  monto              DECIMAL(20,6) NOT NULL,
  PRIMARY KEY (id),
  KEY idcredito (idcredito)
);
```

Each credit has multiple installment rows. Each row represents one cuota with a due date and amount.

### pagos_creditos

**Model**: `models/creditos.py` — class `PagosCreditos`

```sql
CREATE TABLE pagos_creditos (
  id            INT NOT NULL AUTO_INCREMENT,
  idcredito     INT NOT NULL,
  idvencimiento INT NOT NULL,
  idfactura     INT DEFAULT NULL,
  fecha_pago    DATE NOT NULL,
  monto         DECIMAL(20,6) NOT NULL,
  punitorios    DECIMAL(20,6) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY idcredito (idcredito),
  KEY idvencimiento (idvencimiento),
  KEY idfactura (idfactura)
);
```

Payments are linked to specific vencimientos (installments). A cuota is pagada when there exists a `pagos_creditos` row for that `idvencimiento`.

### estados_creditos

**Model**: `models/creditos.py` — class `EstadosCreditos`

```sql
CREATE TABLE estados_creditos (
  id          INT NOT NULL AUTO_INCREMENT,
  nombre      VARCHAR(50) NOT NULL,
  descripcion VARCHAR(200) NOT NULL,
  PRIMARY KEY (id)
);
```

**State IDs (from code analysis)**:

| ID | Nombre (inferred) | Source |
|----|-------------------|--------|
| 1 | Solicitado | `services/creditos.py` line 328: `estado=1` default |
| 3 | Aprobado | `services/creditos.py` line 488: `estado == 3` |
| 5 | Facturado | `services/ventas/ventas.py` line 307: `credito_obj.estado = 5` |

Other states (2, 4, 6+) likely exist (Rechazado, En evaluacion, etc.) but are not explicitly documented in code. The SQL dump has 0 rows in `estados_creditos` -- states are configured per-installation.

### planes_creditos

**Model**: `models/creditos.py` — class `PlanesCreditos`

| Field | Type | Notes |
|-------|------|-------|
| id | INT PK | |
| nombre | VARCHAR(100) | Plan name |
| descripcion | VARCHAR(500) | |
| tasa_interes | FLOAT | Monthly interest rate |
| cuotas | INT | Number of installments |
| anticipo | BOOLEAN | Whether first payment is down payment |
| garantes | SMALLINT | Required guarantors (default 1) |
| baja | DATE | Soft-delete date |

---

## 2. Saldo Calculation -- THE CORE PROBLEM

The `creditos` table has `monto_total` but NO `saldo` field. The outstanding balance must be computed by joining `vencimientos_creditos` with `pagos_creditos`.

### Formula

```
saldo_credito = SUM(vencimientos.monto) - SUM(COALESCE(pagos.monto, 0))
```

Equivalently, we can compute it per-cuota:

```
-- A cuota is "pendiente" (unpaid) if:
-- vencimientos_creditos.id NOT IN (pagos_creditos.idvencimiento)
-- OR SUM(pagos.monto) < vencimientos.monto (partial payment)
```

### Existing Pattern: get_cant_cuotas_vencidas (line 11727)

The stored procedure already computes unpaid cuotas:

```sql
SELECT COUNT(*) AS cuotas_impagas
FROM (
  SELECT vc.id, vc.monto, COALESCE(SUM(pc.monto), 0.0) AS pagos
  FROM vencimientos_creditos vc
  LEFT OUTER JOIN pagos_creditos pc ON vc.id = pc.idvencimiento
  WHERE fecha_vencimiento < CURDATE()
  GROUP BY vc.id, vc.monto
  HAVING (vc.monto - pagos) > 0
) D;
```

This gives us the pattern: LEFT JOIN pagos, check `(monto - SUM(pagos)) > 0`.

### For Dashboard: Aggregate SQL

```sql
SELECT
  -- Total credits (active, i.e. approved or invoiced)
  COUNT(DISTINCT c.id) AS total_creditos_activos,
  -- Total outstanding amount
  COALESCE(SUM(sub.saldo), 0) AS monto_total_creditos,
  -- Credits with at least one overdue unpaid cuota
  COUNT(DISTINCT CASE WHEN sub.tiene_cuota_vencida = 1 THEN c.id END) AS creditos_vencidos
FROM creditos c
JOIN (
  SELECT
    vc.idcredito,
    SUM(vc.monto) - COALESCE(SUM(pc.monto), 0) AS saldo,
    MAX(CASE WHEN vc.fecha_vencimiento < CURDATE() AND (vc.monto - COALESCE(pc.total_pagado, 0)) > 0
         THEN 1 ELSE 0 END) AS tiene_cuota_vencida
  FROM vencimientos_creditos vc
  LEFT JOIN (
    SELECT idvencimiento, SUM(monto) AS monto
    FROM pagos_creditos
    GROUP BY idvencimiento
  ) pc ON vc.id = pc.idvencimiento
  GROUP BY vc.idcredito
  HAVING saldo > 0
) sub ON c.id = sub.idcredito
WHERE c.estado IN (3, 5)  -- Aprobado o Facturado
  [AND c.idsucursal = :id_sucursal]
```

---

## 3. Vencimiento: How to Determine "vencido" vs "por vencer"

### Key Finding: Two Levels of Vencimiento

**Level 1 -- Per-installment (cuota)**:
A cuota is vencida when `vencimientos_creditos.fecha_vencimiento < CURDATE()` AND the cuota is not fully paid.

This is the natural definition -- each cuota has an explicit `fecha_vencimiento`.

**Level 2 -- Per-credit**:
A credit is vencido when it has AT LEAST ONE cuota vencida (unpaid and past due).

### Existing Logic Confirmation

From `get_cuotas_creditos_vencidas` (line 11803):
```sql
WHERE v.fecha_vencimiento < CURDATE()
  AND pc.id IS NULL  -- No payment recorded
```

From `get_cant_cuotas_vencidas` (line 11727):
```sql
WHERE fecha_vencimiento < CURDATE()
GROUP BY vc.id, vc.monto
HAVING (vc.monto - pagos) > 0
```

Both confirm: **vencido = fecha_vencimiento < CURDATE() AND not fully paid**.

### Dashboard Definition

| Metric | Definition |
|--------|-----------|
| Creditos activos | `estado IN (3, 5)` AND saldo > 0 |
| Creditos vencidos | Creditos activos WITH at least one cuota where `fecha_vencimiento < CURDATE()` AND `monto - pagos > 0` |
| Monto total | SUM(saldo) across all active credits |
| Morosidad % | `(creditos_vencidos / total_creditos_activos) * 100` |
| Top deudores | Active credits ordered by saldo DESC, with client info |

---

## 4. Indexes

### Current Indexes on creditos

| Table | Index | Columns | Type |
|-------|-------|---------|------|
| creditos | PRIMARY | id | PK |
| creditos | idcliente | idcliente | FK index |
| creditos | idplan | idplan | FK index |
| creditos | estado | estado | FK index |
| creditos | idfactura | idfactura | FK index |
| creditos | creditos_ibfk_5 | idsucursal | FK index |

### Current Indexes on vencimientos_creditos

| Table | Index | Columns | Type |
|-------|-------|---------|------|
| vencimientos_creditos | PRIMARY | id | PK |
| vencimientos_creditos | idcredito | idcredito | FK index |

### Current Indexes on pagos_creditos

| Table | Index | Columns | Type |
|-------|-------|---------|------|
| pagos_creditos | PRIMARY | id | PK |
| pagos_creditos | idcredito | idcredito | FK index |
| pagos_creditos | idvencimiento | idvencimiento | FK index |
| pagos_creditos | idfactura | idfactura | FK index |

### Performance Assessment

The FK index on `vencimientos_creditos.idcredito` supports GROUP BY idcredito well.
The FK index on `pagos_creditos.idvencimiento` supports the LEFT JOIN aggregation.

**For dashboard queries, existing indexes are sufficient** assuming moderate data volumes (hundreds to low thousands of credits). The GROUP BY and LEFT JOIN patterns are well-supported.

**Recommended additional index** (optional, for future-proofing):

```sql
-- Composite index for the vencido check query
ALTER TABLE vencimientos_creditos ADD INDEX idx_vto_credito_fecha (idcredito, fecha_vencimiento);
```

---

## 5. How Existing Code Handles Creditos

### services/creditos.py -- Key Functions

| Function | Purpose | Relevance |
|----------|---------|-----------|
| `get_datos_creditos()` (line 517) | Weekly/monthly credit totals for tablero | Already computes total + count for approved/invoiced credits |
| `get_creditos_by_estado()` (line 439) | Credits by state in date range | Uses stored procedure, filters by estado |
| `alerta_creditos_atrasados()` (line 605) | Count of overdue cuotas | Calls `get_cant_cuotas_vencidas()` SP |
| `get_cuotas_pendientes()` (line 563) | Pending cuotas for a client | Filters by `estado = 5` (facturado) |
| `ver_cuotas_creditos_vencidas()` (line 508) | All overdue cuotas with interest | Calls `get_cuotas_creditos_vencidas()` SP |

### Key Patterns to Reuse

1. **Estado filter**: `c.estado IN (3, 5)` -- only approved or invoiced credits are active
2. **Saldo = vencimientos - pagos**: The LEFT JOIN + HAVING pattern from `get_cant_cuotas_vencidas`
3. **Vencido = fecha_vencimiento < CURDATE() AND unpaid**: Consistent across all SPs
4. **Interest calculation**: `interes = monto * (POW(1 + tasa_diaria, dias_mora) - 1)` -- from `configuracion.interes_mora_creditos`

### services/ventas/ventas.py (line 307)

When a credit is invoiced: `credito_obj.estado = 5` (facturado). This confirms that facturado is the active state for credits that have been billed.

---

## 6. Relationship with cta_cte (Stage 3)

**Important distinction**: The `creditos` system is SEPARATE from `cta_cte_cli`.

- `cta_cte_cli`: Tracks all invoice/payment movements per client. Used for general accounts receivable.
- `creditos`: Tracks installment payment plans. A credit is created when a client buys on an installment plan (credito).

**Overlap**: When a credit is facturado (estado=5), an invoice is created in `facturav`, which creates a row in `cta_cte_cli`. But the installment tracking is in `creditos/vencimientos_creditos/pagos_creditos`.

**For the dashboard**: The creditos section should be displayed SEPARATELY from cta_cte sections. They represent different views:
- Cta cobrar: General AR aging (when was last movement)
- Creditos: Installment plan health (which cuotas are overdue)

---

## 7. Query Design for Dashboard

### 7.1 Creditos KPIs

```sql
SELECT
  COUNT(DISTINCT sub.idcredito) AS total_activos,
  COUNT(DISTINCT CASE WHEN sub.tiene_cuota_vencida = 1 THEN sub.idcredito END) AS vencidos,
  COALESCE(SUM(sub.saldo), 0) AS monto_total
FROM (
  SELECT
    c.id AS idcredito,
    SUM(vc.monto) - COALESCE(SUM(pc.total_pagado), 0) AS saldo,
    MAX(CASE
      WHEN vc.fecha_vencimiento < CURDATE()
        AND (vc.monto - COALESCE(pc.total_pagado, 0)) > 0
      THEN 1 ELSE 0
    END) AS tiene_cuota_vencida
  FROM creditos c
  JOIN vencimientos_creditos vc ON vc.idcredito = c.id
  LEFT JOIN (
    SELECT idvencimiento, SUM(monto) AS total_pagado
    FROM pagos_creditos
    GROUP BY idvencimiento
  ) pc ON vc.id = pc.idvencimiento
  WHERE c.estado IN (3, 5)
    [AND c.idsucursal = :id_sucursal]
  GROUP BY c.id
  HAVING saldo > 0
) sub
```

**Morosidad**: Calculated in Python as `(vencidos / total_activos) * 100`.

### 7.2 Top Deudores Creditos

```sql
SELECT
  c.id AS idcredito,
  cli.nombre,
  cli.documento,
  p.nombre AS plan,
  cr.cuotas,
  cr.monto_total,
  sub.saldo,
  sub.cuotas_pagadas,
  sub.cuotas_vencidas,
  sub.proxima_cuota_vto
FROM (
  SELECT
    vc.idcredito,
    SUM(vc.monto) - COALESCE(SUM(pc.total_pagado), 0) AS saldo,
    COUNT(DISTINCT CASE WHEN pc.total_pagado >= vc.monto THEN vc.id END) AS cuotas_pagadas,
    COUNT(DISTINCT CASE
      WHEN vc.fecha_vencimiento < CURDATE()
        AND (vc.monto - COALESCE(pc.total_pagado, 0)) > 0
      THEN vc.id
    END) AS cuotas_vencidas,
    MIN(CASE
      WHEN (vc.monto - COALESCE(pc.total_pagado, 0)) > 0
      THEN vc.fecha_vencimiento
    END) AS proxima_cuota_vto
  FROM vencimientos_creditos vc
  LEFT JOIN (
    SELECT idvencimiento, SUM(monto) AS total_pagado
    FROM pagos_creditos
    GROUP BY idvencimiento
  ) pc ON vc.id = pc.idvencimiento
  GROUP BY vc.idcredito
  HAVING saldo > 0
) sub
JOIN creditos cr ON sub.idcredito = cr.id
JOIN clientes cli ON cr.idcliente = cli.id
JOIN planes_creditos p ON cr.idplan = p.id
WHERE cr.estado IN (3, 5)
  [AND cr.idsucursal = :id_sucursal]
ORDER BY sub.saldo DESC
LIMIT :limite
```

---

## 8. Sucursal Filter

**creditos HAS an `idsucursal` field.** Unlike cta_cte (Stage 3), the sucursal filter works directly:

```sql
WHERE c.idsucursal = :id_sucursal
```

This is simpler and more reliable than the cta_cte approach.

---

## 9. Service Function Signatures

### New functions for `services/dashboard_gerencial.py`

```python
def get_creditos_kpis(id_sucursal=None):
    """
    KPIs de creditos: total_activos, vencidos, monto_total, morosidad.
    Retorna dict con valores formateados y raw.
    """

def get_creditos_top(limite=10, id_sucursal=None):
    """
    Top deudores por credito: cliente, documento, plan, saldo,
    cuotas pagadas, cuotas vencidas, proxima fecha de vencimiento.
    Retorna lista de dicts.
    """
```

---

## 10. Route Endpoints Needed

| Route | Method | Purpose |
|-------|--------|---------|
| /api/dashboard-gerencial/creditos-kpis | GET | Creditos KPIs (optional id_sucursal) |
| /api/dashboard-gerencial/creditos-top | GET | Top deudores by credit (optional limite, id_sucursal) |

---

## 11. Template Sections

### SECCION: Creditos (after Cuentas por Pagar)

```html
<!-- Section header -->
<div class="row mb-2 mt-4">
  <div class="col-12">
    <h6 class="text-uppercase text-muted small font-weight-bold">
      <i class="fas fa-credit-card me-1"></i>Creditos
    </h6>
  </div>
</div>

<!-- KPIs: 4 cards row -->
<div id="seccion-creditos-kpis" class="row mb-4">
  <!-- Total Activos (primary) -->
  <!-- Vencidos (danger) -->
  <!-- Monto Total (info) -->
  <!-- Morosidad % (warning) -->
</div>

<!-- Top Deudores table -->
<div id="seccion-creditos-top" class="row mb-4">
  <!-- Full-width table: #, Cliente, Doc, Plan, Saldo, Cuotas, Vencidas, Prox. Vto -->
</div>
```

### KPI Card Colors

| Card | Border Color | Icon |
|------|-------------|------|
| Total Activos | primary (#4e73df) | fa-credit-card |
| Vencidos | danger (#e74a3b) | fa-exclamation-triangle |
| Monto Total | info (#36b9cc) | fa-dollar-sign |
| Morosidad % | warning (#f6c23e) | fa-chart-line |

---

## 12. Updating get_datos_dashboard()

```python
def get_datos_dashboard(desde, hasta, id_sucursal=None, comparar=False):
    return {
        # ... existing Stage 1+2+3 data ...
        'creditos_kpis': get_creditos_kpis(id_sucursal),
        'creditos_top': get_creditos_top(10, id_sucursal),
    }
```

---

## 13. Edge Cases

| Case | Behavior |
|------|----------|
| Sin creditos en base | KPIs = 0, morosidad = 0%, top vacio |
| Todos los creditos pagados | Saldo = 0, excluir de top deudores |
| Credito con cuotas parciales | LEFT JOIN + SUM handles partial payments |
| Credito recien aprobado sin cuotas generadas | Excluir (no vencimientos = no saldo) |
| estados_creditos sin datos | No credits match estado IN (3,5), KPIs = 0 |
| Credito con estado != 3,5 | Excluir -- only approved/invoiced credits |
| idsucursal filtro | Aplica directo via c.idsucursal |
| Credito con monto_total = 0 | Excluir (HAVING saldo > 0) |
| Cuota vencida pero con pago parcial | (monto - pagos) > 0 -- still vencida |
| Multiple credits same client | Appears multiple times in top (per credit) |

---

## 14. Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| No saldo field -- must compute | Certain | Subquery aggregation, HAVING saldo > 0 |
| Estado IDs may vary per installation | Medium | Query estados_creditos first, or filter dynamically |
| Large vencimientos_creditos table | Low | FK index on idcredito supports GROUP BY |
| Partial payments complicating saldo | Medium | LEFT JOIN with SUM(pagos) handles correctly |
| Creditos overlap with cta_cte confusion | Low | Display as separate section with clear labeling |

---

## 15. Recommendations

1. **Compute saldo from vencimientos - pagos** -- no saldo field exists, aggregation is required
2. **Filter estado IN (3, 5)** -- only approved/invoiced credits are active (confirmed from code)
3. **Use LEFT JOIN on pagos_creditos grouped by idvencimiento** -- handles partial payments correctly
4. **Morosidad = vencidos / activos * 100** -- simple ratio, show as percentage in KPI card
5. **Sucursal filter applies directly** -- creditos has idsucursal, unlike cta_cte
6. **Display AFTER cta_cte sections** -- creditos is a different concept from general AR
7. **Show proxima_cuota_vto in top list** -- actionable info for the user
8. **Show plan name in top list** -- context for the credit type
9. **Consider caching** -- saldo computation is O(n) per credit; for large datasets, consider a nightly materialized saldo column
10. **Label clearly** -- "Creditos" section should explain it shows installment plan health, separate from general accounts receivable

---

## 16. Affected Files

| File | Change | Lines Est. |
|------|--------|------------|
| services/dashboard_gerencial.py | Add 2 new functions + update aggregator | ~120 |
| routes/dashboard_gerencial.py | Add 2 API endpoints + imports | ~25 |
| templates/dashboard-gerencial.html | Add 2 new sections (KPIs + table) | ~120 |
| static/js/dashboard-gerencial.js | Minor: no new JS needed (server-rendered) | ~0 |
| static/css/dashboard-gerencial.css | Add badge styles for creditos | ~15 |
