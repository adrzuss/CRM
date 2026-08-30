# Especificación: Asignación de Lista de Precios a Punto de Venta

**Cambio:** `puntos-venta-lista-precio`
**Tipo:** Nueva capacidad (full spec — no existe spec base)

---

## Propósito

Un punto de venta DEBE poder tener asignada una lista de precios. La asignación se persiste en DB, se pre-selecciona al editar el registro, y se muestra en la vista de lista.

---

## Requisitos

### Requisito: Modelo ORM expone `id_lista_precio`

El modelo `PuntosVenta` DEBE mapear la columna `id_lista_precio` como FK nullable hacia `listas_precio.id`. DEBE exponer una relación `lista_precio` para acceso directo al objeto relacionado.

#### Escenario: FK nullable sin valor

- DADO un punto de venta sin lista asignada
- CUANDO se carga el objeto ORM
- ENTONCES `pv.id_lista_precio` es `None` y `pv.lista_precio` es `None`

#### Escenario: FK con valor

- DADO un punto de venta con `id_lista_precio = 3`
- CUANDO se carga con `joinedload(PuntosVenta.lista_precio)`
- ENTONCES `pv.lista_precio.nombre` retorna el nombre de la lista

---

### Requisito: Servicio persiste `id_lista_precio`

`grabarDatosPtoVta` DEBE leer `id_lista_precio` del formulario y persistirlo. Si el valor es vacío o ausente, DEBE guardar `None` (no forzar cero).

#### Escenario: Guardar con lista seleccionada

- DADO un formulario con `id_lista_precio = "2"`
- CUANDO se llama `grabarDatosPtoVta`
- ENTONCES el registro queda con `id_lista_precio = 2`

#### Escenario: Guardar sin lista ("Sin lista")

- DADO un formulario con `id_lista_precio = ""`
- CUANDO se llama `grabarDatosPtoVta`
- ENTONCES el registro queda con `id_lista_precio = None`

---

### Requisito: Ruta provee listas de precios al template

La ruta `puntos_venta` DEBE pasar `listas_precios = ListasPrecios.query.all()` al contexto del template. La consulta DEBE incluir `joinedload(PuntosVenta.lista_precio)` para evitar N+1.

#### Escenario: Contexto disponible en template

- DADO que existen 3 listas de precios activas
- CUANDO se carga la vista de configuración de puntos de venta
- ENTONCES el template recibe `listas_precios` con 3 elementos

---

### Requisito: Formulario muestra selector de lista de precios

El partial `_alta-punto-venta.html` DEBE incluir un `<select name="id_lista_precio">` dentro de `pv-section-general`. DEBE tener una opción inicial "Sin lista" con valor vacío. DEBE pre-seleccionar la lista asignada al editar.

#### Escenario: Crear nuevo punto de venta

- DADO el formulario de alta vacío
- CUANDO se renderiza el selector
- ENTONCES la primera opción es "Sin lista" y está seleccionada

#### Escenario: Editar punto de venta con lista asignada

- DADO un punto de venta con `id_lista_precio = 2`
- CUANDO se abre el formulario de edición
- ENTONCES la opción con `value="2"` aparece como seleccionada

#### Escenario: Guardar cambio de lista

- DADO un punto de venta con `id_lista_precio = 1`
- CUANDO el usuario cambia la selección a otra lista y guarda
- ENTONCES el registro refleja el nuevo `id_lista_precio`

---

### Requisito: Vista de lista muestra la lista de precios asignada

El partial `_lst-puntos-ventas.html` DEBE mostrar una columna "Lista de precios". Si el punto de venta tiene lista asignada, DEBE mostrar un badge con el nombre. Si no tiene lista, DEBE mostrar "—".

#### Escenario: Punto de venta con lista

- DADO un punto de venta con `lista_precio.nombre = "Mayorista"`
- CUANDO se renderiza la tabla
- ENTONCES aparece un badge con el texto "Mayorista"

#### Escenario: Punto de venta sin lista

- DADO un punto de venta con `id_lista_precio = None`
- CUANDO se renderiza la tabla
- ENTONCES la celda muestra "—"

---

### Requisito: Patrones Bootstrap 5 en la vista de lista

`_lst-puntos-ventas.html` DEBE usar únicamente patrones BS5. DEBE reemplazar atributos `data-dismiss` por `data-bs-dismiss` y cualquier invocación `$(...).modal(...)` por `bootstrap.Modal`.

#### Escenario: Modal de confirmación usa BS5

- DADO que el partial usa `data-bs-dismiss="modal"` y `new bootstrap.Modal(...)`
- CUANDO se abre y cierra un modal
- ENTONCES el modal funciona sin errores de consola relacionados con BS4

---

## Restricciones

- Las listas de precios son globales: NO se filtra por sucursal.
- La migración de columna (`id_lista_precio INTEGER NULL`) es prerrequisito y está fuera de scope.
- No se realiza rediseño visual completo; solo correcciones de consistencia BS5.
