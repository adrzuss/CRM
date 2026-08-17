# Tablero de Ventas

## Propósito

Render del tablero gerencial (`/tablero-inicial`): muestra métricas de ventas en tarjetas y 3 gráficos Chart.js (barras de ventas de los últimos 6 meses, doughnut de ingresos de hoy y 2 pies de ventas por rubros). Los scripts inline que asignan los datos de los gráficos MUST ejecutarse bajo la política CSP con nonce, y las consultas de reporte MUST degradar sin romper la página.

## Requirements

### Requirement: Scripts inline autorizados por la CSP

Los scripts inline de `tablero.html` que asignan los datos de los gráficos (`mesess`/`eventoss`, `tipoPagos`/`cantPagos`, `nombresRubros`/`ventasRubros`, `nombresRubros`/`cantidadRubros`) MUST incluir el nonce emitido por el servidor para la respuesta actual y MUST ejecutarse sin ser bloqueados por la Content-Security-Policy.

#### Scenario: Gráficos con datos bajo CSP

- GIVEN una sesión autenticada que navega a `/tablero-inicial`
- WHEN el servidor responde con la política `script-src 'self' 'nonce-...'` y los scripts inline llevan el nonce válido
- THEN los 4 scripts inline se ejecutan y las variables de datos quedan asignadas
- AND los gráficos `barrasEventos`, `myPieChart`, `myPieChart2` y `myPieChart3` se renderizan con los datos provistos

#### Scenario: Período sin ventas

- GIVEN la consulta de reporte devuelve listas vacías para el período
- WHEN la página se renderiza y los scripts inline se ejecutan
- THEN los gráficos se renderizan vacíos sin lanzar errores
- AND la página permanece operativa

### Requirement: Degradación del reporte de rubros

La consulta de ventas por rubros MUST NOT provocar un error HTTP 500 en `/tablero-inicial`. Si la consulta falla (error SQL, stored procedure ausente, etc.), la ruta SHALL renderizar la página con listas vacías para `rubros`, `vtaRubros` y `cantRubros`.

#### Scenario: Stored procedure de rubros falla

- GIVEN la consulta `venta_rubros` lanza un error en la base de datos
- WHEN el usuario navega a `/tablero-inicial`
- THEN la respuesta es HTTP 200 (no 500)
- AND los gráficos de rubros se renderizan vacíos
- AND las tarjetas y los demás gráficos muestran datos normalmente

#### Scenario: Consulta de rubros exitosa

- GIVEN la consulta `venta_rubros` devuelve resultados
- WHEN el usuario navega a `/tablero-inicial`
- THEN `myPieChart2` y `myPieChart3` se renderizan con los rubros, montos y cantidades devueltos

### Requirement: Sin gráfico sobre canvas inexistente

El JavaScript del tablero MUST NOT intentar crear un gráfico sobre un canvas que no existe en la página (`barrasRubros`). La eliminación de ese código SHALL NOT afectar la creación de los demás gráficos.

#### Scenario: Carga sin error de consola

- GIVEN la página del tablero con los 3 gráficos declarados en el template
- WHEN se cargan los scripts de Chart.js
- THEN no se registra el error "Failed to create chart: can't acquire context from the given item"
- AND `barrasEventos`, `myPieChart`, `myPieChart2` y `myPieChart3` se crean correctamente

### Requirement: Tableros existentes sin regresión

Los cambios SHALL NOT alterar el comportamiento de los tableros que comparten o reutilizan la misma superficie (`tablero_administrativo`, `tablero_basico`) ni de las tarjetas de métricas del tablero gerencial.

#### Scenario: Tableros administrativo y básico intactos

- GIVEN las rutas `/tablero-administrativo` y `/tablero-basico`
- WHEN se renderizan después del cambio
- THEN responden sin errores nuevos y muestran sus datos como antes

#### Scenario: Tarjetas de métricas sin cambios

- GIVEN `/tablero-inicial` con datos de ventas, créditos y saldos
- WHEN la página se renderiza
- THEN las tarjetas de ventas de hoy/semana, créditos y saldos de clientes/proveedores siguen mostrando sus valores