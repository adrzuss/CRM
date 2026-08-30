# Dashboard Alertas Gerenciales — Specification (Stage 6)

## Purpose

Panel de alertas críticas en el dashboard gerencial que señala automáticamente problemas operativos. Deriva de funciones existentes (sin queries nuevas). Se muestra al inicio del dashboard, después de filtros.

---

## Requirements

### F31: Panel de Alertas Gerenciales

The system SHALL display a collapsible alerts panel at the top of the dashboard (after filters, before KPIs) showing critical conditions detected from existing data. The panel SHALL be hidden when zero alerts exist.

**Alert types**:

| Alert | Source Function | Trigger Condition | Severity |
|-------|----------------|-------------------|----------|
| Stock bajo mínimo | `get_stock_kpis(id_sucursal)` | `bajo_minimo > 0` | warning |
| Sin stock | `get_stock_kpis(id_sucursal)` | `sin_stock > 0` | danger |
| Créditos vencidos | `get_creditos_kpis(id_sucursal)` | `creditos_vencidos > 0` | danger |
| Cta_cte vencida | `get_cta_cobrar_kpis(dias_vto)` | `saldo_vencido > 0` | danger |
| Banco saldo negativo | `get_bancos_detalle()` | any `saldo_raw < 0` | danger |

**Data source**: `get_datos_dashboard()` SHALL add `alertas` key — a list of alert objects. Each alert reuses data already computed by the aggregator (no additional queries).

#### Scenario: 3 alertas activas

- GIVEN stock bajo_minimo = 5, creditos_vencidos = 3, saldo_vencido_ctacte = $50000
- WHEN se carga el dashboard
- THEN panel muestra 3 alert cards con severidad, icono, y conteo/valor
- AND panel está expandido por defecto

#### Scenario: Sin alertas

- GIVEN bajo_minimo = 0, sin_stock = 0, creditos_vencidos = 0, saldo_vencido = 0, bancos todos saldo >= 0
- WHEN se carga el dashboard
- THEN panel `#seccion-alertas` NO se renderiza en el DOM
- AND no hay espacio reservado

#### Scenario: Banco con saldo negativo

- GIVEN 3 bancos, uno con saldo_raw = -$25000
- WHEN se evalúan alertas
- THEN alerta "Banco saldo negativo" aparece con valor "$ 25.000,00"
- AND el nombre del banco se incluye en el detalle

---

### F32: API Endpoint Alertas

The system SHALL expose `GET /api/dashboard-gerencial/alertas` returning alertas JSON for HTMX refresh.

**Parameters**: same as main dashboard (`desde`, `hasta`, `id_sucursal`).

**Response JSON**:
```json
{
  "success": true,
  "data": {
    "alertas": [
      { "tipo": "stock_bajo", "titulo": "Stock Bajo Mínimo", "detalle": "42 artículos por debajo del mínimo", " severidad": "warning", "icono": "fa-box-open", "count": 42 }
    ],
    "total": 1
  }
}
```

#### Scenario: Refresh HTMX de alertas

- GIVEN dashboard cargado
- WHEN HTMX hace GET a `/api/dashboard-gerencial/alertas`
- THEN response contiene lista `alertas` con objetos tipo/titulo/detalle/severidad/icono
- AND status = 200

---

## Edge Cases

| Case | Behavior |
|------|----------|
| Sin datos de stock | No alerta stock — `sin_stock=0, bajo_minimo=0` |
| `get_datos_dashboard()` falla | Alertas = lista vacía, panel oculto |
| Banco con saldo = 0 exacto | No alerta (condición estricta: `< 0`) |
| Múltiples bancos negativos | Una alerta por banco, cada una con su nombre |

---

## Non-Functional Requirements

| Requirement | Specification |
|-------------|--------------|
| **NF22: Sin queries nuevas** | Alertas SHALL reutilizar funciones existentes ya llamadas por `get_datos_dashboard()` |
| **NF23: Performance** | `get_alertas_gerenciales()` SHALL ejecutarse en < 100ms (datos ya en memoria del agregador) |
| **NF24: Sin datos inventados** | Alertas SHALL mostrarse solo cuando condiciones reales se cumplen |
