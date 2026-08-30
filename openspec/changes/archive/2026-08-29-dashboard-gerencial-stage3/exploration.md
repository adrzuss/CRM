# Exploration: Dashboard Gerencial — Etapa 3 (Cuentas por Cobrar / Por Pagar)

**Date**: 2026-08-29
**Status**: COMPLETE

---

## 1. Table Structures

### cta_cte_cli (Cuentas Corrientes Clientes)

**Model**: `models/ctactecli.py` — class `CtaCteCli`
**Table name**: `cta_cte_cli` (NOT `cta_cte_cliente` as the prompt suggests)

`sql
CREATE TABLE cta_cte_cli (
  id        INT NOT NULL AUTO_INCREMENT,
  idcliente INT NOT NULL,
  fecha     DATE NOT NULL,
  debe      DECIMAL(20,6) DEFAULT NULL,
  haber     DECIMAL(20,6) DEFAULT NULL,
  idcomp    INT DEFAULT NULL,
  PRIMARY KEY (id),
  KEY idcliente (idcliente),
  CONSTRAINT cta_cte_cli_ibfk_1 FOREIGN KEY (idcliente) REFERENCES clientes (id)
);
`

### cta_cte_prov (Cuentas Corrientes Proveedores)

**Model**: `models/ctacteprov.py` — class `CtaCteProv`
**Table name**: `cta_cte_prov` (NOT `cta_cte_proveedor`)

`sql
CREATE TABLE cta_cte_prov (
  id          INT NOT NULL AUTO_INCREMENT,
  idproveedor INT NOT NULL,
  fecha       DATE NOT NULL,
  debe        DECIMAL(20,6) NOT NULL,
  haber       DECIMAL(20,6) NOT NULL,
  idfactura   INT NOT NULL DEFAULT '0',
  PRIMARY KEY (id),
  KEY idproveedor (idproveedor),
  CONSTRAINT cta_cte_prov_ibfk_1 FOREIGN KEY (idproveedor) REFERENCES proveedores (id)
);
`

---

## 2. Saldo Calculation

### Base Formula

`saldo = SUM(debe) - SUM(haber)`

This is the universal pattern used throughout the codebase:

- `services/ctactecli.py` line 40: `saldo_ctacte()` uses `func.sum(CtaCteCli.debe) - func.sum(CtaCteCli.haber)`
- `services/ctacteprov.py` line 7: `saldo_ctacte()` same pattern
- `services/reportes.py` line 620: `saldo = debe - haber`
- Stored procedures `get_saldos_cc_cli` (line 190168) and `get_saldos_cc_prov` (line 190220) both use `SUM(debe) - SUM(haber)`

### Saldo per Entity (grouped)

`sql
SELECT 
  idcliente,
  SUM(debe - haber) AS saldo
FROM cta_cte_cli
GROUP BY idcliente
HAVING saldo > 0
ORDER BY saldo DESC
`

This is exactly the pattern used in:

- `services/reportes.py` line 623-634 (`get_cuentas_corrientes` top deudores)
- `lst_clientes_cc_vencidas` stored procedure (line 192040)

---

## 3. CRITICAL: No vencimiento Field - How Vencido Works

### The Problem

Neither `cta_cte_cli` nor `cta_cte_prov` has a `vencimiento` (due date) field. There is no contractual due date per transaction.

### Existing Approach: MAX(fecha) Per Entity

The existing stored procedures use a **different definition of vencido** than one might expect:

**`get_saldos_cc_cli`** (line 190168):

`sql
-- Gets MAX(fecha) per client
SELECT idcliente, MAX(fecha) AS ultima_fecha 
FROM cta_cte_cli 
GROUP BY idcliente

-- Then filters those where ultima_fecha < CURDATE() - INTERVAL 30 DAY
-- And sums their debe/haber to get saldo_vencido
`

**IMPORTANT BUG/CONVENTION**: The stored procedures read `dias_vto_cta_cte` from `configuracion` table but then HARDCODE `INTERVAL 30 DAY` instead of using the variable. This appears in:

- `get_saldos_cc_cli` line 190206: `WHERE c.ultima_fecha < CURDATE() - INTERVAL 30 DAY`
- `get_saldos_cc_prov` line 190257: `WHERE c.ultima_fecha < CURDATE() - INTERVAL 30 DAY`
- `get_clientes_cc_vencidas` line 190240: `WHERE c.ultima_fecha < CURDATE() - INTERVAL 30 DAY`
- `lst_clientes_cc_vencidas` line 192054: `WHERE d.ultima_fecha < CURDATE() - INTERVAL 30 DAY`

The `dias_vto` variable is fetched but never used in the WHERE clause. This is a known pattern in the existing code.

### Definition of Vencido (for dashboard purposes)

**An entity (client/proveedor) is vencido if its MAX(fecha) is older than N days from today.**

This means: the LAST movement for this entity happened more than N days ago. If a client had their last cta_cte movement 45 days ago and has a positive saldo, they are considered vencido.

This is NOT the same as invoice X is overdue - it is this entity has not had any activity recently and still owes money.

### Recommended Approach for Dashboard

**Use the same convention as the existing stored procedures** but parameterize the days:

`sql
-- Saldo vencido: entities whose last movement is older than :dias_vto days
SELECT SUM(cc.debe), SUM(cc.haber)
FROM cta_cte_cli AS cc
JOIN (
    SELECT idcliente, MAX(fecha) AS ultima_fecha 
    FROM cta_cte_cli 
    GROUP BY idcliente
) c ON c.idcliente = cc.idcliente
WHERE c.ultima_fecha < CURDATE() - INTERVAL :dias_vto DAY
`

**Vencido**: `MAX(fecha) < CURDATE() - INTERVAL N DAY` AND `saldo > 0`
**Por vencer**: `MAX(fecha) >= CURDATE() - INTERVAL N DAY` AND `saldo > 0`

### Alternative Approach (per-movement aging)

A more granular approach would age EACH MOVEMENT individually:

`sql
-- Vencido per movement: debe movement where fecha < cutoff
SELECT idcliente,
  SUM(CASE WHEN fecha < CURDATE() - INTERVAL :dias_vto DAY THEN debe ELSE 0 END) AS debe_vencido,
  SUM(CASE WHEN fecha >= CURDATE() - INTERVAL :dias_vto DAY THEN debe ELSE 0 END) AS debe_por_vencer,
  SUM(haber) AS total_haber
FROM cta_cte_cli
GROUP BY idcliente
`

**RECOMMENDATION**: Use the **per-entity (MAX fecha)** approach for the dashboard. Reasons:

1. The existing stored procedures use MAX(fecha) per entity
2. The existing `lst_clientes_cc_vencidas` uses MAX(fecha) per entity
3. It is simpler and consistent with existing codebase
4. Per-movement aging without FIFO matching is also an approximation (a recent small payment does not necessarily pay off the oldest debt)

---

## 4. Configuration: dias_vto_cta_cte

**Table**: `configuracion`
**Field**: `dias_vto_cta_cte` (SmallInteger, default 0)
**Model**: `models/configs.py` line 41

**How it is used**: Read by stored procedures `get_saldos_cc_cli`, `get_saldos_cc_prov`, `get_clientes_cc_vencidas`, `lst_clientes_cc_vencidas`. All fetch it from `configuracion WHERE id = :empresa` (hardcoded to 1 in the app).

**How it is set**: Via configuration form (`routes/configs.py` line 68: `request.form['dias_vto_cc']`), saved by `services/configs.py` line 26.

**BUG**: The stored procedures fetch `dias_vto` but then hardcode `INTERVAL 30 DAY` in the WHERE clause. The variable is unused.

**For the dashboard**: The `dias_vto_cta_cte` value should be read from `configuracion` and passed as a parameter.

**Recommendation**: Read `dias_vto_cta_cte` from `configuracion` and use it as default. If value is 0, default to 30. Allow the user to override via a UI toggle (30/60/90 days) similar to the sin-movimiento toggle in Stage 2.

---

## 5. Indexes

### Current Indexes

| Table | Index | Columns | Type |
|-------|-------|---------|------|
| cta_cte_cli | PRIMARY | id | PK |
| cta_cte_cli | idcliente | idcliente | FK index |
| cta_cte_prov | PRIMARY | id | PK |
| cta_cte_prov | idproveedor | idproveedor | FK index |

### Missing Indexes (Performance Concern)

The dashboard queries will GROUP BY `idcliente`/`idproveedor` and compute `MAX(fecha)`. The existing FK index on `idcliente` supports this well.

**Recommended additional indexes** for aging queries:

`sql
-- For per-movement aging (fecha-based filtering)
ALTER TABLE cta_cte_cli ADD INDEX idx_cte_cli_fecha (fecha);
ALTER TABLE cta_cte_prov ADD INDEX idx_cte_prov_fecha (fecha);

-- For composite queries (grouping + date filtering)
ALTER TABLE cta_cte_cli ADD INDEX idx_cte_cli_cliente_fecha (idcliente, fecha);
ALTER TABLE cta_cte_prov ADD INDEX idx_cte_prov_proveedor_fecha (idproveedor, fecha);
`

**Impact**: Without these, the aging queries will need full table scans on cta_cte_cli/cta_cte_prov. With the FK index on idcliente, grouping is efficient, but date-based filtering per-group requires scanning all rows per group.

**Mitigation**: The existing data volumes appear small (13 rows in cta_cte_cli, 26 in cta_cte_prov in the dump). But in production, these tables will grow significantly over time.

---

## 6. Existing Code to Reuse

### services/reportes.py - get_cuentas_corrientes() (line 602)

This function already provides:

- Saldo total (debe - haber) for ALL clients
- Top 10 deudores with saldo > 0
- COUNT(DISTINCT idcliente) for clients with debt

**Pattern to follow**:

`python
# Already has the exact SQL we need
sql_top = text("""
    SELECT c.id, c.nombre,
        COALESCE(SUM(ccc.debe - ccc.haber), 0) as saldo
    FROM cta_cte_cli ccc
    JOIN clientes c ON ccc.idcliente = c.id
    GROUP BY c.id, c.nombre
    HAVING saldo > 0
    ORDER BY saldo DESC
    LIMIT 10
""")
`

**Difference for dashboard**: We need DOCUMENTO in the top list. Add `c.documento` to the SELECT and GROUP BY.

### services/ctactecli.py - get_saldo_clientes() (line 53)

Calls stored procedure `get_saldos_cc_cli(:empresa)` returning saldo_actual and saldo_vencido.

### services/ctacteprov.py - getSaldosCtacteProv() (line 28)

Groups by proveedor, returns saldo per provider. Already handles the SUM(debe) - SUM(haber) pattern.

### services/fondos.py - get_saldo_ctas_ctes_cli() (line 128)

Same stored procedure call, returns saldoActual and saldoVencido.

### services/fondos.py - get_saldo_ctas_ctes_prov() (line 138)

Calls `get_saldos_cc_prov(:empresa)`. Note: multiplies by -1 because proveedor saldo is stored inverted (haber - debe convention from the purchase perspective).

### Configuracion model

`python
class Configuracion(db.Model):
    dias_vto_cta_cte = db.Column(db.SmallInteger, nullable=False, default=0)
`

Accessible via `Configuracion.query.get(1)` (empresa always = 1).

---

## 7. Query Design for Dashboard

### 7.1 Cuentas por Cobrar KPIs

**Per-entity approach** (RECOMMENDED - matches existing convention):

`sql
SELECT
    COUNT(DISTINCT CASE WHEN sub.saldo > 0 THEN sub.idcliente END) AS clientes_con_deuda,
    COALESCE(SUM(CASE WHEN sub.saldo > 0 THEN sub.saldo ELSE 0 END), 0) AS saldo_total,
    COALESCE(SUM(CASE WHEN sub.saldo > 0 AND sub.ultima_fecha < CURDATE() - INTERVAL :dias_vto DAY THEN sub.saldo ELSE 0 END), 0) AS saldo_vencido,
    COALESCE(SUM(CASE WHEN sub.saldo > 0 AND sub.ultima_fecha >= CURDATE() - INTERVAL :dias_vto DAY THEN sub.saldo ELSE 0 END), 0) AS saldo_por_vencer
FROM (
    SELECT 
        idcliente, 
        SUM(debe - haber) AS saldo,
        MAX(fecha) AS ultima_fecha
    FROM cta_cte_cli
    GROUP BY idcliente
) sub
`

### 7.2 Top Deudores

`sql
SELECT
    c.id,
    c.nombre,
    c.documento,
    SUM(ccc.debe - ccc.haber) AS saldo,
    MAX(ccc.fecha) AS ultima_fecha
FROM cta_cte_cli ccc
JOIN clientes c ON ccc.idcliente = c.id
GROUP BY c.id, c.nombre, c.documento
HAVING saldo > 0
ORDER BY saldo DESC
LIMIT :limite
`

### 7.3 Cuentas por Pagar KPIs

Same pattern as clientes, substituting `cta_cte_prov` and `proveedores`:

`sql
SELECT
    COUNT(DISTINCT CASE WHEN sub.saldo > 0 THEN sub.idproveedor END) AS proveedores_con_deuda,
    COALESCE(SUM(CASE WHEN sub.saldo > 0 THEN sub.saldo ELSE 0 END), 0) AS saldo_total,
    COALESCE(SUM(CASE WHEN sub.saldo > 0 AND sub.ultima_fecha < CURDATE() - INTERVAL :dias_vto DAY THEN sub.saldo ELSE 0 END), 0) AS saldo_vencido,
    COALESCE(SUM(CASE WHEN sub.saldo > 0 AND sub.ultima_fecha >= CURDATE() - INTERVAL :dias_vto DAY THEN sub.saldo ELSE 0 END), 0) AS saldo_por_vencer
FROM (
    SELECT 
        idproveedor, 
        SUM(debe - haber) AS saldo,
        MAX(fecha) AS ultima_fecha
    FROM cta_cte_prov
    GROUP BY idproveedor
) sub
`

### 7.4 Top Proveedores

`sql
SELECT
    p.id,
    p.nombre,
    p.fantasia,
    SUM(ccc.debe - ccc.haber) AS saldo,
    MAX(ccc.fecha) AS ultima_fecha
FROM cta_cte_prov ccc
JOIN proveedores p ON ccc.idproveedor = p.id
GROUP BY p.id, p.nombre, p.fantasia
HAVING saldo > 0
ORDER BY saldo DESC
LIMIT :limite
`

---

## 8. Data Convention: Vencido Labels

Since there is NO `vencimiento` field and we use `MAX(fecha)` as a proxy, the UI labels should be clear:

| Label | Meaning |
|-------|---------|
| Saldo vencido | Entities whose last movement is older than N days |
| Saldo por vencer | Entities with recent activity and positive saldo |

**Recommendation**: Keep standard accounting terminology (vencido/por vencer) but add the day count as context in the KPI card subtitle. Example: "Saldo vencido (> 30d)"

---

## 9. Sucursal Filter Consideration

**cta_cte tables have NO `idsucursal` field.** There is no direct way to filter by sucursal.

However, we can JOIN through the invoice tables:

- `cta_cte_cli.idcomp` -> `facturav.id` -> `facturav.idsucursal`
- `cta_cte_prov.idfactura` -> `facturac.id` -> `facturac.idsucursal`

**Challenge**: `idcomp` in `cta_cte_cli` is the ID of the invoice OR the receipt (recibo). Not all movements have an invoice - manual adjustments via `addCtaCteCli` route set `idcomp = 0` (default).

**For the dashboard**: **Skip the sucursal filter for cta_cte sections.** Reasons:

1. The cta_cte tables are entity-level (client/provider), not per-sucursal
2. A partial sucursal filter would give misleading results (some movements excluded)
3. The dashboard should show consolidated cta_cte data regardless of sucursal filter
4. If needed later, a `idsucursal` column can be added to cta_cte tables via migration

---

## 10. Service Function Signatures

### New functions for `services/dashboard_gerencial.py`

`python
def get_cta_cobrar_kpis(dias_vto=None):
    """
    KPIs de cuentas por cobrar (clientes).
    Retorna: saldo_total, saldo_vencido, saldo_por_vencer, cantidad_clientes
    dias_vto: dias de vencimiento. Si None, lee de configuracion.
    """

def get_cta_cobrar_top(limite=10):
    """
    Top deudores: clientes con mayor saldo positivo.
    Retorna lista de dicts con: nombre, documento, saldo, ultima_fecha
    """

def get_cta_pagar_kpis(dias_vto=None):
    """
    KPIs de cuentas por pagar (proveedores).
    Retorna: saldo_total, saldo_vencido, saldo_por_vencer, cantidad_proveedores
    """

def get_cta_pagar_top(limite=10):
    """
    Top proveedores: proveedores con mayor saldo positivo.
    Retorna lista de dicts con: nombre, fantasia, saldo, ultima_fecha
    """
`

---

## 11. Route Endpoints Needed

| Route | Method | Purpose |
|-------|--------|---------|
| /api/dashboard-gerencial/cta-cobrar-kpis | GET | Cuentas por cobrar KPIs (optional dias_vto param) |
| /api/dashboard-gerencial/cta-cobrar-top | GET | Top deudores (optional limite param) |
| /api/dashboard-gerencial/cta-pagar-kpis | GET | Cuentas por pagar KPIs (optional dias_vto param) |
| /api/dashboard-gerencial/cta-pagar-top | GET | Top proveedores (optional limite param) |

---

## 12. Template Sections

### SECCION: Cuentas por Cobrar (after stock-sin-movimiento)

`html
<!-- KPIs: 4 cards row -->
<div id="seccion-cta-cobrar-kpis" class="row mb-4">
    <!-- Saldo Total (primary) -->
    <!-- Saldo Vencido (danger) -->
    <!-- Saldo por Vencer (success) -->
    <!-- Clientes con Deuda (warning) -->
</div>

<!-- Top Deudores table -->
<div id="seccion-cta-cobrar-top" class="row mb-4">
    <!-- Full-width table: #, Cliente, Documento, Saldo, Ultimo Mov. -->
</div>
`

### SECCION: Cuentas por Pagar

`html
<!-- KPIs: 4 cards row -->
<div id="seccion-cta-pagar-kpis" class="row mb-4">
    <!-- Saldo Total (primary) -->
    <!-- Saldo Vencido (danger) -->
    <!-- Saldo por Vencer (success) -->
    <!-- Proveedores con Deuda (warning) -->
</div>

<!-- Top Proveedores table -->
<div id="seccion-cta-pagar-top" class="row mb-4">
    <!-- Full-width table: #, Proveedor, Fantasia, Saldo, Ultimo Mov. -->
</div>
`

### KPI Card Colors

| Card | Border Color | Icon |
|------|-------------|------|
| Saldo Total | primary (#4e73df) | fa-dollar-sign |
| Saldo Vencido | danger (#e74a3b) | fa-exclamation-triangle |
| Saldo por Vencer | success (#1cc88a) | fa-clock |
| Clientes/Proveedores con Deuda | warning (#f6c23e) | fa-users |

---

## 13. Updating get_datos_dashboard()

The aggregator function needs to include:

`python
def get_datos_dashboard(desde, hasta, id_sucursal=None, comparar=False):
    return {
        # ... existing Stage 1+2 data ...
        'cta_cobrar_kpis': get_cta_cobrar_kpis(),
        'cta_cobrar_top': get_cta_cobrar_top(10),
        'cta_pagar_kpis': get_cta_pagar_kpis(),
        'cta_pagar_top': get_cta_pagar_top(10),
    }
`

---

## 14. Edge Cases

| Case | Behavior |
|------|----------|
| Sin registros en cta_cte_cli | KPIs = , top deudores vacio |
| Todos los saldos = 0 | KPIs = , no vencido, no por vencer |
| Saldo negativo (haber > debe) | Excluir de top deudores (HAVING saldo > 0). KPIs solo cuentan saldo > 0 |
| dias_vto_cta_cte = 0 en configuracion | Default a 30 dias si el valor es 0 |
| cliente baja = '1900-01-01' (activo) | Incluir en queries (no filtrar por baja en cta_cte) |
| proveedor sin fantasia | Mostrar nombre como fallback |
| Multiple movements same entity | Group by entity, compute saldo as SUM(debe - haber) |
| idcomp = 0 (movimiento manual) | Incluir en calculo - es un movimiento valido |

---

## 15. Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| No vencimiento field - approximation only | Certain | Document as basado en fecha del movimiento, no fecha de vencimiento contractual |
| Stored procedures hardcode 30 dias instead of using dias_vto variable | Certain | Dashboard will read dias_vto from configuracion and use it correctly |
| No sucursal field in cta_cte | Certain | Skip sucursal filter for cta_cte sections; show consolidated data |
| Large cta_cte tables in production | Medium | LIMIT on top queries; consider adding indexes on fecha |
| Saldo negativo distorsion | Medium | Filter saldo > 0 for KPIs and top lists |
| idcomp linking inconsistency | Low | cta_cte_cli uses idcomp (could be invoice OR receipt); cta_cte_prov uses idfactura (always invoice) |
| Join to sucursal via invoice is unreliable | Medium | Skip sucursal filter entirely for Stage 3 |

---

## 16. Recommendations

1. **Use MAX(fecha) per entity** for vencido/por-vencer classification - matches existing convention
2. **Read dias_vto_cta_cte from configuracion** - do NOT hardcode 30 days (fix the bug the stored procedures have)
3. **Default dias_vto to 30** when configuracion value is 0
4. **Skip sucursal filter for cta_cte** - tables have no idsucursal, partial filtering is misleading
5. **Add c.documento to top deudores** - useful for identification
6. **Add p.fantasia to top proveedores** - use fantasia as display name with nombre as fallback
7. **Show ultima_fecha in top lists** - helps user understand vencido context
8. **Add limite param to top functions** - consistent with Stage 1 get_top_productos pattern
9. **Add NOTA**: Document in the UI that vencido is based on last movement date, not contractual due date
10. **Consider adding a dias_vto toggle** to the cta_cte sections (30/60/90 days) - similar to sin-movimiento toggle in Stage 2

---

## 17. Affected Files

| File | Change | Lines Est. |
|------|--------|------------|
| services/dashboard_gerencial.py | Add 4 new functions + update aggregator | ~150 |
| routes/dashboard_gerencial.py | Add 4 API endpoints + imports | ~40 |
| templates/dashboard-gerencial.html | Add 4 new sections (KPIs + tables) | ~180 |
| static/js/dashboard-gerencial.js | Add init for cta_cte sections | ~20 |
| static/css/dashboard-gerencial.css | Add styles for cta_cte badges | ~15 |
