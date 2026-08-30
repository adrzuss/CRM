# Delta para puntos-venta-lista-precio

**Cambio:** `nueva-venta-lista-precio-default`

---

## ADDED Requirements

### Requisito: `set_punto_vta` expone `id_lista_precio` en la respuesta JSON

La ruta `POST /ventas/set_punto_vta` DEBE incluir el campo `id_lista_precio` (entero o null) en el objeto JSON de respuesta. El valor DEBE provenir directamente del objeto `PuntosVenta` cargado, sin transformación.

#### Escenario: POS con lista asignada

- DADO un POS con `id_lista_precio = 2`
- CUANDO se llama `POST /ventas/set_punto_vta` con ese POS
- ENTONCES la respuesta JSON incluye `"id_lista_precio": 2`

#### Escenario: POS sin lista asignada

- DADO un POS con `id_lista_precio = null`
- CUANDO se llama `POST /ventas/set_punto_vta`
- ENTONCES la respuesta JSON incluye `"id_lista_precio": null`
