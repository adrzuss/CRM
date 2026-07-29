# Proposal: Más Tests 🧪

## Intent

Ahora que los services están divididos en paquetes (`services/ventas/`, `services/articulos/`), tenemos la red de contención de 19 tests existentes. Es momento de cubrir las rutas y services críticos que aún no tienen tests: ventas, artículos y proveedores.

## Scope

### In Scope
- Tests de rutas para ventas (`routes/ventas.py`) — listado, creación, factura
- Tests de rutas para artículos (`routes/articulos.py`) — listado, stock, precios
- Tests de rutas para proveedores (`routes/proveedores.py`) — listado, compras
- Tests de services para `services/ventas/` — funciones clave de facturación
- Tests de services para `services/articulos/` — stock, precios, búsqueda

### Out of Scope
- Tests de rutas de créditos, bancos, fondos, cta cte (cambio futuro)
- Tests de integración con AFIP (requiere entorno especial)
- Tests de templates/UI (requiere Playwright/Selenium)

## Capabilities

### New Capabilities
- `route-tests`: Tests de rutas Flask con mocking de DB y session
- `service-tests`: Tests unitarios de services con mocking de SQLAlchemy

### Modified Capabilities
None

## Approach

1. Identificar las 3–5 rutas más críticas de cada módulo (ventas, artículos, proveedores)
2. Escribir tests con el patrón existente: `conftest.py` fixtures + mocking de `g` y `session`
3. Para services: mockear `db.session` y probar funciones clave (cálculo de totales, stock, etc.)
4. Mantener el estilo existente de tests (comentarios en español, asserts simples)

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `tests/test_ventas.py` | New | Tests de rutas + services de ventas |
| `tests/test_articulos.py` | New | Tests de rutas + services de artículos |
| `tests/test_proveedores.py` | New | Tests de rutas + services de proveedores |
| `tests/conftest.py` | Modified | Agregar fixtures necesarios para nuevos tests |

## Riesgos

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Rutas que dependen de sesión compleja | Media | Mockear `session` en fixtures |
| Services que llaman stored procedures | Alta | Mockear `db.session.execute()` |
| Tests lentos por DB real | Baja | Usar SQLite en memoria como ya hacemos |

## Success Criteria

- [ ] `pytest tests/ -v` — todos los tests nuevos + existentes pasan
- [ ] Al menos 3 tests por módulo (ventas, artículos, proveedores)
- [ ] Tests de services que verifican lógica de negocio (no solo HTTP)
- [ ] Sin cambios en código de producción
