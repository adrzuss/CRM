# Design: Estilos de títulos y encabezados de columnas en tablas

## Technical Approach

Cambio 100% CSS en `static/css/main.css`. Se editan solo las dos reglas del bloque `ESTILOS PARA TABLA DE ENTIDADES` (L1625 y L1630): el header `.table-modern .table-header` pasa de gradiente gris claro a gradiente teal de marca, y el texto `th` a blanco. Como `main.css` se carga globalmente (`base.html:26`), las 3 plantillas que usan `table-modern` heredan el estilo sin tocar templates. No se crea archivo CSS nuevo. Sin delta funcional → spec omitido por decisión; el diseño se referencia desde la propuesta aprobada.

## Architecture Decisions

### Decisión: Gradiente teal oscuro accesible para el header

| Opción | Trade-off | Decisión |
|--------|-----------|----------|
| `linear-gradient(135deg, #0198a5, #01717b)` (valores originales de la propuesta) | Extremo claro da 3.48:1 con texto blanco — falla AA | Rechazada (decisión de producto 2026-08-07) |
| `var(--primary)` de sb-admin (`#4e73df`) | Genérico, rompe identidad teal del sistema | Rechazada |
| **`linear-gradient(135deg, #00808a, #005f66)` + texto blanco** | Teal oscuro, AA en toda la superficie | **ELEGIDA — decisión final de producto** |

**Rationale**: El usuario pidió explícitamente un color que "se note" (el gris claro actual no se distinguía) y eligió la opción A tras revisar los contrastes: gradiente teal oscuro `#00808a → #005f66` con texto blanco. Verificación: blanco sobre `#00808a` (stop claro) = **4.71:1**, sobre `#005f66` (stop oscuro) ≈ **7:1** — cumple WCAG AA 4.5:1 en toda la superficie del gradiente, incluso para el texto normal del header (0.85rem ~13.6px bold). Se mantiene `border-bottom: 2px solid #005f66` (coherente con el extremo oscuro).

### Decisión: Eliminación de la clase huérfana `modern-table-container`

| Opción | Trade-off | Decisión |
|--------|-----------|----------|
| Quitarla de `_lst-articulos.html:2` | Ordena el HTML, pero toca plantilla (fuera del alcance CSS-puro) | **Dejar como está (no bloqueante)** |
| Dejarla | Clase definida en ningún lado, inofensiva | Elegida |

**Rationale**: `modern-table-container` es huérfana (no hay regla CSS), pero el `div` ya tiene `table-responsive` (regla en `main.css:1610` que aporta sombra/borde). Quitarla es trivial y fuera del alcance aprobado. **Corrección de ruta**: la propuesta citaba `templates/partials/_lst-articulos.html`; la ruta real es `templates/articulos/partials/_lst-articulos.html`.

## Data Flow

No hay flujo de datos ni lógica: cambio de presentación pura en una hoja de estilos global.

    templates (3) ──table-modern──> Browser ──> static/css/main.css (2 reglas editadas)

## File Changes

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `static/css/main.css` | Modificar | 2 reglas en bloque tablas (L1625, L1630) |

## Edits CSS Exactos (before → after)

**Regla 1 — `main.css:1625`** `.table-modern .table-header`:

```css
/* before */
background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
border-bottom: 2px solid #dee2e6;

/* after (aprobado) */
background: linear-gradient(135deg, #00808a 0%, #005f66 100%);
border-bottom: 2px solid #005f66;
```

**Regla 2 — `main.css:1630` `.table-modern .table-header th`** (sólo `color`):

```css
/* before */
color: #495057;

/* after */
color: #ffffff;
```

Se mantienen tipografía (uppercase, 0.85rem, weight 600), padding y bordes actuales. No se toca la media-query L1770 (fondo/color) ni la regla donde se repite el color.

## Interfaces / Contracts

Sin API. El contrato es el selector `.table-modern .table-header th`, que acota el cambio a las 3 tablas `table-modern` y deja intactas las ~60 tablas Bootstrap planas. Las 3 templates (`articulos/partials/_lst-articulos.html`, `entidades/partials/_lst-entidades.html`, `entidades/fin-ent-cred.html`) heredan por CSS.

## Testing Strategy

| Capa | Qué probar | Cómo |
|------|-----------|------|
| Visual (E2E manual) | Header arriba color teal en las 3 vistas | `python index.py`, navegar a listado de artículos, listado de entidades y crédito de entidades; comprobar fondo + texto blanco |
| Contraste | Verificar AA y el criterio "≥ 4.5:1" | Herramienta de contraste: blanco vs `#00808a`=4.71:1, vs `#005f66`≈7:1 — ambos extremos sobre 4.5:1 |
| Regresión | Otras ~60 tablas Bootstrap no cambian | Inspección visual de una tabla sin `table-modern`; verificar que el selector no las alcanza |

No hay test runner (strict TDD deshabilitado, `config.yaml` verify build = `python index.py`).

## Migration / Rollout

No migración de datos ni feature flag. Cambio trivial (≈5 líneas editadas en 1 archivo). Dentro del presupuesto de 400 líneas por PR.

## Open Questions

- Resuelto: gradiente final elegido por el usuario = `#00808a → #005f66` + texto blanco (opción A accesible). No quedan decisiones pendientes.