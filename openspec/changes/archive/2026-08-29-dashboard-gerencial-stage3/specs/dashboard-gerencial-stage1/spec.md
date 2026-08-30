# Delta for Dashboard Gerencial ERP — Etapa 1

## ADDED Requirements

### F18: Sección Cuentas por Cobrar en Dashboard

The system SHALL display a "Cuentas por Cobrar" section in the dashboard after the "Productos sin Movimiento" section, containing 3 KPI cards (saldo total, vencido, por vencer) and a badge with the count of clients with debt.

The section SHALL load via HTMX from endpoint `/api/dashboard-gerencial/cta-cobrar-kpis`.

#### Scenario: Sección visible en dashboard

- GIVEN usuario accede al dashboard gerencial
- WHEN se carga la página
- THEN la sección "Cuentas por Cobrar" aparece después de "Productos sin Movimiento"
- AND muestra 3 KPI cards con saldos formateados

---

### F19: Top Deudores en Dashboard

The system SHALL display a "Top Deudores" table after the "Cuentas por Cobrar" KPIs section.

The table SHALL load via HTMX from endpoint `/api/dashboard-gerencial/cta-cobrar-top`.

#### Scenario: Tabla de deudores visible

- GIVEN hay clientes con saldo > 0
- WHEN se carga el dashboard
- THEN la tabla "Top Deudores" muestra filas con #, Cliente, Documento, Saldo
- AND está ordenada por saldo DESC

---

### F20: Sección Cuentas por Pagar en Dashboard

The system SHALL display a "Cuentas por Pagar" section containing 3 KPI cards (saldo total, vencido, por vencer).

The section SHALL load via HTMX from endpoint `/api/dashboard-gerencial/cta-pagar-kpis`.

---

### F21: Top Proveedores en Dashboard

The system SHALL display a "Top Proveedores" table after the "Cuentas por Pagar" KPIs section.

The table SHALL load via HTMX from endpoint `/api/dashboard-gerencial/cta-pagar-top`.

#### Scenario: Tabla de proveedores visible

- GIVEN hay proveedores con saldo > 0
- WHEN se carga el dashboard
- THEN la tabla "Top Proveedores" muestra filas con #, Proveedor, FantasÍa, Saldo
- AND está ordenada por saldo DESC

---

## MODIFIED Requirements

### API Specification (Extendida)

Los endpoints existentes SE MANTIENEN. Se agregan 4 nuevos endpoints HTMX para secciones de cuentas por cobrar/pagar.

(Previously: Solo existían endpoints de KPIs, evolución, sucursales, rubros, top productos, top vendedores, y stock)

#### Scenario: Endpoints cta_cte responden correctamente

- GIVEN dashboard cargado
- WHEN HTMX hace GET a `/api/dashboard-gerencial/cta-cobrar-kpis`
- THEN response JSON contiene `saldo_total`, `saldo_vencido`, `saldo_por_vencer`, `clientes_con_deuda`
- AND status = 200

#### Scenario: Parámetro dias_vencimiento en endpoints

- GIVEN endpoint `/api/dashboard-gerencial/cta-cobrar-kpis?dias_vencimiento=60`
- WHEN se ejecuta la query
- THEN los saldos vencidos/por vencer se calculan con umbral de 60 días

---

### UI Specification (Extendida)

El layout existente SE MANTIENE. Se agregan 4 nuevas secciones al final del dashboard, después de "Productos sin Movimiento".

(Previously: Layout terminaba con top productos y top vendedores)

#### Scenario: Layout con todas las secciones

- GIVEN dashboard completo con Etapas 1+2+3
- WHEN se renderiza
- THEN el orden de secciones es: KPIs → Evolución → Sucursales → Rubros → Top Productos → Top Vendedores → Stock KPIs → Stock por Sucursal → Sin Movimiento → Ctas por Cobrar → Top Deudores → Ctas por Pagar → Top Proveedores

#### Scenario: Badges de saldo vencido/por vencer

- GIVEN sección de cuentas por cobrar con datos
- WHEN se muestra el KPI de saldo vencido
- THEN el badge usa clase CSS `badge-danger`
- AND saldo por vencer usa `badge-success`

---

## Non-Functional Requirements

| Requirement | Specification |
|-------------|--------------|
| **NF12: Sin inventar datos** | Si `cta_cte_cliente` o `cta_cte_prov` están vacías, los widgets muestran "No disponible" en lugar de $0 |
| **NF13: Decimal monetario** | Todos los saldos de cta_cte SHALL usar `Decimal` internamente. Formato visual: `$ 1.250.450,50` |
| **NF14: Multi-sucursal cta_cte** | Queries de cta_cte SHALL respetar filtro `idsucursal` cuando se especifica |
| **NF15: Días vencimiento default** | Default `dias_vencimiento = 30`. Toggle 30/60/90交互 via HTMX |
| **NF16: Performance** | Queries de cta_cte SHALL usar `LIMIT` en top deudores/proveedores (default 10) |
