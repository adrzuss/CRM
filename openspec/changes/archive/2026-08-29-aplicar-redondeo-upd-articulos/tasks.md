# Tasks: Aplicar Redondeo en upd-articulos

## Phase 1: Backend — routes/articulos.py

- [x] 1.1 Add `ReglaRedondeo` to imports from `models.configs`
- [x] 1.2 Query active rules (`ReglaRedondeo.query.filter_by(activo=True).all()`) in `update_articulo()` GET handler
- [x] 1.3 Pass `reglas_redondeo` to `render_template('upd-articulos.html', ...)`

## Phase 2: Template — upd-articulos.html

- [x] 2.1 Add JSON serialization `<script>` tag with `const REGLAS_REDONDEO = {{ reglas_redondeo | tojson }};` before JS module imports

## Phase 3: JavaScript — upd-articulos.js

- [x] 3.1 Add `aplicarRedondeo(precio, reglas)` function supporting arriba/abajo/cercano + restar_unidades
- [x] 3.2 Modify `calcularPrecio()` line 65 to apply `aplicarRedondeo()` after `markup × costoTotal`
