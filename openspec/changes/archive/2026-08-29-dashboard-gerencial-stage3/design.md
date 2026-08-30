# Design: Dashboard Gerencial ERP — Etapa 3 (Cuentas por Cobrar / Por Pagar)

## Technical Approach

Extender el dashboard existente (Etapas 1+2) con 4 funciones de servicio, 4 endpoints HTMX y 6 secciones de template para cuentas por cobrar y por pagar. Reutiliza `_formato_moneda()` y patrones de error existentes. Las queries usan `fecha` de cta_cte (no vencimiento contractual) con umbrales configurables para clasificar saldos.

## Architecture Decisions

### Decision: Clasificación por antigüedad usando `fecha` de cta_cte

| Opción | Tradeoff | Decisión |
|--------|----------|----------|
| `fecha` + interval configurable | Aproximación basada en fecha de imputación, no vencimiento contractual | **Elegida** — la tabla no tiene campo `vencimiento`; es la única opción viable |
| Agregar campo `vencimiento` a cta_cte | Requiere migración, datos históricos incompletos | Descartada — fuera de scope, alto riesgo |
| Usar `fecha_emision` de facturav/facturac | Más preciso pero cta_cte puede existir sin factura | Descartada — la fecha de cta_cte es la fuente de saldo |

**Rationale**: La columna `fecha` de cta_cte representa cuándo se imputó el movimiento. Es la fecha más confiable para determinar antigüedad del saldo. El label UI dirá "Saldo > N días" para dejar claro que no es vencimiento contractual.

### Decision: Multi-sucursal via LEFT JOIN con facturav/facturac

| Opción | Tradeoff | Decisión |
|--------|----------|----------|
| LEFT JOIN facturav/facturac para `idsucursal` | Puede omitir cta_cte sin factura asociada | **Elegida** — cobertura >99%, simple |
| Subquery con UNION de todas las tablas con idsucursal | Complejidad alta, rendimiento peor | Descartada — innecesaria |
| Agregar `idsucursal` a cta_cte | Requiere migración | Descartada — fuera de scope |

**Rationale**: `cta_cte_cli.idcomp` → `facturav.id` (ventas) y `cta_cte_prov.idfactura` → `facturac.id` (compras). LEFT JOIN asegura que registros sin factura aparezcan como "Sin sucursal". En la práctica, prácticamente toda cta_cte tiene factura asociada.

### Decision: Posición en el template

| Ubicación | Tradeoff | Decisión |
|-----------|----------|----------|
| Después de Stock, antes de créditos | Agrupa KPIs financieros juntos; lógica visual: ventas → stock → cobros/pagos | **Elegida** |
| Al final del dashboard | Separa contenido financiero | Descartada — fragmenta la experiencia |

### Decision: KPIs para saldos netos negativos

| Opción | Tradeoff | Decisión |
|--------|----------|----------|
| Filtrar `HAVING saldo > 0` para KPIs de suma | KPIs muestran deuda real; clientes con saldo a favor no contaminan | **Elegida** |
| Incluir todos los saldos (positivos y negativos) | Más "real" pero confunde: un cliente con $100K a favor y otro con $50K deuda = $50K total | Descartada |

**Rationale**: Los KPIs miden exposición de capital. Un saldo negativo (cliente nos debe) no cancela otro saldo positivo (nosotros le debemos) en reporting gerencial.

## Data Flow

```
MySQL cta_cte_cli ──→ LEFT JOIN facturav ──→ get_cta_cobrar_kpis()  ──→ Route ──→ Template KPIs
                     LEFT JOIN clientes                          │
                                                                 └──→ get_cta_cobrar_top()  ──→ Route ──→ Template Tabla

MySQL cta_cte_prov ──→ LEFT JOIN facturac ──→ get_cta_pagar_kpis()   ──→ Route ──→ Template KPIs
                     LEFT JOIN proveedores                        │
                                                                 └──→ get_cta_pagar_top()   ──→ Route ──→ Template Tabla
```

## File Changes

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `services/dashboard_gerencial.py` | Modificar | +4 funciones: `get_cta_cobrar_kpis`, `get_cta_cobrar_top`, `get_cta_pagar_kpis`, `get_cta_pagar_top`. Actualizar `get_datos_dashboard()` |
| `routes/dashboard_gerencial.py` | Modificar | +4 imports, +4 endpoints HTMX, parsear `dias_vencimiento` en `_parsear_filtros()` |
| `templates/dashboard-gerencial.html` | Modificar | +6 secciones HTML después de "Productos sin Movimiento": 4 KPI cards + 2 tablas |
| `static/js/dashboard-gerencial.js` | Modificar | +init para secciones cta_cte en `inicializarDashboard()`, sin nuevos charts |
| `static/css/dashboard-gerencial.css` | Modificar | +badges de saldo (`.badge-cta-vencido`, `.badge-cta-por-vencer`) |

## Interfaces / Contracts

### Service — get_cta_cobrar_kpis

```python
def get_cta_cobrar_kpis(id_sucursal=None, dias_vencimiento=30):
    """
    KPIs cuentas por cobrar: saldo_total, saldo_vencido, saldo_por_vencer,
    cantidad_deudores.
    Saldo = SUM(debe) - SUM(haber) por cliente, filtrado saldo > 0.
    Vencido: fecha < CURDATE() - dias_vencimiento.
    Retorna dict con valores formateados y raw.
    """
```

### Service — get_cta_cobrar_top

```python
def get_cta_cobrar_top(limite=10, id_sucursal=None, dias_vencimiento=30):
    """
    Top N deudores: nombre, documento, saldo.
    Ordena por saldo DESC.
    Retorna lista de dicts.
    """
```

### Service — get_cta_pagar_kpis

```python
def get_cta_pagar_kpis(id_sucursal=None, dias_vencimiento=30):
    """
    KPIs cuentas por pagar: saldo_total, saldo_vencido, saldo_por_vencer,
    cantidad_proveedores.
    Misma lógica que cta_cobrar pero con cta_cte_prov/facturac/proveedores.
    Retorna dict con valores formateados y raw.
    """
```

### Service — get_cta_pagar_top

```python
def get_cta_pagar_top(limite=10, id_sucursal=None, dias_vencimiento=30):
    """
    Top N proveedores: nombre, fantasia, saldo.
    Ordena por saldo DESC.
    Retorna lista de dicts.
    """
```

### Endpoint patterns (HTMX)

```
GET /api/dashboard-gerencial/cta-cobrar-kpis?id_sucursal=&dias_vencimiento=30
GET /api/dashboard-gerencial/cta-cobrar-top?limite=10&id_sucursal=&dias_vencimiento=30
GET /api/dashboard-gerencial/cta-pagar-kpis?id_sucursal=&dias_vencimiento=30
GET /api/dashboard-gerencial/cta-pagar-top?limite=10&id_sucursal=&dias_vencimiento=30
```

### Query pattern (ejemplo cta_cobrar_kpis)

```sql
SELECT
    COALESCE(SUM(saldo), 0) AS saldo_total,
    COALESCE(SUM(CASE WHEN fecha < CURDATE() - INTERVAL :dias DAY THEN saldo END), 0) AS saldo_vencido,
    COALESCE(SUM(CASE WHEN fecha >= CURDATE() - INTERVAL :dias DAY THEN saldo END), 0) AS saldo_por_vencer,
    COUNT(*) AS cantidad_deudores
FROM (
    SELECT
        cc.idcliente,
        cc.fecha,
        COALESCE(SUM(cc.debe - cc.haber), 0) AS saldo
    FROM cta_cte_cli cc
    LEFT JOIN facturav f ON cc.idcomp = f.id
    WHERE 1=1 [AND f.idsucursal = :id_sucursal]
    GROUP BY cc.idcliente
    HAVING saldo > 0
) AS sub
```

## Testing Strategy

| Capa | Qué testear | Enfoque |
|------|-------------|---------|
| Unit | Funciones service con datos mockeados | Verificar cálculos de saldo y clasificación vencido/por vencer |
| Integration | Endpoints HTMX responden JSON válido | Llamada directa con Flask test client |
| Visual | KPIs y tablas renderizan correctamente | Manual: verificar badges, colores, datos |

## Migration / Rollout

No se requiere migración. Las tablas `cta_cte_cli`, `cta_cte_prov`, `clientes`, `proveedores`, `facturav`, `facturac` ya existen. Solo se agregan funciones y endpoints.

## Open Questions

- [ ] `cta_cte_cli.idcomp` — ¿es FK directa a `facturav.id`? El modelo no declara ForeignKey explícito. Verificar en BD que el join `cc.idcomp = f.id` es válido.
- [ ] ¿Filtrar `baja = '1900-01-01'` en clientes/proveedores para excluir dados de baja?
