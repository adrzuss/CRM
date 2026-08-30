# Delta for Dashboard Gerencial ERP — Stage 1

## ADDED Requirements

### F28: Agregador extiende con Bancos y Caja

The system SHALL extend `get_datos_dashboard()` to include bancos and caja sections. No existing behavior is modified.

The aggregator SHALL add:
- `bancos_kpis`: result of `get_bancos_kpis(desde, hasta)`
- `bancos_detalle`: result of `get_bancos_detalle(desde, hasta)`
- `caja_kpis`: result of `get_caja_kpis(desde, hasta, id_sucursal)`
- `caja_rendiciones`: result of `get_caja_rendiciones_recientes(id_sucursal, limite=10)`

#### Scenario: Agregador incluye bancos y caja

- GIVEN `get_datos_dashboard()` called with valid params
- WHEN response is assembled
- THEN returned dict contains keys `bancos_kpis`, `bancos_detalle`, `caja_kpis`, `caja_rendiciones`
- AND all keys contain valid data structures

---

### F29: Sección Bancos en Dashboard

The system SHALL display a "Bancos" section in the dashboard after "Créditos", containing 3 KPI cards (saldo total, movimientos del mes, ingresos vs egresos) and a table per bank with saldo and participación %.

The section SHALL load via HTMX from endpoint `/api/dashboard-gerencial/bancos-kpis` and `/api/dashboard-gerencial/bancos-detalle`.

#### Scenario: Sección visible en dashboard

- GIVEN usuario accede al dashboard gerencial
- WHEN se carga la página
- THEN la sección "Bancos" aparece después de "Créditos"
- AND muestra 3 KPI cards + tabla por banco

---

### F30: Sección Caja en Dashboard

The system SHALL display a "Caja" section in the dashboard after "Bancos", containing 2 KPI cards (total efectivo, rendiciones del mes) and a table of last 10 rendiciones.

The section SHALL load via HTMX from endpoint `/api/dashboard-gerencial/caja-kpis` and `/api/dashboard-gerencial/caja-rendiciones`.

#### Scenario: Sección visible en dashboard

- GIVEN usuario accede al dashboard gerencial
- WHEN se carga la página
- THEN la sección "Caja" aparece después de "Bancos"
- AND muestra 2 KPI cards + tabla rendiciones recientes

---

## Non-Functional Requirements

| Requirement | Specification |
|-------------|--------------|
| NF17: Bancos sin filtro sucursal | Queries de bancos SHALL NO usar filtro `idsucursal` (campo no existe en `bancos_propios`) |
| NF18: Caja con filtro sucursal | Queries de caja SHALL respetar filtro `idsucursal` cuando se especifica |
| NF19: Saldo acumulado bancos | Saldo total bancos SHALL ser acumulado de TODOS los movimientos, sin filtro de período |
| NF20: Decimal monetario | Todos los valores de bancos/caja SHALL usar `Decimal` internamente |
| NF21: Sin datos inventados | Si no hay movimientos bancarios o rendiciones, mostrar "No hay..." en lugar de $0 |

---

## API Specification

### `GET /api/dashboard-gerencial/bancos-kpis`

**Parameters**: `desde`, `hasta`

**Response JSON**:
```json
{
  "success": true,
  "data": {
    "saldo_total_bancos": "$ 1.250.000,00",
    "saldo_total_bancos_raw": 1250000.00,
    "movimientos_mes": 45,
    "ingresos_mes": "$ 800.000,00",
    "ingresos_mes_raw": 800000.00,
    "egresos_mes": "$ 350.000,00",
    "egresos_mes_raw": 350000.00
  }
}
```

### `GET /api/dashboard-gerencial/bancos-detalle`

**Parameters**: `desde`, `hasta`

**Response JSON**:
```json
{
  "success": true,
  "data": [
    {
      "banco": "Banco Nación",
      "id_banco": 1,
      "saldo": "$ 500.000,00",
      "saldo_raw": 500000.00,
      "movimientos": 20,
      "participacion": 40.0
    }
  ]
}
```

### `GET /api/dashboard-gerencial/caja-kpis`

**Parameters**: `desde`, `hasta`, `id_sucursal` (optional)

**Response JSON**:
```json
{
  "success": true,
  "data": {
    "total_efectivo": "$ 250.000,00",
    "total_efectivo_raw": 250000.00,
    "total_otros_valores": "$ 80.000,00",
    "total_otros_valores_raw": 80000.00,
    "cantidad_rendiciones": 12
  }
}
```

### `GET /api/dashboard-gerencial/caja-rendiciones`

**Parameters**: `limite` (optional, default 10), `id_sucursal` (optional)

**Response JSON**:
```json
{
  "success": true,
  "data": [
    {
      "fecha": "15/08/2026",
      "usuario": "Juan Pérez",
      "sucursal": "Central",
      "total_ventas": "$ 45.000,00",
      "total_efectivo": "$ 35.000,00",
      "total_otros_valores": "$ 10.000,00"
    }
  ]
}
```

---

## Edge Cases

| Case | Behavior |
|------|----------|
| Orden secciones dashboard | KPIs → Evolución → Sucursales → Rubros → Top Productos → Top Vendedores → Stock → Ctas por Cobrar → Ctas por Pagar → Créditos → **Bancos** → **Caja** |
| Bancos sin movimientos | saldo_total = $0, tabla vacía, "No hay movimientos bancarios" |
| Caja sin rendiciones | total_efectivo = $0, tabla "No hay rendiciones recientes" |
| Filtro sucursal en bancos | Ignorado — bancos muestran saldo total general |
| Filtro sucursal en caja | Aplica — solo rendiciones de esa sucursal |
