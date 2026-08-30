# Design: Dashboard Gerencial — Etapa 5 (Bancos / Caja)

## Technical Approach

Extender el dashboard gerencial con dos nuevas secciones de visibilidad financiera: **Bancos** (saldos, movimientos, ingresos vs egresos) y **Caja** (rendiciones de efectivo). Se siguen exactamente los patrones existentes de services/routes/template de las Etapas 1-4. Sin archivos nuevos — solo modificaciones a 5 archivos existentes.

## Architecture Decisions

### Decision: Saldo bancario calculado desde movimientos (no campo acumulado)

**Choice**: `saldo = SUM(CASE WHEN tipo_operacion='I' THEN monto ELSE -monto END)` sobre toda la historia de `bancos_propios`.

**Alternatives considered**: Agregar campo `saldo_acumulado` a la tabla `bancos`.

**Rationale**: La tabla `bancos_propios` no tiene campo de saldo acumulado. Crear una migración para agregarlo sería overkill para un dashboard read-only. El cálculo desde movimientos es preciso y consistente con la fuente de verdad. Performance aceptable porque `bancos_propios` es una tabla de uso moderado.

### Decision: Bancos NO filtran por sucursal

**Choice**: Los KPIs y detalle de bancos ignoran el filtro de sucursal. Las rendiciones de caja SÍ lo aplican.

**Alternatives considered**: Agregar `idsucursal` a `bancos_propios` (migración de BD).

**Rationale**: `bancos_propios` no tiene columna `idsucursal`. Los movimientos bancarios son globales. Mostrar saldo total consolidado es correcto desde el punto de vista gerencial. Solo las rendiciones de caja se filtran por sucursal (la tabla `rendiciones_caja` sí tiene `idsucursal`).

### Decision: Arqueo de caja fuera de alcance

**Choice**: No implementar arqueo.

**Alternatives considered**: Crear tabla de arqueos.

**Rationale**: No existe tabla dedicada de arqueos en el esquema actual. Agregarla requiere migración + módulo completo. Se documenta como futuro.

## Data Flow

```
MySQL                    Service                     Route              Template
─────                    ───────                     ─────              ────────
bancos                   get_bancos_kpis()           api_bancos_kpis()  KPI cards
  └─ JOIN tipo_mov_bancos                              (GET /api/         (saldo_total,
  └─ JOIN bancos_propios                               dashboard-          movimientos,
                                                       gerencial/         ingresos/egresos)
                                                       bancos-kpis)
bancos_propios ──→ get_bancos_detalle()    ──→ api_bancos_detalle()   ──→  Tabla por banco
  └─ JOIN tipo_mov_bancos                            (GET ...bancos-      (nombre, saldo,
  └─ JOIN bancos                                      detalle)            participacion %)
                                                       │
rendiciones_caja ──→ get_caja_kpis()       ──→ api_caja_kpis()       ──→  KPI cards
  └─ JOIN sucursales                                  (GET ...caja-       (total_efectivo,
                                                      kpis)              rendiciones)
                                                       │
rendiciones_caja ──→ get_caja_rendiciones()──→ api_caja_rendiciones() ──→  Tabla rendiciones
  └─ JOIN sucursales     _recientes()                 (GET ...caja-       (fecha, usuario,
  └─ JOIN usuarios                                   rendiciones)        sucursal, montos)
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `services/dashboard_gerencial.py` | Modify | Agregar 4 funciones al final (antes de `get_datos_dashboard`). Actualizar `get_datos_dashboard` para incluir las 4 nuevas keys |
| `routes/dashboard_gerencial.py` | Modify | Agregar 4 imports + 4 endpoints HTMX + actualizar `dashboard_gerencial()` route |
| `templates/dashboard-gerencial.html` | Modify | Agregar 2 secciones HTML al final (antes del cierre `{% endblock %}`) |
| `static/js/dashboard-gerencial.js` | Modify | Agregar init básico para bancos/caja en `inicializarDashboard()` |
| `static/css/dashboard-gerencial.css` | Modify | Agregar badges para saldo positivo/negativo de bancos |

## Interfaces / Contracts

### Service Functions

```python
# Saldo bancario: histórico (no filtrado por fechas para saldo, sí para movimientos del mes)
def get_bancos_kpis(desde, hasta, id_sucursal=None):
    # Returns: saldo_total_bancos, saldo_total_bancos_raw,
    #          movimientos_mes, ingresos_mes, ingresos_mes_raw,
    #          egresos_mes, egresos_mes_raw

def get_bancos_detalle(desde, hasta, id_sucursal=None):
    # Returns: [{banco, saldo, saldo_raw, movimientos, participacion}, ...]

# Caja: filtrada por sucursal
def get_caja_kpis(desde, hasta, id_sucursal=None):
    # Returns: total_efectivo, total_efectivo_raw,
    #          total_otros_valores, total_otros_valores_raw,
    #          cantidad_rendiciones

def get_caja_rendiciones_recientes(id_sucursal=None, limite=10):
    # Returns: [{fecha, usuario, sucursal, total_ventas, total_efectivo, total_otros_valores}, ...]
```

### HTMX Endpoints

| Endpoint | Service Call | Params |
|----------|-------------|--------|
| `GET /api/dashboard-gerencial/bancos-kpis` | `get_bancos_kpis(desde, hasta)` | desde, hasta (NO id_sucursal) |
| `GET /api/dashboard-gerencial/bancos-detalle` | `get_bancos_detalle(desde, hasta)` | desde, hasta (NO id_sucursal) |
| `GET /api/dashboard-gerencial/caja-kpis` | `get_caja_kpis(desde, hasta, id_sucursal)` | desde, hasta, id_sucursal |
| `GET /api/dashboard-gerencial/caja-rendiciones` | `get_caja_rendiciones_recientes(id_sucursal)` | id_sucursal, limite=10 |

### SQL Patterns

**Bancos KPIs — saldo acumulado + movimientos del mes:**
```sql
-- Saldo acumulado (TODOS los movimientos, no filtrado por fecha)
SELECT
    b.id, b.nombre,
    COALESCE(SUM(CASE WHEN tmb.tipo_operacion = 'I' THEN bp.monto ELSE -bp.monto END), 0) AS saldo
FROM bancos b
LEFT JOIN bancos_propios bp ON b.id = bp.id_banco AND bp.baja = '1900-01-01'
LEFT JOIN tipo_mov_bancos tmb ON bp.tipo_movimiento = tmb.id
WHERE b.baja = '1900-01-01'
GROUP BY b.id, b.nombre
```

**Rendiciones — con joins a sucursal y usuario:**
```sql
SELECT rc.fecha, u.nombre AS usuario, s.nombre AS sucursal,
       rc.total_ventas, rc.total_efectivo, rc.total_otros_valores
FROM rendiciones_caja rc
JOIN usuarios u ON rc.idusuario = u.id
JOIN sucursales s ON rc.idsucursal = s.id
WHERE rc.fecha BETWEEN :desde AND :hasta
    AND s.idsucursal = :id_sucursal  -- si se filtra
ORDER BY rc.fecha DESC
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | 4 funciones de service | Mockear `db.session.execute`, verificar retorno y formato |
| Integration | Endpoints HTMX | Request HTTP a `/api/dashboard-gerencial/bancos-kpis` etc. |
| E2E | Dashboard renderiza | Verificar que las secciones bancos/caja aparecen en el HTML |

## Migration / Rollout

No migration required. Solo se agregan funciones y se modifican archivos existentes. Las secciones nuevas se renderizan al final del dashboard, sin afectar Etapas 1-4.

## Open Questions

- [ ] ¿`rendiciones_caja` tiene datos reales en producción? Si está vacía, las KPIs de caja mostrarán "$ 0,00" y "0 rendiciones" — acceptable.
- [ ] ¿Es correcto que `bancos_propios.baja` se filtre como `'1900-01-01'`? Los modelos lo confirman como default.
