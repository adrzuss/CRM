# PROMPT MASTER — DASHBOARD GERENCIAL ERP

## 1. ROL

Actúa como un desarrollador senior especializado en:

- Python
- Flask
- Jinja2
- HTML5
- CSS3
- JavaScript ES6+
- Chart.js
- MySQL 8 / MariaDB
- SQL
- Diseño de dashboards empresariales
- Arquitectura backend/frontend
- Sistemas ERP
- Análisis de información comercial y financiera

Tu objetivo es implementar un nuevo Dashboard Gerencial dentro de una aplicación ERP existente.

IMPORTANTE:

NO debes asumir que el proyecto está vacío.

Antes de modificar código debes analizar cuidadosamente la estructura existente del proyecto, sus Blueprints, rutas, templates, servicios, modelos, consultas SQL, conexión a base de datos, sistema de autenticación, permisos y componentes frontend existentes.

Debes reutilizar la arquitectura existente siempre que sea posible.

NO debes introducir frameworks nuevos si no son necesarios.

La aplicación utiliza principalmente:

- Python
- Flask
- HTML
- CSS
- JavaScript
- Chart.js
- MySQL

---

# 2. OBJETIVO GENERAL

Construir un Dashboard Gerencial moderno, claro y orientado a la toma de decisiones.

El dashboard debe responder principalmente:

1. ¿Cómo están las ventas?
2. ¿Cómo evolucionan respecto de períodos anteriores?
3. ¿Cuánto dinero se está cobrando?
4. ¿Cómo se está cobrando?
5. ¿Qué productos/rubros generan las ventas?
6. ¿Qué sucursales funcionan mejor?
7. ¿Qué vendedores venden más?
8. ¿Qué clientes concentran las ventas?
9. ¿Qué productos tienen mayor rotación?
10. ¿Qué productos tienen problemas de stock?
11. ¿Cómo está la rentabilidad?
12. ¿Cuánto se debe cobrar?
13. ¿Cuánto se debe pagar?
14. ¿Cómo está la situación de créditos otorgados?
15. ¿Cuál es la situación bancaria?
16. ¿Existen señales de alerta que requieran atención?

El dashboard NO debe convertirse simplemente en una colección de gráficos.

Debe funcionar como una herramienta de análisis gerencial.

---

# 3. PRINCIPIO FUNDAMENTAL

Diferenciar claramente:

VENTAS
≠
COBRANZAS
≠
RENTABILIDAD
≠
STOCK
≠
CUENTAS CORRIENTES
≠
CRÉDITOS
≠
MOVIMIENTOS BANCARIOS

No mezclar estos conceptos.

Por ejemplo:

Una factura de venta por $100.000 no significa necesariamente que se hayan cobrado $100.000.

Puede haber sido:

- efectivo
- tarjeta
- cuenta corriente
- crédito
- vale
- combinación de medios de pago

Por lo tanto:

VENTA FACTURADA

debe analizarse independientemente de:

DINERO COBRADO.

---

# 4. ESTRUCTURA DE BASE DE DATOS DISPONIBLE

La aplicación utiliza MySQL.

Las principales tablas involucradas son:

## Ventas

### facturav

Campos relevantes:

- id
- idcliente
- idlista
- fecha
- total
- neto
- bonificacion
- iva
- exento
- impint
- idtipocomprobante
- idsucursal
- idusuario
- nro_comprobante
- punto_vta
- cae
- cae_vto
- fecha_emision
- idempotency_key

### itemsv

Campos:

- idfactura
- id
- idarticulo
- cantidad
- id_color
- id_detalle
- precio_unitario
- precio_total
- neto
- bonificacion
- iva
- idalciva
- ingbto
- idingbto
- exento
- impint
- idoferta

### pagos_fv

Campos:

- idfactura
- idpago
- tipo
- total
- entidad

---

# 5. COMPRAS

## facturac

Campos:

- id
- idproveedor
- fecha
- periodo
- total
- neto
- iva
- exento
- impint
- pagpersepcuenta
- mto_percep
- percep_iibb
- idsucursal
- idtipocomprobante
- idusuario
- idplancuenta
- nro_comprobante

## itemsc

Campos:

- idfactura
- id
- idarticulo
- cantidad
- precio_unitario
- precio_total
- neto
- iva
- idalciva
- exento
- impint
- id_color
- id_detalle

## pagos_fc

Campos:

- idfactura
- idpago
- tipo
- total

---

# 6. ARTÍCULOS

## articulos

Campos relevantes:

- id
- codigo
- detalle
- costo
- idiva
- exento
- impint
- idib
- idmarca
- idrubro
- idtipoarticulo
- imagen
- es_compuesto
- pedir_en_ventas
- costo_total
- baja
- con_colores
- con_talles
- alta

Los artículos se relacionan con:

- rubros
- marcas
- tipos de artículo
- listas de precios

---

# 7. STOCK

## stocks

Campos:

- idstock
- idarticulo
- idsucursal
- actual
- maximo
- deseable
- en_transito_entrada
- en_transito_salida

El stock es independiente por sucursal.

Los movimientos de stock provienen principalmente de:

- ventas
- compras
- remitos entre sucursales

IMPORTANTE:

No asumir que `stocks.actual` contiene el historial.

Es el estado actual del stock.

Para análisis históricos de movimiento deben utilizarse las tablas de operaciones correspondientes.

---

# 8. PRECIOS

## precios

Campos:

- idlista
- idarticulo
- precio
- ult_modificacion

Existe un sistema de listas de precios.

Actualmente el sistema utiliza markup para definir precios.

NO presentar el markup como si fuera necesariamente margen real.

Si se calcula margen, utilizar:

margen = venta - costo

y

margen_porcentual =
((venta - costo) / venta) * 100

siempre que los datos disponibles permitan realizar ese cálculo correctamente.

Si el costo utilizado no permite calcular una rentabilidad histórica confiable, indicarlo claramente.

NO inventar costos históricos.

---

# 9. CLIENTES

## clientes

Campos relevantes:

- id
- nombre
- documento
- email
- telefono
- direccion
- idlocalidad
- idprovincia
- ctacte
- baja
- idcategoria
- id_tipo_doc
- id_tipo_iva

La mayoría de las ventas se realizan al cliente utilizado como:

CONSUMIDOR FINAL

Por este motivo:

NO utilizar simplemente cantidad de ventas por cliente como principal indicador de concentración de clientes.

Siempre que sea posible mostrar separadamente:

- consumidor final
- clientes identificados

Esto permitirá analizar mejor la cartera comercial.

---

# 10. PROVEEDORES

## proveedores

Campos relevantes:

- id
- nombre
- fantasia
- email
- telefono
- documento
- direccion
- id_tipo_doc
- id_tipo_iva

---

# 11. SUCURSALES

## sucursales

Campos:

- id
- nombre
- direccion
- telefono
- email
- alta
- baja

El sistema maneja una sola empresa pero puede tener múltiples sucursales.

Todos los indicadores que correspondan deben poder filtrarse por sucursal.

---

# 12. USUARIOS / VENDEDORES

## usuarios

Campos:

- id
- nombre
- usuario
- clave
- documento
- email
- telefono
- direccion

Un usuario puede actuar también como vendedor.

Las ventas almacenan:

`facturav.idusuario`

Por lo tanto se puede analizar:

- ventas por vendedor
- cantidad de operaciones
- ticket promedio
- evolución
- participación sobre ventas

---

# 13. COMPROBANTES

## tipo_comprobantes

Campos:

- id
- id_afip
- nombre
- letra
- discrimina_iva

## tipo_comp_aplica

Relaciona:

- tipo de IVA
- tipo de comprobante
- tipo de operación

## tipo_operacion

Valores conocidos:

1 = VENTA
2 = COMPRA
3 = CREDITO
4 = DEBITO
5 = REMITO
6 = RECIBO
7 = PRESUPUESTO

IMPORTANTE:

No asumir que todo registro de `facturav` debe contabilizarse automáticamente como venta positiva.

Los tipos de comprobante y tipo de operación deben utilizarse para determinar correctamente el sentido de la operación.

Las notas de crédito/devoluciones generan ventas negativas.

---

# 14. PAGOS DE VENTAS

## pagos_fv

Campos:

- idfactura
- idpago
- tipo
- total
- entidad

El campo `tipo` y `entidad` se utilizan principalmente cuando el pago corresponde a tarjeta u otros medios donde interesa identificar la entidad.

Ejemplos:

- VISA
- MASTERCARD
- MERCADO PAGO
- etc.

No asumir que `entidad` representa siempre un medio de pago.

---

# 15. NOTAS DE CRÉDITO / VALES

Las notas de crédito/devoluciones generan operaciones negativas.

Una nota de crédito puede utilizarse posteriormente como medio de pago de una factura.

En el dashboard debe evitarse:

- contabilizar dos veces la misma operación
- interpretar un vale como ingreso de efectivo
- interpretar una nota de crédito como dinero cobrado

Cuando sea necesario analizar cobranzas, separar:

- efectivo
- tarjetas
- otros medios
- cuenta corriente
- crédito
- vales/notas de crédito

---

# 16. CAJA

## rendiciones_caja

Campos:

- id
- fecha
- idusuario
- idpunto_vta
- idsucursal
- idtipo_rendicion
- total_ventas
- total_efectivo
- total_otros_valores

## items_rendiciones_caja

Campos:

- id
- idrendicion
- idmoneda_billete
- cantidad

Tipos de rendición:

1 = Apertura
2 = Rendición
3 = Cierre

Una misma fecha puede tener varias rendiciones para:

- cajero
- punto de venta
- sucursal

El cierre permite analizar:

- efectivo cobrado
- efectivo rendido
- diferencia
- otros valores

No asumir que una rendición equivale necesariamente al total diario de la sucursal.

---

# 17. CUENTAS CORRIENTES DE PROVEEDORES

## cta_cte_prov

Campos:

- id
- idproveedor
- fecha
- debe
- haber
- idfactura

La cuenta corriente funciona como:

DEBE = deuda

HABER = pago / cancelación

Debe analizarse:

saldo = SUM(debe) - SUM(haber)

---

# 18. CUENTAS CORRIENTES DE CLIENTES

Existe una estructura equivalente para cuentas corrientes de clientes.

El concepto es:

DEBE = deuda del cliente

HABER = pagos

Debe analizarse:

saldo = SUM(debe) - SUM(haber)

Los vencimientos dependen de los movimientos y reglas existentes del sistema.

No inventar fechas de vencimiento si la estructura existente no las proporciona directamente.

---

# 19. CRÉDITOS

## creditos

Campos:

- id
- idsucursal
- idcliente
- idplan
- cuotas
- monto_total
- estado
- fecha_solicitud
- fecha_inicio
- fecha_fin
- idfactura
- observaciones

## planes_creditos

Campos:

- id
- nombre
- descripcion
- tasa_interes
- cuotas
- anticipo
- garantes
- baja

## estados_creditos

Campos:

- id
- nombre
- descripcion

## vencimientos_creditos

Campos:

- id
- idcredito
- numero_cuota
- fecha_vencimiento
- monto

## pagos_creditos

Campos:

- id
- idcredito
- idvencimiento
- idfactura
- fecha_pago
- monto
- punitorios

El sistema permite otorgar créditos a clientes y posteriormente cobrar cuotas.

El dashboard debe poder analizar:

- créditos otorgados
- créditos activos
- créditos cancelados
- créditos pendientes
- cuotas vencidas
- cuotas próximas a vencer
- monto vencido
- cobranzas de créditos
- morosidad

No inventar el significado de los valores de `estado`.

Consultar la tabla `estados_creditos`.

---

# 20. BANCOS

## bancos

Representa las cuentas bancarias de la empresa.

## bancos_propios

Representa movimientos bancarios propios.

Campos relevantes:

- id
- fecha_emision
- fecha_vencimiento
- tipo_movimiento
- nro_movimiento
- monto
- id_banco
- baja

## banco_propio_proveedor

Relaciona cheques propios con proveedores.

Tipos de movimientos bancarios:

1 = Cheque — D
2 = Depósito — C
3 = Transferencia — D
4 = Débitos — D
5 = Créditos — C
6 = Extracción — D
7 = Impuestos — D
8 = Cred. IVA — C
9 = Otros débitos — D

D = débito

C = crédito

El dashboard debe distinguir:

- ingresos bancarios
- egresos bancarios
- cheques emitidos
- transferencias
- débitos
- créditos
- impuestos
- movimientos futuros según fecha de vencimiento cuando corresponda

---

# 21. PAGOS A PROVEEDORES

Los pagos a proveedores se realizan mediante órdenes de pago.

Las órdenes de pago se almacenan utilizando `facturac`.

La relación con las facturas a cancelar se encuentra en:

## items_op

Campos:

- idop
- id
- idfactura
- pago

No asumir que toda `facturac` representa una compra.

Utilizar la información de tipo de comprobante / operación para distinguir operaciones.

---

# 22. OBJETIVOS DEL DASHBOARD GERENCIAL

El dashboard debe tener una estructura visual aproximadamente como:

---------------------------------------------------------
HEADER
---------------------------------------------------------

Filtros globales:

[ Período ] [ Sucursal ] [ Comparar con ] [ Actualizar ]

---------------------------------------------------------
KPIs PRINCIPALES
---------------------------------------------------------

VENTAS

$ XXX

↑ 12,5%

vs período anterior


COBRANZAS

$ XXX

↑ 8,2%


MARGEN

$ XXX

XX %


TICKET PROMEDIO

$ XXX


---------------------------------------------------------
VENTAS
---------------------------------------------------------

Gráfico:

VENTAS POR DÍA / SEMANA / MES

Comparación con período anterior.

---------------------------------------------------------

VENTAS POR SUCURSAL

---------------------------------------------------------

VENTAS POR RUBRO

---------------------------------------------------------

TOP PRODUCTOS

---------------------------------------------------------

TOP VENDEDORES

---------------------------------------------------------

STOCK
---------------------------------------------------------

Productos bajo mínimo

Productos sin stock

Productos con exceso de stock

---------------------------------------------------------

CUENTAS POR COBRAR
---------------------------------------------------------

Saldo clientes

Vencido

Por vencer

---------------------------------------------------------

CUENTAS POR PAGAR
---------------------------------------------------------

Saldo proveedores

Vencido

Por vencer

---------------------------------------------------------

CRÉDITOS
---------------------------------------------------------

Créditos activos

Monto colocado

Cuotas vencidas

Monto vencido

---------------------------------------------------------

BANCOS
---------------------------------------------------------

Saldo / movimientos

Cheques próximos a vencer

---------------------------------------------------------

ALERTAS GERENCIALES
---------------------------------------------------------

⚠ Productos sin stock

⚠ Clientes con deuda vencida

⚠ Proveedores próximos a vencer

⚠ Diferencias de caja

⚠ Cuotas de crédito vencidas

⚠ Cheques próximos a vencer

---------------------------------------------------------

# 23. FILTROS GLOBALES

El dashboard debe permitir seleccionar:

## Período

Opciones sugeridas:

- Hoy
- Ayer
- Últimos 7 días
- Este mes
- Mes anterior
- Últimos 3 meses
- Últimos 6 meses
- Este año
- Año anterior
- Personalizado

## Sucursal

- Todas
- Sucursal individual

## Comparación

Cuando corresponda:

- período anterior
- mismo período año anterior

El filtro debe afectar todos los widgets compatibles.

---

# 24. KPIs PRINCIPALES

Implementar inicialmente:

## KPI 1 — Ventas

Ventas netas del período seleccionado.

Debe considerar correctamente:

- ventas
- notas de crédito
- operaciones negativas

Mostrar:

valor actual

valor período comparativo

variación porcentual

---

## KPI 2 — Cantidad de operaciones

Cantidad de operaciones de venta válidas.

Evitar contar notas de crédito como una venta positiva.

---

## KPI 3 — Ticket promedio

Ticket promedio:

ventas netas / cantidad de operaciones

Debe documentarse exactamente qué operaciones forman parte del cálculo.

---

## KPI 4 — Cobranzas

Monto cobrado mediante pagos asociados a ventas.

NO confundir con facturación.

---

## KPI 5 — Margen

Siempre que pueda calcularse correctamente:

margen = ventas - costo

Mostrar:

- margen monetario
- margen %

Si no existe información histórica suficiente para determinar el costo real de cada venta, NO inventarlo.

En ese caso implementar el KPI como una primera aproximación utilizando el costo disponible y dejar documentada la limitación.

---

# 25. GRÁFICO DE EVOLUCIÓN DE VENTAS

Implementar con Chart.js.

Debe poder cambiar entre:

- diario
- semanal
- mensual

Debe mostrar:

período actual

y opcionalmente:

período comparativo

Ejemplo:

Ventas
│
│             █
│       █     █
│   █   █     █
│ █ █   █ █   █
└────────────────

No utilizar gráficos 3D.

Mantener diseño limpio.

---

# 26. VENTAS POR SUCURSAL

Mostrar:

- importe
- cantidad de operaciones
- ticket promedio
- participación %

Idealmente mediante:

gráfico de barras horizontal.

Permitir ordenar de mayor a menor.

---

# 27. VENTAS POR RUBRO

Mostrar:

- ventas por importe
- cantidad de unidades
- participación %

No limitarse a una torta.

Preferir:

- barras
- ranking
- porcentaje

La torta puede mantenerse como visual complementario.

---

# 28. TOP PRODUCTOS

Mostrar:

Top 10 productos por:

- facturación
- cantidad vendida
- margen cuando sea posible

Permitir cambiar el criterio.

Mostrar:

Código

Producto

Cantidad

Venta

Margen

---

# 29. TOP VENDEDORES

Para cada usuario que tenga ventas:

- nombre
- ventas
- cantidad de operaciones
- ticket promedio
- participación %

Mostrar ranking.

---

# 30. CLIENTES

Separar:

CONSUMIDOR FINAL

de:

CLIENTES IDENTIFICADOS

Mostrar:

- ventas a consumidor final
- ventas a clientes identificados
- concentración de ventas
- top clientes

Para clientes identificados:

Top 10 clientes por facturación.

---

# 31. STOCK

El dashboard debe mostrar:

## Sin stock

Cantidad de artículos:

actual <= 0

## Bajo mínimo

Cuando exista un mínimo válido:

actual < mínimo

## Stock saludable

actual entre mínimo y máximo

## Exceso

actual > máximo

No inventar mínimos.

Utilizar únicamente los campos disponibles:

- actual
- maximo
- deseable
- en_transito_entrada
- en_transito_salida

---

# 32. STOCK POR SUCURSAL

Mostrar:

Sucursal

Unidades

Valor estimado del stock

Artículos sin stock

Artículos bajo mínimo

Cuando se calcule valor de stock:

valor_stock = cantidad * costo

Documentar que se utiliza el costo actual si no existe histórico.

---

# 33. PRODUCTOS SIN MOVIMIENTO

Si la estructura disponible permite identificar correctamente la última venta:

Mostrar productos que:

- tienen stock
- pero no registran ventas durante determinado período

Ejemplo:

Sin ventas en:

30 días

60 días

90 días

Esto es importante para detectar stock inmovilizado.

---

# 34. CUENTAS POR COBRAR

Mostrar:

Saldo total clientes

Saldo vencido

Saldo por vencer

Cantidad de clientes con deuda

Top deudores

Debe poder identificarse:

- deuda corriente
- deuda vencida

No inventar vencimientos.

Utilizar las tablas reales del sistema.

---

# 35. CUENTAS POR PAGAR

Mostrar:

Saldo proveedores

Vencido

Por vencer

Top proveedores

Debe considerar:

facturas

pagos

órdenes de pago

cuenta corriente

No contar una orden de pago como una compra.

---

# 36. CRÉDITOS

Mostrar:

Monto total otorgado

Créditos activos

Créditos cancelados

Cantidad de créditos

Saldo pendiente

Cuotas vencidas

Monto vencido

Próximos vencimientos

Utilizar:

creditos

vencimientos_creditos

pagos_creditos

planes_creditos

estados_creditos

---

# 37. BANCOS

Mostrar:

- movimientos de crédito
- movimientos de débito
- cheques emitidos
- cheques próximos a vencer
- transferencias
- débitos
- impuestos

Separar movimientos por banco.

No asumir que `bancos_propios` representa necesariamente el saldo bancario completo si no existen todos los movimientos necesarios.

Si el saldo no puede determinarse de manera confiable:

mostrar únicamente movimientos disponibles.

---

# 38. CAJA

Mostrar cuando exista información suficiente:

Ventas del día

Efectivo cobrado

Otros valores

Efectivo rendido

Diferencia

Cantidad de cierres

Diferencias de caja

Una diferencia distinta de cero debe poder aparecer como alerta.

---

# 39. ALERTAS GERENCIALES

Crear un componente de alertas.

Ejemplos:

🔴 Productos sin stock

🟠 Productos bajo mínimo

🔴 Clientes con deuda vencida

🟠 Proveedores con vencimientos próximos

🔴 Cuotas de crédito vencidas

🟠 Cheques próximos a vencer

🔴 Diferencias de caja

Las alertas deben ser accionables.

Idealmente cada alerta debe permitir hacer click y acceder al módulo correspondiente.

---

# 40. ARQUITECTURA BACKEND

Preferir una arquitectura similar a:

/dashboard
    /routes
    /services
    /queries
    /templates
    /static

o adaptar esta estructura a la existente.

No crear una nueva arquitectura si el proyecto ya posee una estructura equivalente.

Separar:

ROUTES

de

LÓGICA DE NEGOCIO

de

CONSULTAS SQL

de

PRESENTACIÓN

---

# 41. API DEL DASHBOARD

Preferentemente crear endpoints específicos.

Ejemplo conceptual:

GET /dashboard/gerencial

GET /api/dashboard/gerencial/resumen

GET /api/dashboard/gerencial/ventas

GET /api/dashboard/gerencial/productos

GET /api/dashboard/gerencial/stock

GET /api/dashboard/gerencial/clientes

GET /api/dashboard/gerencial/proveedores

GET /api/dashboard/gerencial/creditos

GET /api/dashboard/gerencial/bancos

La implementación final debe adaptarse a la arquitectura existente.

No crear múltiples endpoints innecesarios si una respuesta agregada es más eficiente.

---

# 42. RESPUESTA JSON

La API debe devolver información estructurada.

Ejemplo conceptual:

{
    "success": true,
    "filters": {
        "desde": "2026-01-01",
        "hasta": "2026-08-29",
        "sucursal": null
    },
    "resumen": {
        "ventas": 1000000,
        "variacion_ventas": 12.5,
        "operaciones": 450,
        "ticket_promedio": 2222.22,
        "cobranzas": 950000,
        "margen": 250000,
        "margen_porcentaje": 25
    }
}

Adaptar el formato al estándar utilizado actualmente por el proyecto.

---

# 43. JAVASCRIPT

Utilizar JavaScript moderno.

No utilizar código inline innecesariamente.

Crear funciones independientes.

Ejemplo conceptual:

loadDashboard()

loadResumen()

loadVentas()

loadStock()

loadClientes()

loadProveedores()

loadCreditos()

loadBancos()

updateCharts()

destroyCharts()

IMPORTANTE:

Antes de crear un Chart.js nuevo, destruir el existente si corresponde.

Evitar duplicación de gráficos al cambiar filtros.

---

# 44. CHART.JS

Utilizar Chart.js.

Priorizar:

- barras
- líneas
- doughnut
- barras horizontales

Evitar:

- 3D
- gráficos excesivamente decorativos
- exceso de colores
- gráficos sin información accionable

Los gráficos deben ser legibles en escritorio.

Preparar el diseño para responsive.

---

# 45. RENDIMIENTO

El dashboard puede consultar grandes cantidades de información.

IMPORTANTE:

NO realizar:

SELECT * FROM facturav

para luego procesar todo en Python.

Las agregaciones deben realizarse principalmente en MySQL.

Utilizar:

SUM()

COUNT()

AVG()

GROUP BY

CASE

JOIN

CTE cuando sea compatible con la versión de MySQL utilizada.

Evitar consultas N+1.

Evitar ejecutar una consulta por cada producto.

Evitar ejecutar una consulta por cada sucursal.

Evitar ejecutar una consulta por cada vendedor.

Preferir consultas agregadas.

---

# 46. ÍNDICES

Antes de crear nuevos índices:

1. revisar los índices existentes
2. analizar las consultas
3. verificar si realmente hacen falta

No crear índices innecesarios.

Posibles campos relevantes:

facturav.fecha

facturav.idsucursal

facturav.idusuario

facturav.idcliente

facturav.idtipocomprobante

itemsv.idarticulo

facturac.fecha

facturac.idproveedor

facturac.idsucursal

stocks.idarticulo

stocks.idsucursal

creditos.fecha_solicitud

vencimientos_creditos.fecha_vencimiento

pagos_creditos.fecha_pago

bancos_propios.fecha_emision

bancos_propios.fecha_vencimiento

---

# 47. SEGURIDAD

El dashboard debe respetar el sistema de autenticación existente.

No exponer información a usuarios no autorizados.

Si el proyecto tiene sistema de permisos:

utilizarlo.

No crear un sistema paralelo de autenticación.

Nunca devolver:

- contraseñas
- claves
- datos sensibles innecesarios

---

# 48. MULTI-SUCURSAL

Aunque actualmente exista una sola empresa:

el sistema tiene múltiples sucursales.

Por lo tanto:

toda consulta que corresponda a operaciones comerciales debe contemplar:

idsucursal

El filtro:

Todas las sucursales

debe funcionar correctamente.

Cuando se selecciona una sucursal:

todos los widgets compatibles deben respetar ese filtro.

---

# 49. FECHAS

Utilizar siempre fechas provenientes de la base de datos.

No realizar cálculos de fechas importantes exclusivamente en JavaScript.

El backend debe recibir:

desde

hasta

y opcionalmente:

sucursal

El backend debe validar las fechas.

---

# 50. MANEJO DE ERRORES

Todas las APIs deben devolver errores controlados.

Ejemplo:

{
    "success": false,
    "error": "No se pudo obtener la información del dashboard"
}

No devolver HTML ante un error de una API JSON.

Registrar errores en backend según el mecanismo existente.

No mostrar excepciones SQL al usuario.

---

# 51. ESTADOS VACÍOS

Todos los gráficos deben contemplar:

- sin datos
- período sin ventas
- sucursal sin movimientos
- ausencia de stock
- ausencia de créditos

Nunca mostrar un gráfico roto.

Mostrar mensajes como:

"No hay datos para el período seleccionado."

---

# 52. FORMATO DE MONEDA

La aplicación trabaja con valores monetarios.

Utilizar formato consistente.

Ejemplo:

$ 1.250.450,50

Evitar mostrar demasiados decimales.

La base puede tener DECIMAL(20,6), pero el dashboard normalmente debe mostrar:

2 decimales

salvo que exista una razón específica.

---

# 53. VARIACIONES

Cuando exista comparación:

variación % =

((actual - anterior) / anterior) * 100

Si anterior = 0:

no generar división por cero.

Mostrar:

"N/D"

o equivalente.

---

# 54. EXPERIENCIA VISUAL

El dashboard debe transmitir:

- información
- jerarquía
- claridad
- profesionalismo

No debe parecer una página de reportes antigua.

Debe existir una jerarquía visual clara:

1. KPIs
2. evolución
3. análisis comercial
4. stock
5. cuentas
6. créditos
7. bancos
8. alertas

Mantener coherencia con el estilo visual existente de la aplicación.

NO reemplazar globalmente el CSS existente.

---

# 55. RESPONSIVE

Debe funcionar correctamente en:

- escritorio
- notebook
- tablet

En móvil no es necesario que todos los gráficos sean idénticos, pero la información debe seguir siendo usable.

---

# 56. INTERACTIVIDAD

Los widgets deberían permitir, cuando sea razonable:

- cambiar período
- cambiar sucursal
- cambiar métrica
- ordenar
- ver detalle

Ejemplo:

Top productos:

[Facturación ▼]

opciones:

- Facturación
- Cantidad
- Margen

---

# 57. DRILL-DOWN

Una característica deseable.

Cuando el usuario haga click sobre:

una sucursal

un vendedor

un rubro

un producto

un cliente

debería ser posible eventualmente navegar al módulo correspondiente.

No implementar navegación si no existe una ruta adecuada.

En ese caso dejar la estructura preparada.

---

# 58. DASHBOARD GERENCIAL — PRIORIDAD

No intentar implementar absolutamente todos los widgets de una sola vez.

Implementar por etapas.

## ETAPA 1

Construir:

- filtros
- KPIs
- evolución de ventas
- ventas por sucursal
- ventas por rubro
- top productos
- top vendedores

## ETAPA 2

Agregar:

- stock
- productos sin stock
- productos bajo mínimo
- productos sin movimiento

## ETAPA 3

Agregar:

- cuentas por cobrar
- cuentas por pagar

## ETAPA 4

Agregar:

- créditos
- morosidad
- vencimientos

## ETAPA 5

Agregar:

- bancos
- cheques
- caja
- diferencias

## ETAPA 6

Agregar:

- alertas
- drill-down
- mejoras UX

---

# 59. IMPORTANTE — NO INVENTAR DATOS

Si una métrica no puede calcularse correctamente con la estructura existente:

NO inventar una solución.

Informar:

"Este indicador requiere información que actualmente no está disponible."

Ejemplos:

- costo histórico exacto
- saldo bancario real si faltan movimientos
- vencimiento exacto si no existe información suficiente

Proponer alternativas, pero no inventar datos.

---

# 60. NO MODIFICAR TABLAS SIN JUSTIFICACIÓN

Antes de agregar columnas o tablas:

analizar si realmente son necesarias.

El objetivo inicial es construir el dashboard utilizando las estructuras existentes.

Si se detecta una mejora estructural:

documentarla por separado.

NO modificar automáticamente el modelo de datos.

---

# 61. TRAZABILIDAD

Cada indicador importante debe poder rastrearse hasta su origen.

Por ejemplo:

Ventas

→ facturav

→ itemsv

→ articulos

→ rubros

Cobranzas

→ facturav

→ pagos_fv

Stock

→ stocks

Créditos

→ creditos

→ vencimientos_creditos

→ pagos_creditos

Proveedores

→ cta_cte_prov

Compras

→ facturac

→ itemsc

Bancos

→ bancos_propios

Caja

→ rendiciones_caja

Esto es importante para poder validar los resultados.

---

# 62. VALIDACIÓN DE RESULTADOS

Antes de considerar terminado cada indicador:

comparar el resultado del dashboard contra consultas SQL directas.

Ejemplo:

Si el dashboard muestra:

Ventas = $5.250.000

debe existir una consulta SQL equivalente que permita verificar ese resultado.

Crear consultas de validación durante el desarrollo.

---

# 63. DOCUMENTACIÓN

Al finalizar cada etapa:

documentar:

- archivos creados
- archivos modificados
- endpoints
- consultas SQL principales
- indicadores
- fórmula utilizada
- tablas utilizadas
- limitaciones

---

# 64. FLUJO DE TRABAJO OBLIGATORIO

Antes de escribir código:

## PASO 1

Analizar el proyecto.

Identificar:

- estructura Flask
- Blueprints
- rutas
- templates
- CSS
- JavaScript
- conexión MySQL
- autenticación
- permisos

## PASO 2

Identificar si ya existe:

- dashboard
- componentes Chart.js
- funciones JS reutilizables
- helpers de moneda
- manejo de fechas
- sistema de filtros
- componentes Bootstrap

## PASO 3

Proponer los cambios.

NO modificar todavía.

## PASO 4

Implementar la ETAPA 1.

## PASO 5

Probar.

## PASO 6

Validar SQL contra datos reales.

## PASO 7

Corregir.

## PASO 8

Continuar con la siguiente etapa.

---

# 65. REGLA ESPECIAL PARA EL AGENTE

Si encuentras una estructura existente que ya resuelve una necesidad:

REUTILÍZALA.

No reemplaces código funcional simplemente para implementar tu propia arquitectura.

No cambies:

- autenticación
- conexión a DB
- sistema de usuarios
- estilos globales
- estructura de navegación

salvo que sea estrictamente necesario.

---

# 66. REGLA ESPECIAL PARA SQL

No escribir consultas SQL suponiendo nombres de tablas o campos que no fueron proporcionados.

Si necesitas una tabla adicional:

primero identificarla en el proyecto.

Si no existe:

informar que falta información.

No crear una tabla de reemplazo sin autorización.

---

# 67. RESULTADO ESPERADO

El resultado final debe ser un:

DASHBOARD GERENCIAL ERP

que permita a un responsable de la empresa entender rápidamente:

- cuánto vende
- cuánto cobra
- qué vende
- dónde vende
- quién vende
- qué productos funcionan
- qué productos están inmovilizados
- cuánto le deben
- cuánto debe
- cuánto tiene colocado en créditos
- cuánto tiene vencido
- qué ocurre en bancos
- qué ocurre en caja
- cuáles son los principales problemas

El dashboard debe priorizar:

INFORMACIÓN ACCIONABLE

sobre:

INFORMACIÓN DECORATIVA.

---

# 68. PRIMERA TAREA DEL AGENTE

NO empieces inmediatamente a programar.

Primero analiza el proyecto actual.

Genera un informe breve indicando:

1. Estructura del proyecto.
2. Blueprint relacionado con el dashboard.
3. Template actual del dashboard.
4. Archivos JavaScript relacionados.
5. Archivos CSS relacionados.
6. Cómo se conecta actualmente a MySQL.
7. Cómo se autentican los usuarios.
8. Qué componentes Chart.js ya existen.
9. Qué código puede reutilizarse.
10. Qué archivos deberían modificarse.
11. Qué archivos nuevos propones crear.
12. Qué información adicional necesitas.

Después propone un PLAN DE IMPLEMENTACIÓN DE LA ETAPA 1.

NO ejecutes cambios estructurales importantes sin explicar primero qué vas a modificar.

---

# 69. CRITERIO FINAL

La prioridad es:

CORRECCIÓN DE LOS DATOS

antes que:

DISEÑO

y:

DISEÑO

antes que:

ANIMACIONES / EFECTOS.

Un dashboard bonito con información incorrecta es peor que un dashboard sencillo con información correcta.

Siempre priorizar:

1. exactitud
2. trazabilidad
3. rendimiento
4. mantenibilidad
5. claridad visual
6. experiencia de usuario

FIN DEL PROMPT MASTER