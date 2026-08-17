# Reporte de Archivo: fix-tablero-ventas

> Fase: sdd-archive · Modo artefacto: openspec · Proyecto: crm
> Fecha: 2026-08-17

## Resumen

Cambio `fix-tablero-ventas` completado y archivado. Bug fix que restaura los 3 gráficos del tablero gerencial (`/tablero-inicial`) vacíos por regresión CSP del commit `219aac2` (nonce faltante en 4 scripts inline de `templates/tablero.html`), más endurecimiento de 2 fallas latentes de la misma superficie (código muerto `barrasRubros` en `chart-bar-demo.js`; `get_vta_rubros` sin try/except en `reportes.py`).

## Datos del cambio

- **Commit de implementación**: `65df9a2` — `fix(tablero): restaurar gráficos del tablero gerencial con nonce CSP`
- **Archivos fuente (3)**: `templates/tablero.html` (nonce x4, +4/-4), `static/js/demo/chart-bar-demo.js` (-84 líneas, bloque muerto `barrasRubros`), `services/ventas/reportes.py` (try/except en `get_vta_rubros`)
- **Fuera de alcance (follow-ups)**: contexto incompleto de `tablero_administrativo` (`routes/tableros.py:106`), vars nunca provistas `proximosEventos`/`proximasCitas`/`proximasCuotas`/`cuotasVencidas` (`tablero.html:291-346`), auditoría CSP sistémica (40+ templates con inline sin nonce)
- **Rollback**: `git revert 65df9a2` (cambios independientes entre sí)

## Verificación

**Veredicto**: PASS WITH WARNINGS — sin defectos CRITICAL de implementación (evidencia estática: py_compile reportes.py OK, node --check de ambos JS OK, diff sin cambios fuera de alcance).

**Pendientes manuales en navegador (tareas 4.1-4.5, PENDING-MANUAL — se transfieren a la próxima sesión)**:
- **4.1** — `/tablero-inicial`: 3 gráficos con datos (barras 6 meses, doughnut ingresos hoy, 2 pies de rubros)
- **4.2** — Consola limpia: sin violaciones CSP, sin "can't acquire context", sin "length of null"
- **4.3** (opcional) — Degradación: SP `venta_rubros` roto → HTTP 200 con pies vacíos
- **4.4** — Regresión: `/tablero-basico` y `/tablero-gerencial` sin errores nuevos; tarjetas de métricas intactas
- **4.5** — `/tablero-administrativo`: 500 pre-existente idéntico al pre-fix (no empeora)

**Follow-ups recomendados (SUGGESTION del verify-report)**:
- Auditoría CSP sistémica: 40+ templates con `<script>` inline sin nonce (p.ej. `fondos/flujo-fondos.html`, `ctactecli/partials/_ctacte-cli.html`, `fondos/rend-cajas.html`, `creditos/*.html`)
- `tablero_administrativo`: 500 pre-existente por contexto incompleto (`routes/tableros.py:106`)
- Vars nunca provistas en `tablero.html:291-346` → tarjetas vacías silenciosas desde `e6e7d2b`
- Guard defensivo opcional en `chart-pie-demo.js:34` (`Array.isArray(tipoPagos)`)

## Sync de specs

| Dominio | Acción | Detalle |
|---------|--------|---------|
| `tablero-ventas` | Creado | Spec completa copiada de `openspec/changes/fix-tablero-ventas/specs/tablero-ventas/spec.md` → `openspec/specs/tablero-ventas/spec.md` (4 requirements, 7 scenarios; sin delta previo en `openspec/specs/`) |

## Contenido del archivo

`openspec/changes/archive/2026-08-17-fix-tablero-ventas/`:
- `proposal.md` ✅ (intent, scope, approach, rollback)
- `exploration.md` ✅ (causa raíz CSP commit `219aac2`, cadena ruta→template→JS verificada)
- `specs/tablero-ventas/spec.md` ✅ (delta spec, fuente de la spec principal)
- `design.md` ✅ (decisiones de arquitectura, flujo de datos)
- `tasks.md` ✅ (12 tareas: 7 completas, 5 PENDING-MANUAL 4.1-4.5)
- `verify-report.md` ✅ (PASS WITH WARNINGS, matriz de compliance 0/7 runtime)
- `archive-report.md` ✅ (este reporte)

## Trazabilidad

- Rastreo engit: commit único `65df9a2` (8 archivos: 3 fuente + 5 openspec), sin cambios fuera de alcance.
- No aplica registro de observation IDs de Engram: los artefactos viven en el filesystem (modo openspec). Este reporte se persiste además en Engram (`sdd/fix-tablero-ventas/archive-report`).