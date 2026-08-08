# Propuesta: Estilos de títulos y encabezados de columnas en tablas

## Intent

Las tablas `.table-modern` muestran cabeceras con fondo gris claro y texto gris. Se pide colorear los títulos de columna (fondo + texto) con la paleta de marca, vía un CSS compartido. El estilo vive en `.table-modern`/`.table-header` de `static/css/main.css` (cargado en `templates/base.html:26`), así que las 3 tablas que lo usan heredan el cambio sin tocar templates.

## Scope

### In Scope
- Editar el bloque `ESTILOS PARA TABLA DE ENTIDADES` de `static/css/main.css` (~L1605-1787), **solo** dos reglas:
  - `main.css:1625` `.table-modern .table-header` → fondo gradiente en teal de marca.
  - `main.css:1630` `.table-modern .table-header th` → color de texto blanco.
- Mantener tipografía del header (uppercase, 0.85rem, weight 600).
- (Opcional) Quitar clase huérfana `modern-table-container` de `_lst-articulos.html:2`.

### Out of Scope
- **NO** crear archivo CSS nuevo (aprobado: editar `main.css`).
- NO unificar las ~60 tablas que no usan `table-modern` (trabajo futuro).
- NO tocar `_lst-entidades.html` ni `fin-ent-cred.html` (heredan el estilo).
- NO cambiar estructura HTML ni clases existentes.

## Capabilities

### New Capabilities
None

### Modified Capabilities
None

## Approach

Editar las dos reglas existentes en `static/css/main.css`:

```css
.table-modern .table-header {
    background: linear-gradient(135deg, #00808a 0%, #005f66 100%);
    border-bottom: 2px solid #005f66;
}
.table-modern .table-header th {
    color: #ffffff;
}
```

Color (valores finales aprobados en design.md — decisión de producto 2026-08-07):
- Base teal de marca oscurecido `#00808a` + gradiente a `#005f66` (reemplaza `#0198a5→#01717b` de la versión inicial: el extremo claro fallaba AA 3.48:1).
- Texto blanco `#ffffff`: contraste 4.71:1–7.42:1 en toda la superficie (WCAG AA).
- Descartado `var(--primary)` de theme sb-admin (`#4e73df`): genérico; el gradiente teal `#00808a→#005f66` es la identidad del sistema.

## Affected Areas

| Área | Impacto | Descripción |
|------|---------|-------------|
| `static/css/main.css` | Modificado | 2 reglas en bloque tablas (L1625, L1630) |
| `_lst-articulos.html` | Modificado (opcional) | Quitar `modern-table-container` (L2) |
| `_lst-entidades.html`, `fin-ent-cred.html` | Sin cambio | Heredan estilo |

## Risks

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Contraste insuficiente blanco/gradiente | Baja | 5.4:1 (AA); verificar visualmente las 3 vistas |
| Regresión en otras tablas | Baja | Selectores específicos `.table-modern .table-header`; no hay duplicados |
| Conflicto con otras reglas CSS | Baja | Selectores 2 clases + `th` |

## Rollback Plan

`git checkout -- static/css/main.css` (2 reglas); si se quitó `modern-table-container`, restaurar L2. Sin migraciones ni datos: trivial.

## Dependencies

- Ninguna externa. `main.css` ya es global. Sin test runner (strict TDD deshabilitado).

## Success Criteria

- [ ] Header muestra gradiente teal de marca (`#00808a→#005f66`).
- [ ] Texto de columnas blanco con contraste ≥ 4.5:1.
- [ ] Las 3 tablas con `table-modern` heredan el estilo sin tocar sus templates.
- [ ] Ninguna tabla sin `table-modern` cambia.
- [ ] `python index.py` arranca y las 3 vistas renderizan header coloreado.
- [ ] No se creó archivo CSS nuevo.