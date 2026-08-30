# Proposal: Dashboard Gerencial ERP — Etapa 3 (Cuentas por Cobrar / Por Pagar)

## Intent

Extender el dashboard gerencial (Etapas 1+2) con sección de cuentas por cobrar y por pagar. El usuario necesita visibilidad del saldo de clientes y proveedores, distribución por antigüedad, y ranking de deudores/proveedores principales para gestionar el capital de trabajo.

**Constraint clave**: Las tablas `cta_cte_cliente` y `cta_cte_prov` NO tienen campo `vencimiento`. Se usa `fecha` (fecha de transacción) con umbrales configurables para clasificar saldos por antigüedad. Esto NO es lo mismo que vencimiento contractual — es una aproximación basada en fecha de imputación.

## Scope

### In Scope

- **KPIs Cuentas por Cobrar**: saldo total, saldo vencido (>N días), saldo por vencer, cantidad clientes con deuda
- **KPIs Cuentas por Pagar**: saldo total proveedores, saldo vencido, saldo por vencer
- **Top deudores**: ranking de clientes con mayor saldo (nombre, documento, saldo)
- **Top proveedores**: ranking de proveedores con mayor saldo (nombre, fantasia, saldo)
- **Modificación de archivos existentes**: service, routes, template, JS, CSS

### Out of Scope

- Aging buckets detallados (30/60/90/120 días) — simplificado a vencido/por vencer
- Cobranza o pagos (solo saldos de cta_cte)
- Alertas de cobranza o recordatorios
- Modificación de la sección de filtros globales

## Capabilities

### New Capabilities

- `cta-cobrar`: KPIs y top deudores de cuentas por cobrar
- `cta-pagar`: KPIs y top proveedores de cuentas por pagar

### Modified Capabilities

- `dashboard-gerencial-stage1`: Se agregan nuevas secciones al dashboard existente

## Approach

### Cálculo de Saldos

**Fórmula base**: `saldo = SUM(debe) - SUM(haber)` por entidad (cliente o proveedor).

**Clasificación por antigüedad** (usando campo `fecha` de cta_cte):

| Categoría | Condición |
|-----------|-----------|
| Por vencer | `fecha >= CURDATE() - INTERVAL :dias_vencimiento DAY` |
| Vencido | `fecha < CURDATE() - INTERVAL :dias_vencimiento DAY` |

**Días de vencimiento**: Default 30 días, configurable via parámetro. El usuario puede ajustar (30, 60, 90 días).

### Service Layer (`services/dashboard_gerencial.py`)

Agregar 4 funciones:
1. `get_cta_cobrar_kpis(id_sucursal, dias_vencimiento=30)` — Saldo total, vencido, por vencer, cantidad clientes con deuda
2. `get_cta_cobrar_top(deudas=10, id_sucursal, dias_vencimiento=30)` — Top N deudores con nombre, documento, saldo
3. `get_cta_pagar_kpis(id_sucursal, dias_vencimiento=30)` — Saldo total proveedores, vencido, por vencer
4. `get_cta_pagar_top(proveedores=10, id_sucursal, dias_vencimiento=30)` — Top N proveedores con nombre, fantasia, saldo

Reutilizar `_formato_moneda()`, `_params_base()`, `_sucursal_filter()` existentes.

### Routes (`routes/dashboard_gerencial.py`)

- Agregar imports de las 4 nuevas funciones
- Agregar 4 endpoints HTMX: `/api/dashboard-gerencial/cta-cobrar-kpis`, `/api/dashboard-gerencial/cta-cobrar-top`, `/api/dashboard-gerencial/cta-pagar-kpis`, `/api/dashboard-gerencial/cta-pagar-top`
- Actualizar `get_datos_dashboard()` para incluir las nuevas secciones

### Template (`templates/dashboard-gerencial.html`)

Agregar después de la sección de Productos sin Movimiento:
- **SECCIÓN: Cuentas por Cobrar** — 3 KPI cards (saldo total, vencido, por vencer) + badge cantidad deudores
- **SECCIÓN: Top Deudores** — Tabla con columnas: #, Cliente, Documento, Saldo
- **SECCIÓN: Cuentas por Pagar** — 3 KPI cards (saldo total, vencido, por vencer)
- **SECCIÓN: Top Proveedores** — Tabla con columnas: #, Proveedor, Fantasía, Saldo

### JS (`static/js/dashboard-gerencial.js`)

- Agregar inicialización de las nuevas secciones en `inicializarDashboard()`
- No se requieren nuevos charts (solo tablas y KPI cards)

### CSS (`static/css/dashboard-gerencial.css`)

- Agregar estilos para badges de saldo (vencido = danger, por vencer = success)

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `services/dashboard_gerencial.py` | Modified | Agregar 4 funciones: cta_cobrar_kpis, cta_cobrar_top, cta_pagar_kpis, cta_pagar_top |
| `routes/dashboard_gerencial.py` | Modified | Agregar 4 endpoints HTMX + imports |
| `templates/dashboard-gerencial.html` | Modified | Agregar 4 secciones HTML al final del dashboard |
| `static/js/dashboard-gerencial.js` | Modified | Agregar init para secciones de cta_cte |
| `static/css/dashboard-gerencial.css` | Modified | Agregar estilos para badges de saldo |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Sin campo `vencimiento` en cta_cte — clasificación es aproximada | High | Documentar que usa `fecha` de transacción, no vencimiento contractual. Label como "Saldo > N días" |
| Queries lentas con muchos registros en cta_cte | Medium | LIMIT en top deudores/proveedores; índice en `cta_cte_cliente(idcliente)` |
| Saldos negativos (haber > debe) distorsionan KPIs | Medium | Filtrar entidades con saldo > 0 para KPIs; mostrar saldo neto en top |
| Breaking Stage 1+2 existente | Low | Funciones independientes; solo se extiende `get_datos_dashboard()` |

## Rollback Plan

1. Eliminar las 4 nuevas funciones del service
2. Eliminar los 4 nuevos endpoints del routes
3. Eliminar las 4 secciones HTML del template
4. Eliminar estilos y JS agregados
5. Restaurar `get_datos_dashboard()` original
6. Verificar que Etapas 1+2 funcionan correctamente

## Dependencies

- Tablas `cta_cte_cliente`, `cta_cte_prov` (ya existentes)
- Tablas `clientes`, `proveedores` (ya existentes)
- `_formato_moneda()`, `_params_base()`, `_sucursal_filter()` (reutilizar existentes)
- `get_sucursales_lista()` de `services/reportes.py` (ya importado)

## Success Criteria

- [ ] KPIs de cuentas por cobrar muestran saldo total, vencido, por vencer
- [ ] KPIs de cuentas por pagar muestran saldo total, vencido, por vencer
- [ ] Top deudores lista clientes con mayor saldo (nombre, documento, saldo)
- [ ] Top proveedores lista proveedores con mayor saldo (nombre, fantasia, saldo)
- [ ] Filtro sucursal aplica correctamente a todas las queries
- [ ] Etapas 1+2 existentes no se rompen
- [ ] No se inventan datos — si falta información, se muestra "No disponible"
- [ ] Decimal se usa para valores monetarios
- [ ] Cantidad de clientes con deuda se muestra correctamente
