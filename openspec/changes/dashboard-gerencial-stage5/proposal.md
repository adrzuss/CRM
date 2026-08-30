# Proposal: Dashboard Gerencial ERP — Etapa 5 (Bancos / Caja)

## Intent

Extender el dashboard gerencial con una sección de visibilidad financiera: saldos bancarios, movimientos del mes, ingresos vs egresos, estado de caja chica y rendiciones recientes. El usuario gerencial necesita un panorama consolidado de la posición de efectivo y bancos para tomar decisiones de liquidez.

## Scope

### In Scope

- **Bancos — KPIs**: Saldo total bancos (SUM ingresos - SUM egresos de `bancos_propios`), movimientos del mes (COUNT), ingresos vs egresos (SUM separados)
- **Bancos — Tabla por banco**: Desglose de saldo por cada banco activo con participacion %
- **Caja — KPIs**: Total efectivo rendido (`rendiciones_caja.total_efectivo`), total otros valores, cantidad de rendiciones del mes
- **Caja — Rendiciones recientes**: Ultimas 10 rendiciones con fecha, usuario, sucursal, montos
- **Modificacion de archivos existentes**: service, routes, template, JS, CSS (sin archivos nuevos)

### Out of Scope

- Arqueo de caja (no existe tabla dedicada de arqueos en el esquema actual)
- Conciliacion bancaria automatica
- Graficos de tendencia de saldos (solo snapshot actual)
- Historial de movimientos bancarios (solo mes actual + saldo acumulado)
- Alertas de saldo minimo o descubiertos

## Capabilities

### New Capabilities

- `bancos-dashboard`: KPIs y tabla de saldos bancarios, movimientos del mes, ingresos vs egresos
- `caja-dashboard`: KPIs de rendiciones de caja, rendiciones recientes

### Modified Capabilities

- `dashboard-gerencial-stage1`: Se agregan nuevas secciones al dashboard existente (sin modificar comportamiento existente)

## Approach

### Tablas involucradas

| Tabla | Uso |
|-------|-----|
| `bancos` | Bancos activos (baja = '1900-01-01') |
| `tipo_mov_bancos` | Tipo de movimiento con `tipo_operacion` ('I' = ingreso, 'E' = egreso) |
| `bancos_propios` | Movimientos bancarios: monto, fecha_emision, id_banco, tipo_movimiento |
| `rendiciones_caja` | Rendiciones de caja: fecha, total_ventas, total_efectivo, total_otros_valores, idsucursal |
| `sucursales` | Join para nombre de sucursal en rendiciones |

**Regla de saldo**: `saldo = SUM(CASE WHEN tipo_operacion = 'I' THEN monto ELSE -monto END)`

### Service Layer (`services/dashboard_gerencial.py`)

Agregar 4 funciones:

1. `get_bancos_kpis(desde, hasta, id_sucursal=None)` — Query sobre `bancos_propios` JOIN `tipo_mov_bancos`. Retorna:
   - `saldo_total_bancos` / `saldo_total_bancos_raw`
   - `movimientos_mes` (COUNT del periodo)
   - `ingresos_mes` / `ingresos_mes_raw`
   - `egresos_mes` / `egresos_mes_raw`

2. `get_bancos_detalle(desde, hasta, id_sucursal=None)` — GROUP BY banco: nombre, saldo, movimientos, participacion %. Retorna lista de dicts.

3. `get_caja_kpis(desde, hasta, id_sucursal=None)` — Query sobre `rendiciones_caja`. Retorna:
   - `total_efectivo` / `total_efectivo_raw`
   - `total_otros_valores` / `total_otros_valores_raw`
   - `cantidad_rendiciones` (COUNT del periodo)

4. `get_caja_rendiciones_recientes(id_sucursal=None, limite=10)` — Ultimas rendiciones ordenadas por fecha DESC. Retorna lista de dicts con fecha, usuario, sucursal, total_ventas, total_efectivo, total_otros_valores.

Reutilizar `_formato_moneda()`, `_params_base()`, `_sucursal_filter()` existentes.

### Routes (`routes/dashboard_gerencial.py`)

- Agregar imports de las 4 nuevas funciones
- Agregar 4 endpoints HTMX:
  - `GET /api/dashboard-gerencial/bancos-kpis`
  - `GET /api/dashboard-gerencial/bancos-detalle`
  - `GET /api/dashboard-gerencial/caja-kpis`
  - `GET /api/dashboard-gerencial/caja-rendiciones`
- Actualizar `get_datos_dashboard()` para incluir las 4 nuevas secciones

### Template (`templates/dashboard-gerencial.html`)

Agregar despues de la seccion de Creditos:

- **SECCION: Bancos** — 3 KPI cards (saldo total, movimientos del mes, ingresos vs egresos) + tabla por banco
- **SECCION: Caja** — 2 KPI cards (total efectivo, rendiciones del mes) + tabla rendiciones recientes

### JS (`static/js/dashboard-gerencial.js`)

- No se requieren nuevos charts (solo tablas y KPI cards)
- Agregar init basico para secciones bancos/caja en `inicializarDashboard()`

### CSS (`static/css/dashboard-gerencial.css`)

- Agregar estilos para badges de estado de banco (saldo positivo = success, saldo negativo = danger)
- Estilos para indicadores de ingreso/egreso

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `services/dashboard_gerencial.py` | Modified | Agregar 4 funciones: bancos_kpis, bancos_detalle, caja_kpis, caja_rendiciones_recientes |
| `routes/dashboard_gerencial.py` | Modified | Agregar 4 endpoints HTMX + imports |
| `templates/dashboard-gerencial.html` | Modified | Agregar 2 secciones HTML al final del dashboard |
| `static/js/dashboard-gerencial.js` | Modified | Agregar init para secciones bancos/caja |
| `static/css/dashboard-gerencial.css` | Modified | Agregar estilos para badges bancos |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `bancos_propios` no tiene filtro `idsucursal` — movimientos no se pueden filtrar por sucursal | Medium | Mostrar saldo total general; si se filtra sucursal, mostrar solo rendiciones de caja de esa sucursal |
| Tabla `rendiciones_caja` podria estar vacia si no se usan rendiciones | Low | Mostrar "No hay rendiciones" en lugar de $0 |
| Saldo bancario historico: `bancos_propios` no tiene campo de saldo acumulado — se calcula desde movimientos | Medium | Documentar que saldo es acumulado desde todos los movimientos (no solo periodo seleccionado) |
| Breaking stages anteriores | Low | Funciones independientes; solo se extiende `get_datos_dashboard()` |

## Rollback Plan

1. Eliminar las 4 nuevas funciones del service
2. Eliminar los 4 nuevos endpoints del routes
3. Eliminar las 2 secciones HTML del template
4. Eliminar estilos y JS agregados
5. Restaurar `get_datos_dashboard()` original
6. Verificar que Stages 1-4 funcionan correctamente

## Dependencies

- Tablas `bancos`, `tipo_mov_bancos`, `bancos_propios` (ya existentes)
- Tablas `rendiciones_caja`, `sucursales` (ya existentes)
- `_formato_moneda()`, `_params_base()`, `_sucursal_filter()` (reutilizar existentes)
- Modelo `Banco`, `TipoMovBancos`, `BancoPropio` de `models/bancos.py`
- Modelo `RendicionesCaja` de `models/configs.py`

## Success Criteria

- [ ] KPIs bancos muestran saldo total, movimientos del mes, ingresos y egresos
- [ ] Tabla por banco muestra saldo desglosado con participacion %
- [ ] KPIs caja muestran total efectivo y cantidad de rendiciones
- [ ] Tabla rendiciones recientes muestra ultimas 10 con fecha, usuario, sucursal, montos
- [ ] Filtro sucursal aplica a rendiciones de caja (no a bancos, que no tienen idsucursal)
- [ ] Stages 1-4 existentes no se rompen
- [ ] No se inventan datos — si no hay movimientos bancarios, mostrar "No hay movimientos"
- [ ] Decimal se usa para valores monetarios
