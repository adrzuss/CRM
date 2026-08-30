# Design: Dashboard Gerencial — Etapa 4: Créditos

## Technical Approach

Extiende el dashboard gerencial con una sección de análisis de créditos. Dos nuevas funciones en el servicio se encargan de calcular KPIs de cartera (créditos activos, vencidos, monto total, % morosidad) y ranking de deudores por saldo impago. Dos endpoints HTMX sirven los datos, y una nueva sección HTML se posiciona después de "Cuentas por Pagar".

**Data source**: `creditos`, `vencimientos_creditos`, `pagos_creditos`, `estados_creditos` — queries SQL directas (no stored procedures), consistente con la decisión de la propuesta de no depender de SP no documentados.

## Architecture Decisions

### Decision: No reutilizar stored procedure `get_cuotas_creditos_vencidas`

| Aspecto | Detalle |
|---------|---------|
| **Choice** | Queries SQL directas en `dashboard_gerencial.py` |
| **Alternatives** | Llamar al SP existente |
| **Rationale** | El SP no está documentado y se ignora su lógica exacta. Las queries directas dan control total sobre la definición de "vencido" (fecha_vencimiento < CURDATE() sin pago registrado) y permiten filtrar por idsucursal de forma consistente. |

### Decision: Filtrar créditos "activos" por `estados_creditos.nombre` en vez de IDs hardcodeados

| Aspecto | Detalle |
|---------|---------|
| **Choice** | JOIN con `estados_creditos` y filtrar por `nombre NOT IN ('ANULADO', 'CANCELADO', 'RECHAZADO')` |
| **Alternatives** | Filtrar `estado IN (3, 5)` como hace `get_datos_creditos` |
| **Rationale** | Los IDs de estado pueden variar entre instalaciones. Filtrar por nombre es robusto y alineado con la propuesta. Los estados no-activos son: anulado, cancelado, rechazado. |

### Decision: Morosidad como proporción de créditos, no de cuotas

| Aspecto | Detalle |
|---------|---------|
| **Choice** | `creditos_con_cuota_vencida / total_creditos_activos * 100` |
| **Alternatives** | Porcentaje de cuotas vencidas sobre total cuotas |
| **Rationale** | La métrica de negocio relevante es "qué proporción de clientes tienen al menos un problema de pago". Más informativa que métrica por cuota. |

## Data Flow

```
MySQL (creditos + vencimientos_creditos + pagos_creditos + estados_creditos)
  │
  ▼
get_creditos_kpis()          get_creditos_top_deudores()
  │                                │
  ▼                                ▼
Route api_creditos_kpis()     Route api_creditos_top()
  │                                │
  ▼                                ▼
JSON response                  JSON response
  │                                │
  ▼                                ▼
get_datos_dashboard()          Template (Jinja2)
  │                                │
  └───── data['creditos_kpis'] ────┘
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `services/dashboard_gerencial.py` | Modify | +2 functions: `get_creditos_kpis()`, `get_creditos_top_deudores()`. Wire-up en `get_datos_dashboard()` |
| `routes/dashboard_gerencial.py` | Modify | +2 imports, +2 endpoints HTMX, +sección créditos en main route |
| `templates/dashboard-gerencial.html` | Modify | +sección HTML créditos (4 KPI cards + tabla top deudores), después de cta_pagar_top |
| `static/js/dashboard-gerencial.js` | Modify | Sin cambios significativos (server-side rendering) |
| `static/css/dashboard-gerencial.css` | Modify | +badge `.badge-creditos-vigente` y `.badge-creditos-vencido` |

## Interfaces / Contracts

### `get_creditos_kpis(id_sucursal=None)` → dict

```python
{
    'creditos_activos': int,       # Total créditos con estado != anulado/cancelado/rechazado
    'creditos_vencidos': int,      # Créditos activos con al menos 1 cuota vencida
    'monto_total_cartera': str,    # Formato '$ 1.250.450,50' (Decimal internamente)
    'monto_total_cartera_raw': float,
    'porcentaje_morosidad': float, # creditos_vencidos / creditos_activos * 100
    'cantidad_deudores': int,      # Clientes con al menos 1 crédito activo con saldo > 0
}
```

### `get_creditos_top_deudores(limite=10, id_sucursal=None)` → list[dict]

```python
[
    {
        'nombre': str,             # Nombre del cliente
        'documento': str,          # Documento del cliente
        'cantidad_creditos': int,  # Créditos activos con saldo > 0
        'saldo_total': str,        # Suma de saldos impagos, formato '$ 1.250,50'
        'saldo_total_raw': float,
    }
]
```

### SQL Patterns

**Saldo por crédito**:
```sql
SELECT c.id,
       COALESCE(SUM(vc.monto), 0) - COALESCE(SUM(pc.monto), 0) AS saldo
FROM creditos c
LEFT JOIN vencimientos_creditos vc ON vc.idcredito = c.id
LEFT JOIN pagos_creditos pc ON pc.idvencimiento = vc.id
JOIN estados_creditos ec ON c.estado = ec.id
WHERE ec.nombre NOT IN ('ANULADO', 'CANCELADO', 'RECHAZADO')
GROUP BY c.id
```

**Crédito con cuota vencida**:
```sql
-- Subquery: al menos 1 vencimiento con fecha < CURDATE() sin pago
SELECT COUNT(DISTINCT c.id) AS creditos_vencidos
FROM creditos c
JOIN vencimientos_creditos vc ON vc.idcredito = c.id
LEFT JOIN pagos_creditos pc ON pc.idvencimiento = vc.id
JOIN estados_creditos ec ON c.estado = ec.id
WHERE ec.nombre NOT IN ('ANULADO', 'CANCELADO', 'RECHAZADO')
  AND vc.fecha_vencimiento < CURDATE()
  AND pc.id IS NULL
```

### Wire-up en `get_datos_dashboard()`

```python
'creditos_kpis': get_creditos_kpis(id_sucursal),
'creditos_top_deudores': get_creditos_top_deudores(10, id_sucursal),
```

## Template Section

Posición: después de `<!-- Top Proveedores -->` (línea ~866), antes del cierre `</div>`.

```
<!-- ═══ SECCIÓN: Créditos (Etapa 4) ══════════════════════════════════ -->
<!-- Header: "Créditos" -->
<!-- 4 KPI cards: Créditos Activos | Créditos Vencidos | Monto Cartera | % Morosidad -->
<!-- Tabla: Top Deudores por Crédito -->
```

KPI cards use `border-start-*` variants: primary, danger, info, warning (same pattern as stock/cta_cte sections).

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | `get_creditos_kpis()`, `get_creditos_top_deudores()` return correct structure | Manual: verificar con datos de BD existentes |
| Integration | Endpoints HTMX responden con JSON success | Curl/Postman a `/api/dashboard-gerencial/creditos-kpis` |
| E2E | Sección créditos renderiza en dashboard | Navegar a `/dashboard-gerencial`, verificar 4 KPIs + tabla |

## Migration / Rollout

No migration required. Todas las tablas (`creditos`, `vencimientos_creditos`, `pagos_creditos`, `estados_creditos`) existen en la BD.

## Open Questions

- [ ] ¿Los estados no-activos son exactamente 'ANULADO', 'CANCELADO', 'RECHAZADO'? Verificar en la BD la tabla `estados_creditos` para confirmar los valores exactos de `nombre`.
- [ ] ¿Se debe filtrar solo créditos con `fecha_inicio <= CURDATE()` (ya empezaron) o todos los activos incluyendo futuros?
