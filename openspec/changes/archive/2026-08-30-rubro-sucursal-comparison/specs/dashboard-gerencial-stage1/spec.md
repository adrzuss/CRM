# Delta for Dashboard Gerencial Stage 1

## MODIFIED Requirements

### F17: Agregador `get_datos_dashboard()`

The system SHALL extend the aggregator `get_datos_dashboard()` to include creditos section data alongside existing sections AND rubro-sucursal comparison data.

The aggregator SHALL add:
- `creditos_kpis`: result of `get_creditos_kpis(id_sucursal)`
- `creditos_top`: result of `get_creditos_top_deudores(limite=10, id_sucursal=id_sucursal)`
- `rubro_sucursal`: result of `get_rubro_sucursal_comparacion(desde, hasta)`

(Previously: Aggregator included creditos section only)

#### Scenario: Agregador incluye créditos y rubro-sucursal

- GIVEN `get_datos_dashboard()` called with valid params
- WHEN response is assembled
- THEN returned dict contains keys `creditos_kpis`, `creditos_top`, and `rubro_sucursal`
- AND all keys contain valid data structures

---

### UI Specification (layout order)

The layout SHALL add a new full-width section "Comparación Rubro × Sucursal" after the existing Sucursales y Rubros cards and before the Top Productos section.

(Previously: Layout ended with Productos sin Movimiento, no cross-tab section)

#### Scenario: Layout con sección cross-tab

- GIVEN dashboard completo
- WHEN se renderiza
- THEN la sección "Comparación Rubro × Sucursal" aparece después de Sucursales/Rubros
- AND antes de Top Productos
