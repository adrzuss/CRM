# Redondeo en Cambio de Precio — Specification

## Purpose

Aplicar reglas de redondeo comercial configuradas en `ReglaRedondeo` al calcular `precio_nuevo` en el endpoint de cambio de precio por marca/rubro (`obtenerArticulosMarcaRubro`).

## Requirements

### REQ-001: Módulo de redondeo comercial

El sistema DEBE tener un archivo `services/articulos/redondeo.py` con funciones puras de redondeo comercial.

#### Scenario: SCE-001 — Redondeo arriba con multiplo=100

- GIVEN un precio_nuevo de 4327 y una regla con multiplo=100, tipo=arriba
- WHEN se aplica `aplicar_redondeo(4327, 100, 'arriba', 0)`
- THEN el resultado es 4400

#### Scenario: SCE-002 — Redondeo abajo con multiplo=100

- GIVEN un precio_nuevo de 4327 y una regla con multiplo=100, tipo=abajo
- WHEN se aplica `aplicar_redondeo(4327, 100, 'abajo', 0)`
- THEN el resultado es 4300

#### Scenario: SCE-003 — Redondeo cercano con multiplo=100

- GIVEN un precio_nuevo de 4327 y una regla con multiplo=100, tipo=cercano
- WHEN se aplica `aplicar_redondeo(4327, 100, 'cercano', 0)`
- THEN el resultado es 4300 (distancia a 4300 = 27, distancia a 4400 = 73)

#### Scenario: SCE-004 — Redondeo arriba con restar=10

- GIVEN un precio_nuevo de 4327, regla multiplo=100, tipo=arriba, restar=10
- WHEN se aplica `aplicar_redondeo(4327, 100, 'arriba', 10)`
- THEN el resultado es 4390 (4400 - 10)

### REQ-002: Función calcular_precio_comercial

El sistema DEBE tener una función `calcular_precio_comercial(precio_lista, porcentaje, reglas_db)` que calcule el precio con porcentaje y aplique la regla de redondeo aplicable.

#### Scenario: Regla encontrada se aplica

- GIVEN un precio_lista=4000, porcentaje=8.175, y una regla activa con multiplo=100, tipo=arriba, rango [4300, 4500]
- WHEN se llama a `calcular_precio_comercial(4000, 8.175, reglas_db)`
- THEN se calcula precio_nuevo=4327, se encuentra la regla, y se retorna 4400

#### Scenario: Sin regla aplicable, precio original se mantiene

- GIVEN un precio_lista=40, porcentaje=25, y reglas con rango mínimo desde_precio=100
- WHEN se llama a `calcular_precio_comercial(40, 25, reglas_db)`
- THEN se retorna 50 (precio_nuevo sin redondear, porque no hay regla para ese rango)

### REQ-003: Consulta de reglas activas por request

La función `obtenerArticulosMarcaRubro` DEBE consultar una sola vez las reglas `ReglaRedondeo` con `activo=True` antes del loop de artículos.

#### Scenario: SCE-007 — Sin reglas activas en DB

- GIVEN no existen reglas activas en la tabla `reglas_redondeo`
- WHEN se ejecuta cambio de precio para un set de artículos
- THEN todos los `precio_nuevo` se calculan sin redondeo (comportamiento actual)

### REQ-004: Redondeo independiente por artículo

Cada artículo DEBE buscar su propia regla aplicable según su `precio_nuevo`, entre `desde_precio` y `hasta_precio` inclusive.

#### Scenario: SCE-006 — Múltiples artículos con distintos precios

- GIVEN 3 artículos con precios_nuevo=50, 4327, y 9800, y reglas para rango [100-5000] (multiplo=100, arriba) y [5000-15000] (multiplo=1000, arriba)
- WHEN se procesan los 3 artículos
- THEN el precio_nuevo=50 queda sin cambio (sin regla para ese rango)
- AND el precio_nuevo=4327 se redondea a 4400 (regla de rango [100-5000])
- AND el precio_nuevo=9800 se redondea a 10000 (regla de rango [5000-15000])

### REQ-005: Export de funciones nuevas

`services/articulos/__init__.py` DEBE exportar `aplicar_redondeo` y `calcular_precio_comercial`.

#### Scenario: Funciones importables desde paquete

- GIVEN las funciones definidas en `redondeo.py`
- WHEN se importa desde `services.articulos`
- THEN ambas funciones están disponibles
