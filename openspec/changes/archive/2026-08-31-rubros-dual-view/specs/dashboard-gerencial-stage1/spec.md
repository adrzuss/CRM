# Delta for Dashboard Gerencial Stage 1

## MODIFIED Requirements

### F7: Ventas por Sucursal (Tabla)

La sección "Ventas por Sucursal" SHALL renderizarse en **full width (`col-12`)** posicionada **ANTES** de ambas secciones de rubros. Antes ocupaba `col-xl-7` junto a rubros en `col-xl-5`.

(Previously: Sección col-xl-7 lado a lado con rubros col-xl-5)

#### Scenario: Sucursal full width antes de rubros

- GIVEN dashboard cargado con datos de sucursales y rubros
- WHEN se renderiza la sección "Ventas por Sucursal"
- THEN la tabla ocupa `col-12` (ancho completo)
- AND aparece ANTES de ambas secciones de rubro (monto y cantidad)

---

### F8: Ventas por Rubro (Dual View — Monto + Cantidad)

La sección "Ventas por Rubro" SHALL dividirse en dos vistas independientes lado a lado (`col-xl-6` cada una): **Monto** (importe) y **Cantidad** (unidades). Cada vista SHALL tener su propio doughnut Chart.js y tabla.

**Dato del backend**: `get_ventas_rubro()` MUST retornar `total_unidades` además de `total_importe`.

**Vista Monto**: doughnut en `#chartRubrosMonto`, tabla columnas: Rubro | Importe | %. Datos: `r.importe_raw`. Porcentaje: `(importe_raw / total_importe) * 100`.

**Vista Cantidad**: doughnut en `#chartRubrosCantidad`, tabla columnas: Rubro | Unid. | %. Datos: `r.unidades`. Porcentaje: `(unidades / total_unidades) * 100`.

#### Scenario: Dos gráficos doughnut renderizados

- GIVEN dashboard con datos de rubros (3 rubros: Electrónica 50%, Ropa 30%, Otros 20%)
- WHEN se carga la página
- THEN se renderizan 2 doughnuts side by side
- AND el doughnut izquierdo muestra importe por rubro
- AND el doughnut derecho muestra unidades por rubro
- AND ambos usan la misma paleta de colores (mismo orden de rubros)

#### Scenario: Tabla Monto con columnas correctas

- GIVEN datos: Electrónica $5000 (50 uds), Ropa $3000 (30 uds)
- WHEN se renderiza la tabla Monto
- THEN columnas son: Rubro | Importe | %
- AND filas ordenadas por importe DESC
- AND porcentaje calculado sobre total_importe

#### Scenario: Tabla Cantidad con columnas correctas

- GIVEN datos: Electrónica $5000 (50 uds), Ropa $3000 (30 uds)
- WHEN se renderiza la tabla Cantidad
- THEN columnas son: Rubro | Unid. | %
- AND filas ordenadas por unidades DESC
- AND porcentaje calculado sobre total_unidades (no total_importe)

#### Scenario: Drill-down en doughnut Monto

- GIVEN doughnut Monto con segmento "Electrónica"
- WHEN usuario hace click en segmento "Electrónica"
- THEN fila "Electrónica" en tabla `#seccion-rubros-monto` recibe resaltado
- AND scroll suave hasta la tabla de monto

#### Scenario: Drill-down en doughnut Cantidad

- GIVEN doughnut Cantidad con segmento "Ropa"
- WHEN usuario hace click en segmento "Ropa"
- THEN fila "Ropa" en tabla `#seccion-rubros-cantidad` recibe resaltado
- AND scroll suave hasta la tabla de cantidad

#### Scenario: HTMX refresh destruye y recrea ambos charts

- GIVEN dashboard con ambos doughnuts renderizados
- WHEN HTMX ejecuta refresh de la sección rubros
- THEN `destruirCharts()` destruye `chartRubrosMonto` Y `chartRubrosCantidad`
- AND `afterSwap` re-parsea `dataset.json` de ambas tablas
- AND ambos doughnuts se recrean con datos actualizados

#### Scenario: Rubro sin nombre en ambas vistas

- GIVEN artículo con `idrubro = NULL`
- WHEN se agrupa por rubro
- THEN ambas tablas muestran "Sin rubro" como nombre
- AND el segmento aparece en ambos doughnuts

#### Scenario: Sin datos de rubros

- GIVEN período sin facturas
- WHEN se carga dashboard
- THEN ambos doughnuts se ocultan o muestran empty state
- AND ambas tablas muestran "Sin datos" en lugar de filas vacías
