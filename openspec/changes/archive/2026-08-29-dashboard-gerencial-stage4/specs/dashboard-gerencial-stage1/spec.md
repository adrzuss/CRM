# Delta for Dashboard Gerencial Stage 1

## MODIFIED Requirements

### F17: Agregador `get_datos_dashboard()`

The system SHALL extend the aggregator `get_datos_dashboard()` to include creditos section data alongside existing sections.

(Previously: Aggregator returned 12 sections up to `cta_pagar_top`)

The aggregator SHALL add:
- `creditos_kpis`: result of `get_creditos_kpis(id_sucursal)`
- `creditos_top`: result of `get_creditos_top_deudores(limite=10, id_sucursal=id_sucursal)`

#### Scenario: Agregador incluye créditos

- GIVEN `get_datos_dashboard()` called with valid params
- WHEN response is assembled
- THEN returned dict contains keys `creditos_kpis` and `creditos_top`
- AND both keys contain valid data structures

---

## MODIFIED Requirements

### API Spec: `GET /api/dashboard-gerencial/datos`

The `seccion` query parameter SHALL accept new values: `creditos_kpis`, `creditos_top`.

(Previously: seccion enum had 10 values up to `cta_pagar_top`)

#### Scenario: HTMX refresh de sección créditos

- GIVEN dashboard loaded
- WHEN HTMX triggers refresh with `seccion=creditos_kpis`
- THEN response JSON contains `data.creditos_kpis` with active credits, vencidos, morosidad

---

## MODIFIED Requirements

### UI Specification

The layout SHALL place "Créditos" section after "Cuentas por Pagar" / "Top Proveedores".

(Previously: Last section was "Top Proveedores")

The section order becomes: KPIs → Evolución → Sucursales → Rubros → Top Productos → Top Vendedores → Stock KPIs → Stock por Sucursal → Sin Movimiento → Ctas por Cobrar → Top Deudores → Ctas por Pagar → Top Proveedores → **Créditos KPIs → Top Deudores por Crédito**

#### Scenario: Layout con créditos

- GIVEN dashboard completo con Etapas 1+2+3+4
- WHEN se renderiza
- THEN "Créditos" section appears after "Top Proveedores"
- AND 4 KPI cards (activos, vencidos, cartera, morosidad) + tabla top deudores are visible
