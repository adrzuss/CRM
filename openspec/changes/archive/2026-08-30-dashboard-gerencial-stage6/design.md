# Design: Dashboard Gerencial ERP — Etapa 6 (Alertas Gerenciales + Drill-Down + Mejoras UX)

## Technical Approach

Agrega un panel de alertas en la parte superior del dashboard que evalúa condiciones críticas derivadas de funciones existentes (sin queries nuevas), e introduce interacciones de drill-down y mejoras de UX sobre la infraestructura actual.

## Architecture Decisions

### Decision: Alertas derivan de funciones existentes

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Reutilizar `get_stock_kpis`, `get_creditos_kpis`, `get_cta_cobrar_kpis`, `get_bancos_detalle` | Llama 4 funciones que ya se ejecutan en `get_datos_dashboard`; sin queries extra | **Elegido** |
| Query dedicado para alertas | Más rápido individualmente pero duplica lógica y crea dependencia SQL nueva | Rechazado |
| Cache con TTL | Reduce carga pero agrega complejidad de invalidación innecesaria | Rechazado |

**Rationale**: Las alertas son evaluaciones booleanas simples sobre datos ya cargados. El costo es ~4 llamadas a Python (sub-milisegundo) vs queries SQL (potencialmente 100ms+ cada una).

### Decision: Endpoint dedicado para refresh de alertas

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Endpoint dedicado `GET /api/dashboard-gerencial/alertas` | Consume recursos extra al refrescar | **Elegido** |
| Reutilizar endpoint existente de KPIs | Filtra datos innecesarios para alertas | Rechazado |
| Cargar todo el dashboard de nuevo | Sobrecarga innecesaria | Rechazado |

**Rationale**: HTMX necesita un endpoint ligero para actualizar solo el panel de alertas sin recargar toda la página. El endpoint reutiliza los mismos filtros de `_parsear_filtros()`.

### Decision: Drill-down via scrollIntoView

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `scrollIntoView({ behavior: 'smooth' })` con `data-target` | Simple, sin dependencias, funciona con HTMX | **Elegido** |
| SPA-style routing con History API | Más elegante pero requiere refactor de template | Rechazado |
| Navegación por hashes en URL | Compete con filtros existentes | Rechazado |

**Rationale**: Ya existen `id="seccion-xxx"` en el template. Solo falta agregar atributos `data-target` y el handler JS.

### Decision: Loading states con CSS puro + HTMX events

| Option | Tradeoff | Decision |
|--------|----------|----------|
| CSS spinner + `htmx:beforeRequest`/`htmx:afterRequest` | No necesita JS adicional, funciona con HTMX | **Elegido** |
| Spinner via JS con timeouts | Más control pero más frágil | Rechazado |
| Skeleton screens completos | Mejor UX pero alto costo de implementación | Rechazado |

## Data Flow

```
┌─────────────────────────────────────────────────────────┐
│  GET /dashboard-gerencial                               │
│  → get_datos_dashboard(desde, hasta, id_sucursal)       │
│      ├── get_stock_kpis()         → stock_kpis          │
│      ├── get_creditos_kpis()      → creditos_kpis       │
│      ├── get_cta_cobrar_kpis()    → cta_cobrar_kpis     │
│      └── get_bancos_detalle()     → bancos_detalle      │
│  → get_alertas_gerenciales(stock_kpis, creditos_kpis,   │
│       cta_cobrar_kpis, bancos_detalle)                  │
│      → data['alertas']                                  │
│  → render_template(data=data)                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  GET /api/dashboard-gerencial/alertas                   │
│  → _parsear_filtros() → desde, hasta, id_sucursal       │
│  → get_stock_kpis(id_sucursal)                          │
│  → get_creditos_kpis(id_sucursal)                       │
│  → get_cta_cobrar_kpis()                                │
│  → get_bancos_detalle()                                 │
│  → get_alertas_gerenciales(...)                         │
│  → jsonify({ success: true, data: alertas })            │
└─────────────────────────────────────────────────────────┘
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `services/dashboard_gerencial.py` | Modify | Agregar `get_alertas_gerenciales()`, extender `get_datos_dashboard()` con `'alertas'` |
| `routes/dashboard_gerencial.py` | Modify | Agregar endpoint `GET /api/dashboard-gerencial/alertas` e import de nueva función |
| `templates/dashboard-gerencial.html` | Modify | Sección `#seccion-alertas`, atributos `data-target`, tooltips en KPIs, empty states mejorados, spinner |
| `static/js/dashboard-gerencial.js` | Modify | Drill-down handlers, loading states, init tooltips, navegación |
| `static/css/dashboard-gerencial.css` | Modify | Estilos `.dg-alerta-*`, `.dg-spinner`, empty states, navegación, responsive |

## Interfaces / Contracts

### get_alertas_gerenciales(stock_kpis, creditos_kpis, cta_cobrar_kpis, bancos_detalle)

```python
def get_alertas_gerenciales(stock_kpis, creditos_kpis, cta_cobrar_kpis, bancos_detalle):
    """
    Evalúa condiciones críticas y retorna lista de alertas.
    Cada alerta: { tipo, titulo, mensaje, severidad, icono, seccion_target, detalle_raw }
    severidad: 'danger' | 'warning' | 'info'
    """
    alertas = []

    # Stock: bajo mínimo
    if stock_kpis['bajo_minimo'] > 0:
        alertas.append({
            'tipo': 'stock_bajo',
            'titulo': 'Stock Bajo Mínimo',
            'mensaje': f"{stock_kpis['bajo_minimo']} artículos por debajo del nivel deseable",
            'severidad': 'warning',
            'icono': 'fa-box',
            'seccion_target': 'seccion-stock-kpis',
            'detalle_raw': stock_kpis['bajo_minimo']
        })

    # Stock: sin stock
    if stock_kpis['sin_stock'] > 0:
        alertas.append({
            'tipo': 'sin_stock',
            'titulo': 'Sin Stock',
            'mensaje': f"{stock_kpis['sin_stock']} artículos sin unidades disponibles",
            'severidad': 'danger',
            'icono': 'fa-times-circle',
            'seccion_target': 'seccion-stock-kpis',
            'detalle_raw': stock_kpis['sin_stock']
        })

    # Créditos vencidos
    if creditos_kpis['creditos_vencidos'] > 0:
        alertas.append({
            'tipo': 'creditos_vencidos',
            'titulo': 'Créditos Vencidos',
            'mensaje': f"{creditos_kpis['creditos_vencidos']} créditos con cuota vencida — {creditos_kpis['porcentaje_morosidad']}% morosidad",
            'severidad': 'danger',
            'icono': 'fa-credit-card',
            'seccion_target': 'seccion-creditos-kpis',
            'detalle_raw': creditos_kpis['creditos_vencidos']
        })

    # Cta_cte vencida
    if cta_cobrar_kpis['saldo_vencido_raw'] > 0:
        alertas.append({
            'tipo': 'cta_cte_vencida',
            'titulo': 'Cuenta Corriente Vencida',
            'mensaje': f"{cta_cobrar_kpis['saldo_vencido']} de saldo vencido a cobrar ({cta_cobrar_kpis['cantidad_deudores']} clientes)",
            'severidad': 'danger',
            'icono': 'fa-hand-holding-dollar',
            'seccion_target': 'seccion-cta-cobrar-kpis',
            'detalle_raw': cta_cobrar_kpis['saldo_vencido_raw']
        })

    # Bancos saldo negativo
    bancos_negativos = [b for b in bancos_detalle if b['saldo_raw'] < 0]
    for b in bancos_negativos:
        alertas.append({
            'tipo': 'banco_negativo',
            'titulo': f"Saldo Negativo: {b['banco']}",
            'mensaje': f"Saldo {b['saldo']} — revisar movimientos",
            'severidad': 'danger',
            'icono': 'fa-building-columns',
            'seccion_target': 'seccion-bancos-detalle',
            'detalle_raw': b['saldo_raw']
        })

    return alertas
```

### API Response

```json
GET /api/dashboard-gerencial/alertas?desde=2026-08-01&hasta=2026-08-30
{
  "success": true,
  "data": [
    {
      "tipo": "sin_stock",
      "titulo": "Sin Stock",
      "mensaje": "42 artículos sin unidades disponibles",
      "severidad": "danger",
      "icono": "fa-times-circle",
      "seccion_target": "seccion-stock-kpis",
      "detalle_raw": 42
    }
  ]
}
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | `get_alertas_gerenciales()` retorna alertas correctas | Simular inputs de funciones existentes con valores que activan/desactivan alertas |
| Integration | Endpoint `/api/dashboard-gerencial/alertas` retorna JSON válido | Verificar respuesta HTTP 200 con estructura correcta |
| E2E | Panel de alertas muestra/oculta según condiciones | Verificar que 0 alertas oculta el panel |

## Migration / Rollout

No migration required. Todos los cambios son en capa de presentación y lógica de negocio sin modificaciones a la base de datos.

## Open Questions

- [ ] ¿Los umbrales de alerta deben ser configurables via `configuracion` o hardcodeados? → Proposal dice hardcodeado, se mantiene así por ahora.
