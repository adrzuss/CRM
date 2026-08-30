# Nueva Venta — Auto-selección de Lista de Precios por Punto de Venta

**Cambio:** `nueva-venta-lista-precio-default`
**Tipo:** Nueva capacidad (full spec)

---

## Propósito

Al asignar un punto de venta en `nueva_venta`, el selector `#idlista` DEBE reflejar automáticamente la lista de precios configurada en ese POS. Si el POS no tiene lista configurada, se aplica la primera opción disponible. El default en page-load DEBE ser la primera lista en lugar del id hardcodeado `1`.

---

## Requisitos

### Requisito: JS aplica `id_lista_precio` al asignar punto de venta

`asignarPuntoVenta()` DEBE, tras establecer los campos del POS en el DOM, leer `result.id_lista_precio` de la respuesta y actualizar `#idlista`. Si el valor es truthy, DEBE establecer ese id. Si es falsy, DEBE establecer el valor de la primera `<option>` del select. `recalcularPreciosPorLista()` NO DEBE ser invocado en esta operación.

#### Escenario: POS con lista configurada

- DADO un POS con `id_lista_precio = 2`
- CUANDO `asignarPuntoVenta()` procesa la respuesta del servidor
- ENTONCES `#idlista` queda con valor `"2"`
- Y `recalcularPreciosPorLista()` no es invocado

#### Escenario: POS sin lista configurada (null)

- DADO un POS con `id_lista_precio = null`
- CUANDO `asignarPuntoVenta()` procesa la respuesta
- ENTONCES `#idlista` queda con el valor de la primera `<option>` del select

#### Escenario: Select sin opciones disponibles

- DADO que `#idlista` no tiene `<option>` (lista vacía)
- CUANDO `asignarPuntoVenta()` intenta aplicar el fallback
- ENTONCES la operación es un no-op (sin error JS)

#### Escenario: Usuario cambia lista manualmente tras auto-selección

- DADO que `#idlista` fue auto-seleccionado por `asignarPuntoVenta()`
- CUANDO el usuario selecciona otra lista manualmente
- ENTONCES el listener `change` existente dispara `recalcularPreciosPorLista()` normalmente

---

### Requisito: Template usa `loop.first` como default en page-load

El template `nueva_venta.html` DEBE pre-seleccionar la primera `<option>` del selector `#idlista` usando `loop.first` en lugar de comparar `lista.id == 1`.

#### Escenario: Page-load sin POS pre-seleccionado

- DADO que la página carga sin sesión de POS activa
- CUANDO se renderiza el selector `#idlista`
- ENTONCES la primera opción de la lista está marcada como `selected`
- Y el comportamiento no depende del valor del campo `id` de esa lista

#### Escenario: Primera lista tiene id distinto de 1

- DADO que la lista con menor id en DB tiene `id = 3`
- CUANDO se renderiza el selector
- ENTONCES esa primera lista queda `selected` (no se produce selección vacía)
