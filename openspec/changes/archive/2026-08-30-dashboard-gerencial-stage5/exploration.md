# Exploration: Dashboard Gerencial — Etapa 5 (Bancos / Caja)

**Date**: 2026-08-30
**Change**: dashboard-gerencial-stage5
**Agent**: SDD Exploration

---

## Executive Summary

Stage 5 adds **Bancos** and **Caja** sections to the Dashboard Gerencial. After thorough exploration:

- **Bancos**: Well-structured data. Table ancos (bank accounts) + ancos_propios (movements) + ipo_mov_bancos (types with C/D flags). Saldo calculable, movimientos del mes factible, ingresos vs egresos straightforward.
- **Caja**: **No dedicated caja or movimientos_caja tables exist.** "Caja" is implemented as a route (/caja in outes/fondos.py) that aggregates sales/purchases by payment type for a given day. endiciones_caja stores cash register closings (end-of-day settlements), not individual movements. This is a **design gap** that requires a decision before proceeding.

---

## 1. Database Schema Analysis

### 1.1 Bancos Tables

#### ancos — Bank accounts
`sql
CREATE TABLE bancos (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  nombre      VARCHAR(50) NOT NULL,      -- Bank name (e.g., "San Juan", "Santander")
  nro_cta     VARCHAR(50) NOT NULL,      -- Account number
  direccion   VARCHAR(50) NOT NULL,
  telefono    VARCHAR(50) NOT NULL,
  email       VARCHAR(50) NOT NULL,
  baja        DATE NOT NULL              -- Soft delete (1900-01-01 = active)
);
`
- **Indexes**: PK on id
- **No index** on aja (used for filtering active records)

#### ipo_mov_bancos — Bank movement types
`sql
CREATE TABLE tipo_mov_bancos (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  nombre          VARCHAR(50) NOT NULL,
  descripcion     VARCHAR(200) NOT NULL,
  tipo_operacion  VARCHAR(1) NOT NULL    -- 'C' = Credit (inflow), 'D' = Debit (outflow)
);
`

**Seed data** (critical for dashboard calculations):

| id | nombre         | tipo_operacion |
|----|----------------|----------------|
| 1  | Cheque         | D              |
| 2  | Deposito       | C              |
| 3  | Transferencia  | D              |
| 4  | Debitos        | D              |
| 5  | Creditos       | C              |
| 6  | Extraccion     | D              |
| 7  | Impuestos      | D              |
| 8  | Cred. IVA      | C              |
| 9  | Otros debitos  | D              |

**Inflows (C)**: Deposito, Creditos, Cred. IVA
**Outflows (D)**: Cheque, Transferencia, Debitos, Extraccion, Impuestos, Otros debitos

#### ancos_propios — Bank movements
`sql
CREATE TABLE bancos_propios (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  fecha_emision     DATE NOT NULL,
  fecha_vencimiento DATE NOT NULL,
  tipo_movimiento   INT NOT NULL,         -- FK -> tipo_mov_bancos.id
  nro_movimiento    VARCHAR(50) NOT NULL,
  monto             DECIMAL(20,6) NOT NULL,
  id_banco          INT NOT NULL,         -- FK -> bancos.id
  baja              DATE NOT NULL         -- Soft delete
);
`
- **Indexes**: ipo_movimiento (FK), id_banco (FK)
- **No index** on echa_emision or aja — potential performance concern for date-range queries
- **Sample data**: 46 rows in production DB (erp-tienda), mostly Cheques (tipo=1)

#### anco_propio_proveedor — Movement-to-supplier link
`sql
CREATE TABLE banco_propio_proveedor (
  id_banco_propio  INT,  -- FK -> bancos_propios.id
  id_proveedor     INT,  -- FK -> proveedores.id
  PRIMARY KEY (id_banco_propio, id_proveedor)
);
`
- Links bank movements to suppliers (used in crear_desde_op from purchase orders)

### 1.2 Caja Tables

#### endiciones_caja — Cash register closings
`sql
CREATE TABLE rendiciones_caja (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  fecha             DATE NOT NULL,
  idusuario         INT NOT NULL,         -- FK -> usuarios.id
  idpunto_vta       INT NOT NULL,         -- FK -> puntos_venta.id
  idsucursal        INT NOT NULL,         -- FK -> sucursales.id
  idtipo_rendicion  INT NOT NULL,         -- FK -> tipo_rendiciones.id
  total_ventas      DECIMAL(20,6) NOT NULL DEFAULT 0,
  total_efectivo    DECIMAL(20,6) NOT NULL DEFAULT 0,
  total_otros_valores DECIMAL(20,6)      -- Added in migration
);
`
- **Indexes**: FK indexes on idusuario, idpunto_vta, idsucursal, idtipo_rendicion
- **No index** on echa — needed for date-range queries

#### items_rendiciones_caja — Denomination breakdown
`sql
CREATE TABLE items_rendiciones_caja (
  id                  INT AUTO_INCREMENT PRIMARY KEY,
  idrendicion         INT NOT NULL,       -- FK -> rendiciones_caja.id
  idmoneda_billete    INT NOT NULL,       -- FK -> monedas_billetes.id
  cantidad            DECIMAL(20,6) NOT NULL
);
`

#### ipo_rendiciones — Rendition types
3 types exist (id 1, 2, 3). Type 3 triggers update_total_rendido_cobrado stored procedure.

#### monedas_billetes — Bills and coins
Denominations with values for cash counting.

### 1.3 What Does NOT Exist

| Concept | Status | Notes |
|---------|--------|-------|
| caja table | **MISSING** | No dedicated cash register entity |
| movimientos_caja table | **MISSING** | No individual cash movement tracking |
| caja chica table | **MISSING** | No petty cash fund concept |
| saldo_caja computed column | **MISSING** | No running balance for cash |
| Index on ancos_propios.fecha_emision | **MISSING** | Needed for date-range queries |
| Index on endiciones_caja.fecha | **MISSING** | Needed for date-range queries |
| Index on ancos_propios.baja | **MISSING** | Used in every query filter |

---

## 2. How Bancos Currently Work

### 2.1 Saldo Calculation

The saldo for a bank account is computed as:

`
saldo = SUM(monto WHERE tipo_operacion = 'C' AND baja = '1900-01-01')
      - SUM(monto WHERE tipo_operacion = 'D' AND baja = '1900-01-01')
`

**SQL approach**:
`sql
SELECT
  b.id,
  b.nombre,
  COALESCE(SUM(CASE WHEN tmb.tipo_operacion = 'C' THEN bp.monto ELSE 0 END), 0) AS total_creditos,
  COALESCE(SUM(CASE WHEN tmb.tipo_operacion = 'D' THEN bp.monto ELSE 0 END), 0) AS total_debitos,
  COALESCE(SUM(CASE
    WHEN tmb.tipo_operacion = 'C' THEN bp.monto
    ELSE -bp.monto
  END), 0) AS saldo
FROM bancos b
JOIN bancos_propios bp ON b.id = bp.id_banco
JOIN tipo_mov_bancos tmb ON bp.tipo_movimiento = tmb.id
WHERE b.baja = '1900-01-01'
  AND bp.baja = '1900-01-01'
GROUP BY b.id, b.nombre
ORDER BY saldo DESC
`

### 2.2 Movimientos del Mes

Count of movements in current month:
`sql
SELECT COUNT(*) AS cantidad_movimientos
FROM bancos_propios bp
WHERE bp.fecha_emision BETWEEN :primer_dia_mes AND :ultimo_dia_mes
  AND bp.baja = '1900-01-01'
`

### 2.3 Ingresos vs Egresos (mes actual)

`sql
SELECT
  COALESCE(SUM(CASE WHEN tmb.tipo_operacion = 'C' THEN bp.monto ELSE 0 END), 0) AS ingresos,
  COALESCE(SUM(CASE WHEN tmb.tipo_operacion = 'D' THEN bp.monto ELSE 0 END), 0) AS egresos
FROM bancos_propios bp
JOIN tipo_mov_bancos tmb ON bp.tipo_movimiento = tmb.id
WHERE bp.fecha_emision BETWEEN :primer_dia_mes AND :ultimo_dia_mes
  AND bp.baja = '1900-01-01'
`

### 2.4 Existing Service Pattern

services/bancos.py uses a class-based service pattern (BancoService, BancoPropioService). The dashboard service uses free functions. We should add free functions to services/dashboard_gerencial.py to maintain consistency.

### 2.5 Existing Route Pattern

outes/bancos.py already has /listado_movs_bancos which shows movements per bank. The dashboard should NOT duplicate this — it should show aggregate KPIs only.

---

## 3. How Caja Currently Works

### 3.1 The /caja Route

The existing /caja route (outes/fondos.py) is a **sales/purchases summary by payment type for a specific day**:

1. User selects a date and optionally a user
2. System queries pagos_fv + pagos_cobros grouped by payment type for sales
3. System queries pagos_fc + pagos_cobros grouped by payment type for purchases
4. Displays as two tables: "Ventas por tipo de cobro" and "Compras por tipo de pago"

This is NOT a traditional cash register with opening/closing balances. It is a **daily payment method breakdown**.

### 3.2 Rendiciones de Caja

endiciones_caja = end-of-day cash register closings where:
- A user counts physical cash and bills
- System compares against recorded sales
- otal_ventas = total sales for the day
- otal_efectivo = physical cash counted
- otal_otros_valores = other payment methods

**This is the closest thing to "arqueo pendiente"** — a rendition that hasn't been done yet for a given day.

### 3.3 What Can Be Derived for Dashboard

| Metric | Source | Feasibility |
|--------|--------|-------------|
| Saldo caja chica | **NOT POSSIBLE** | No caja chica entity |
| Movimientos recientes | pagos_fv + pagos_fc (last N) | Possible but not "caja" concept |
| Arqueo pendiente | endiciones_caja — days without a rendition | Possible via stored procedure |

---

## 4. Design Decision Required

### Option A: Bancos Only (Recommended for Stage 5)

**Scope**: Only bancos section in the dashboard. Skip caja entirely.

**Rationale**:
- Bancos data is well-structured and ready to use
- "Caja" as a concept does not have proper data backing
- The existing /caja route serves a different purpose (payment type breakdown)
- Adding a proper caja system requires new tables, new routes, new business logic — that is a separate feature

**What we would show**:
- Saldo total bancos (aggregate across all accounts)
- Saldo por banco (table: banco, saldo, nro_cta)
- Movimientos del mes (count)
- Ingresos vs Egresos del mes (bar chart or KPI cards)
- Top 10 movimientos recientes (table)

### Option B: Bancos + Caja Derived (Compromise)

**Scope**: Bancos section + a "Caja" section derived from existing data.

**Caja metrics** (derived, not authoritative):
- "Ingresos del dia" from pagos_fv (today's sales payments)
- "Egresos del dia" from pagos_fc (today's purchase payments)
- "Rendiciones pendientes" = days in current month without a endiciones_caja record

**Caveat**: This is NOT a real caja/chica balance. It is payment flow data repurposed.

### Option C: Full Caja System (Separate Feature)

**Scope**: Create proper caja and movimientos_caja tables, then add to dashboard.

**Requires**:
- New migration: caja table (id, nombre, saldo_actual, idsucursal, baja)
- New migration: movimientos_caja table (id, idcaja, fecha, tipo, monto, descripcion, id_usuario, baja)
- Modify sales/purchase payment flows to also write to movimientos_caja
- New service layer for caja CRUD
- Dashboard integration after the above is stable

**Recommendation**: This is a separate SDD change, not Stage 5.

---

## 5. Recommended Approach: Option A + Partial Option B

For Stage 5, implement:

### Section 1: Bancos (Full)
- **KPI Cards** (4 cards):
  1. Saldo Total Bancos — aggregate saldo across all active banks
  2. Movimientos del Mes — count of bancos_propios in current month
  3. Ingresos del Mes — SUM(monto) WHERE tipo_operacion = 'C' in current month
  4. Egresos del Mes — SUM(monto) WHERE tipo_operacion = 'D' in current month

- **Saldo por Banco** (table):
  - Banco, Nro Cuenta, Saldo, Ultimo Movimiento

- **Ingresos vs Egresos** (bar chart):
  - Monthly comparison using Chart.js

- **Top 10 Movimientos Recientes** (table):
  - Fecha, Banco, Tipo, Nro Movimiento, Monto (con badge de ingreso/egreso)

### Section 2: Caja (Lightweight Derived)
- **KPI Cards** (2 cards):
  1. Cobros del Dia — SUM(pagos_fv.total) WHERE fecha = today
  2. Pagos del Dia — SUM(pagos_fc.total) WHERE fecha = today

- **Ultimas Rendiciones** (table):
  - Fecha, Usuario, Sucursal, Total Ventas, Total Efectivo
  - From endiciones_caja (last 10)

---

## 6. Service Functions to Add

### services/dashboard_gerencial.py

`python
# --- 5.1 Saldo Total Bancos ---
def get_bancos_kpis():
    """
    KPIs bancarios: saldo total, movimientos del mes, ingresos y egresos del mes.
    Saldo = SUM(C where tipo_operacion='C') - SUM(monto where tipo='D') for active movements.
    """

# --- 5.2 Saldo por Banco ---
def get_bancos_saldo():
    """
    Saldo desglosado por cada banco activo.
    Retorna lista de dicts con banco, nro_cta, saldo, ultimo_movimiento.
    """

# --- 5.3 Ingresos vs Egresos mensual ---
def get_bancos_ingresos_egresos(desde, hasta):
    """
    Ingresos vs Egresos para el periodo seleccionado.
    Retorna dict con ingresos, egresos, y datos para grafico.
    """

# --- 5.4 Top movimientos recientes ---
def get_bancos_movimientos_recientes(limite=10):
    """
    Ultimos N movimientos bancarios activos.
    """

# --- 5.5 Caja: Cobros y Pagos del dia ---
def get_caja_kpis():
    """
    KPIs de caja derivados: cobros del dia, pagos del dia, balance del dia.
    """

# --- 5.6 Ultimas rendiciones ---
def get_caja_rendiciones(limite=10):
    """
    Ultimas rendiciones de caja.
    """
`

### outes/dashboard_gerencial.py

`python
# New API endpoints:
# GET /api/dashboard-gerencial/bancos-kpis
# GET /api/dashboard-gerencial/bancos-saldo
# GET /api/dashboard-gerencial/bancos-ingresos-egresos
# GET /api/dashboard-gerencial/bancos-movimientos
# GET /api/dashboard-gerencial/caja-kpis
# GET /api/dashboard-gerencial/caja-rendiciones
`

---

## 7. Performance Considerations

### 7.1 Missing Indexes (Recommended)

`sql
-- Critical for bancos_propios date-range queries
ALTER TABLE bancos_propios ADD INDEX idx_bp_fecha_emision (fecha_emision);
ALTER TABLE bancos_propios ADD INDEX idx_bp_baja (baja);

-- Critical for rendiciones_caja date-range queries
ALTER TABLE rendiciones_caja ADD INDEX idx_rc_fecha (fecha);
`

### 7.2 Query Complexity

All proposed queries are simple aggregations with existing FK indexes. Estimated execution time: < 100ms for typical data volumes (46 rows in bancos_propios in production).

### 7.3 No Stored Procedures Needed

Unlike creditos (which uses complex subqueries), bancos queries are straightforward SUM/COUNT with GROUP BY. No stored procedures required.

---

## 8. Template Section Placement

Following the existing pattern, the new sections should be placed AFTER the Credito section (Etapa 4):

`
... existing sections ...
  Credito KPIs (Etapa 4)
  Top Deudores por Credito (Etapa 4)
  === Bancos (Etapa 5) ===          <-- NEW
  Bancos KPIs
  Saldo por Banco
  Ingresos vs Egresos (chart)
  Movimientos Recientes
  === Caja (Etapa 5) ===            <-- NEW
  Caja KPIs
  Ultimas Rendiciones
`

---

## 9. Aggregator Update

get_datos_dashboard() must be extended:

`python
def get_datos_dashboard(desde, hasta, id_sucursal=None, comparar=False):
    return {
        # ... existing sections ...
        'bancos_kpis': get_bancos_kpis(),
        'bancos_saldo': get_bancos_saldo(),
        'bancos_ingresos_egresos': get_bancos_ingresos_egresos(desde, hasta),
        'bancos_movimientos': get_bancos_movimientos_recientes(10),
        'caja_kpis': get_caja_kpis(),
        'caja_rendiciones': get_caja_rendiciones(10),
    }
`

---

## 10. Risks and Open Questions

| Risk | Severity | Mitigation |
|------|----------|------------|
| No movimientos_caja table | HIGH | Use derived metrics from pagos_fv/pagos_fc + rendiciones_caja |
| Missing indexes on echa_emision | MEDIUM | Add indexes in migration before deploying |
| ancos_propios has only ~46 rows in prod | LOW | Not a performance concern at current scale |
| "Caja chica" concept does not exist | HIGH | Document as out of scope; show available data instead |
| otal_otros_valores may be NULL in older rendiciones | LOW | Use COALESCE in queries |

---

## 11. Files to Modify/Create

| File | Action | Description |
|------|--------|-------------|
| services/dashboard_gerencial.py | MODIFY | Add 6 new functions for bancos/caja |
| outes/dashboard_gerencial.py | MODIFY | Add 6 new API endpoints |
| emplates/dashboard-gerencial.html | MODIFY | Add bancos + caja sections |
| static/js/dashboard-gerencial.js | MODIFY | Add chart initialization for ingresos vs egresos |
| static/css/dashboard-gerencial.css | MODIFY | Add badge styles for bancos (ingreso/egreso) |
| openspec/changes/dashboard-gerencial-stage5/spec.md | CREATE | Formal specification |
