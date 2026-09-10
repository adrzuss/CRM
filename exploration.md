## Exploration: comisiones

### Current State

**Architecture Overview:**
- Flask app factory pattern (`create_app()` in `index.py`)
- Blueprints registered with url_prefix (e.g., `bp_ventas` → `/ventas`)
- SQLAlchemy ORM with `db = SQLAlchemy()` in `utils/db.py`
- MySQL database, Alembic migrations in `migrations/`
- Templates: Jinja2 extending `base.html`, using Bootstrap 5, SweetAlert2, HTMX, jQuery
- Frontend JS: separate files per module in `static/js/`, jQuery-based with `swal-helpers.js`
- Spanish naming throughout (snake_case functions, PascalCase models)

**Models Pattern (models/ventas.py):**
- `Factura` → table `facturav`: id, idcliente, idlista, fecha, total, neto, bonificacion, iva, exento, impint, idtipocomprobante, idsucursal, idusuario, nro_comprobante, punto_vta, cae, cae_vto, fecha_emision, idempotency_key
- `Item` → table `itemsv`: idfactura (FK), id, idarticulo, cantidad, precio_unitario, precio_total, neto, bonificacion, iva, idalciva, ingbto, idingbto, exento, impint, idoferta, id_color, id_detalle
- `PagosFV` → table `pagos_fv`: idfactura, idpago, tipo, total, entidad
- `ControlNc` → tracks credit notes: id_comprobante, id_comprobante_org, fecha
- NOTE: No `costo_unitario` field in `itemsv` currently — must be added

**Articulo model (models/articulos.py):**
- Has `costo` (Decimal 20,6) and `costo_total` (Decimal 20,6)
- Has `idmarca`, `idrubro`, `idtipoarticulo` — all FKs needed for commission rules
- Has `precios` relationship to `Precio` model

**Sales Flow (services/ventas/ventas.py):**
1. `procesar_nueva_venta(form, id_sucursal)` — main entry point
2. Checks idempotency key, creates `Factura` record
3. `procesar_items()` — iterates form items, creates `Item` records, updates stock
4. `procesar_pagos()` — creates `PagosFV` records (efectivo=tipo1, tarjeta=tipo2, ctacte=tipo3, bonificacion=tipo4, credito=tipo5, nota_credito=tipo20, vale=tipo21)
5. If credit note: calls `procesar_nueva_nc()` which creates `ControlNc` record
6. All within one transaction with rollback on error

**Credit Note Flow:**
- Route `nueva_nota_credito` reuses `procesar_nueva_venta()` with same transaction
- `ControlNc` links NC to original invoice
- Stock updates with `tipoMovimiento = 'NotaCredito'` for NC types
- NC types identified via `tipo_comp_aplica.id_tipo_oper` (Venta vs Nota de Crédito)
- NC used as payment method (vale) via `PagosFV` tipo=21

**Payment Flow:**
- `pagos_fv` table: tipo 1=efectivo, 2=tarjeta, 3=ctacte, 4=bonificacion, 5=credito, 20=nota_credito, 21=vale, 99=vuelto
- `MovEntidades` tracks card transactions
- `CtaCteCli` tracks account movements

**User/Vendor System:**
- `Usuarios` model (models/sessions.py): id, nombre, usuario, clave, documento, email, telefono, direccion
- NO explicit "vendedor" role — vendors are just users with `idusuario` in `facturav`
- Session stores: `user_id`, `id_sucursal`, `id_empresa`
- `facturav.idusuario` = who registered the sale (currently used as "vendedor")

**Permission System:**
- `Tareas` model: roles/tasks (id, tarea)
- `TareasUsuarios`: assigns tasks to users (idtarea, idusuario)
- `OpcionesMenu`: menu items with `codigo` string identifier
- `PermisosMenu`: links menu options to tasks
- Template function `tiene_permiso('codigo')` checks permission
- Decorator `@check_session` validates session
- If no permissions configured → allows all (backward compatible)
- Sidebar uses `tiene_permiso('Nueva venta')` etc.

**Database Access Patterns:**
- ORM: `db.session.query()`, `db.session.get()`, `Model.query.filter_by()`
- Raw SQL: `db.session.execute(text("CALL procedure(:param)"), params)`
- Heavy use of stored procedures for reports
- `Decimal` for all monetary values
- `db.session.flush()` before getting auto-increment IDs

**Template Patterns:**
- Templates in `templates/{module}/` directories
- Extend `base.html`, use `{% block body %}`
- Bootstrap 5 cards with `.modern-card`, `.card-header`
- Partials in `templates/partials/` and `templates/{module}/partials/`
- jQuery AJAX for dynamic operations, SweetAlert2 for alerts
- HTMX for some dynamic updates
- DataTables for list views

**Blueprint Registration Pattern (index.py):**
```python
from routes.ventas import bp_ventas
app.register_blueprint(bp_ventas, url_prefix='/ventas')
```

**Sidebar Pattern:**
- Collapsible sections with `data-bs-toggle="collapse"`
- Permission-gated links using `tiene_permiso('codigo')`

### Affected Areas

- `models/ventas.py` — must add `costo_unitario` and `costo_total` to `Item` model
- `services/ventas/ventas.py` — must capture `articulo.costo` during item creation in `procesar_items()`
- `index.py` — must register new `bp_comisiones` blueprint
- `templates/partials/_sidebar.html` — must add Comisiones menu section
- `models/sessions.py` — may need new `OpcionesMenu` entries for commission permissions
- NEW: `models/comisiones.py` — 6 new models (planes, reglas, tramos, asignaciones, liquidaciones, detalle)
- NEW: `routes/comisiones.py` — new blueprint
- NEW: `services/comisiones/` — service layer with calculator engine
- NEW: `templates/comisiones/` — CRUD screens
- NEW: `static/js/comisiones.js` — frontend logic

### Approaches

1. **Monolith integration** — Follow existing pattern: models in `models/`, services in `services/`, routes in `routes/`
   - Pros: Matches existing architecture exactly, easy for team to maintain
   - Cons: Files may get large, no clear module boundary
   - Effort: Medium

2. **Self-contained module** — Create `comisiones/` package with routes, services, models, calculator
   - Pros: Clear separation, spec recommends this (Section 48), extensible
   - Cons: Slightly different from existing pattern, more files to manage
   - Effort: Medium-High

3. **Hybrid** — Models in `models/comisiones.py`, services in `services/comisiones/`, routes in `routes/comisiones.py`
   - Pros: Follows existing conventions while keeping commission logic grouped
   - Cons: Slightly less self-contained than approach 2
   - Effort: Medium

### Recommendation

**Approach 3 (Hybrid)** — because:
- The existing codebase has a very consistent pattern (one model file per domain, one route file per domain, services grouped by domain)
- Deviating too much creates maintenance friction
- The calculator engine can live in `services/comisiones/calculator.py` as the spec suggests
- Models go in `models/comisiones.py` following the pattern of `models/ventas.py`, `models/articulos.py`
- Routes go in `routes/comisiones.py` following existing blueprint pattern

### Risks

1. **Historical data** — Existing sales lack `costo_unitario` in items; margin calculations require this. Must handle NULL/0 gracefully.
2. **Stored procedures** — Many report queries use MySQL stored procedures; commission reports may need new SPs or ORM queries.
3. **Performance** — Commission calculation iterates all items in a period; needs batch queries, not N+1.
4. **Transaction safety** — Adding `costo_unitario` capture to `procesar_items()` modifies the existing sale transaction — must be backward-compatible (default 0).
5. **Permission granularity** — Current permission system uses string codes in `OpcionesMenu.codigo`; must add new codes without breaking existing ones.
6. **NC identification** — Must correctly identify NC vs Sale using `tipo_comp_aplica.id_tipo_oper`; verify the exact type IDs.
7. **Idempotency** — Commission calculation must be idempotent per spec; requires unique constraint on (id_liquidacion, id_factura, id_item, id_regla).

### Ready for Proposal

Yes — the exploration is complete. The spec is thorough and the codebase patterns are well understood. Ready to proceed to proposal/design phase.
