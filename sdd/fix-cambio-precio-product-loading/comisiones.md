# SDD — Sistema de Comisiones

## ERP SoftTech System

**Versión:** 1.0
**Fecha:** 2026-09-01
**Tecnologías:** Python + Flask + MySQL + HTML + CSS + JavaScript + Jinja2

---

# 1. Objetivo

Implementar en el ERP un módulo de **Comisiones** flexible y configurable que permita definir diferentes modelos de cálculo de comisiones y asignarlos a vendedores/usuarios.

El sistema debe permitir que un cliente pueda elegir entre diferentes modalidades de comisión sin necesidad de modificar código fuente.

El objetivo es que el ERP pueda soportar, entre otras, las siguientes modalidades:

* Comisión porcentual sobre venta.
* Comisión porcentual sobre venta neta.
* Comisión sobre margen.
* Comisión por artículo.
* Comisión por rubro.
* Comisión por marca.
* Comisión por tipo de artículo.
* Comisión por lista de precios.
* Comisión según descuento aplicado.
* Comisión según medio de pago.
* Comisión según entidad de tarjeta.
* Comisión por cantidad de unidades.
* Comisiones escalonadas por volumen de venta.
* Bonificaciones por cumplimiento de objetivos.
* Diferentes planes de comisión para diferentes vendedores.
* Diferentes planes de comisión para diferentes períodos.
* Posibilidad de cambiar de modelo de comisión sin perder el historial de liquidaciones anteriores.

El diseño debe ser extensible para permitir agregar nuevas modalidades en el futuro.

---

# 2. Principios generales

El módulo debe separar claramente:

```text
CONFIGURACIÓN
      ↓
PLAN DE COMISIONES
      ↓
REGLAS
      ↓
MOTOR DE CÁLCULO
      ↓
COMISIONES GENERADAS
      ↓
LIQUIDACIÓN
      ↓
PAGO
```

La configuración determina cómo se calcula la comisión.

El motor determina cuánto corresponde.

La liquidación congela los resultados correspondientes a un período.

---

# 3. Concepto de Plan de Comisión

Un **Plan de Comisión** representa un modelo completo de cálculo.

Ejemplos:

```text
Plan 1:
"Vendedor estándar"
5% sobre venta neta

Plan 2:
"Vendedor premium"
3% sobre margen

Plan 3:
"Comisión por producto"
Artículo A → 5%
Artículo B → 7%
Artículo C → 10%

Plan 4:
"Escala mensual"
Hasta $1.000.000 → 2%
$1.000.001 a $2.000.000 → 3%
Más de $2.000.000 → 5%
```

El sistema debe permitir tener múltiples planes activos.

---

# 4. Asignación de planes

Un usuario/vendedor podrá tener asignado un plan de comisión.

La asignación debe tener:

* Usuario.
* Plan.
* Fecha desde.
* Fecha hasta.
* Estado.

Ejemplo:

```text
Juan Pérez
Plan: Vendedor estándar
Desde: 01/01/2026
Hasta: 31/03/2026
```

Luego:

```text
Juan Pérez
Plan: Vendedor premium
Desde: 01/04/2026
Hasta: NULL
```

Esto permite cambiar el modelo de comisión sin alterar las liquidaciones históricas.

---

# 5. Historial

Nunca se debe recalcular una liquidación histórica utilizando las reglas actuales.

Ejemplo:

En enero Juan tenía:

```text
Plan A → 5%
```

En abril se cambia a:

```text
Plan B → 3% sobre margen
```

La liquidación de enero debe continuar mostrando el 5%.

Por este motivo, la liquidación debe almacenar el resultado calculado y no depender exclusivamente de las reglas actuales.

---

# 6. Relación con las ventas existentes

El sistema debe utilizar la estructura existente del ERP.

Relación principal:

```text
facturav
   │
   ├── idusuario
   ├── idcliente
   ├── idlista
   ├── idsucursal
   ├── fecha
   └── ...
        │
        ▼
     itemsv
        │
        ├── idarticulo
        ├── cantidad
        ├── precio_unitario
        ├── precio_total
        ├── bonificacion
        └── ...
             │
             ▼
         articulos
             │
             ├── idmarca
             ├── idrubro
             ├── idtipoarticulo
             └── costo
```

El vendedor se obtiene inicialmente desde:

```text
facturav.idusuario
```

Sin embargo, el diseño debe permitir en el futuro separar:

```text
usuario que registró la venta
```

de:

```text
vendedor responsable de la venta
```

si el negocio lo requiere.

---

# 7. Venta y cobranza

En el modelo actual del negocio, venta y cobranza suceden prácticamente en el mismo proceso.

Por lo tanto, inicialmente:

```text
VENTA
  ↓
COBRANZA
  ↓
COMISIÓN
```

La comisión se calculará sobre la operación realizada.

No se debe crear inicialmente una complejidad innecesaria de:

```text
venta generada
venta pendiente de cobro
comisión pendiente
comisión cobrada
```

Sin embargo, la arquitectura debe permitir incorporar esta separación posteriormente.

---

# 8. Base de cálculo

El plan de comisión debe permitir seleccionar la base utilizada para calcular la comisión.

Opciones iniciales:

### 8.1 Venta total

```text
comisión = total venta × porcentaje
```

### 8.2 Venta neta

```text
comisión = neto × porcentaje
```

### 8.3 Venta después de bonificaciones

```text
base = importe - bonificaciones
```

### 8.4 Margen

```text
margen = venta neta - costo
```

```text
comisión = margen × porcentaje
```

### 8.5 Cantidad

Ejemplo:

```text
$500 por unidad
```

```text
comisión = cantidad × importe_comisión
```

---

# 9. Costo histórico del artículo

Para soportar correctamente las comisiones basadas en margen, modificar `itemsv`.

Agregar:

```sql
costo_unitario DECIMAL(20,6) NOT NULL DEFAULT 0
```

Opcionalmente:

```sql
costo_total DECIMAL(20,6) NOT NULL DEFAULT 0
```

La idea es que al registrar una venta se copie el costo vigente del artículo.

Ejemplo:

```text
articulos.costo = $8.000
```

Venta:

```text
cantidad = 2
precio = $15.000
costo_unitario = $8.000
```

Posteriormente el costo del artículo puede cambiar:

```text
articulos.costo = $10.000
```

La venta histórica debe continuar teniendo:

```text
itemsv.costo_unitario = $8.000
```

De esta manera el cálculo histórico de margen es correcto.

---

# 10. Modalidades de comisión

El sistema debe contemplar una tabla de modalidades disponibles.

Ejemplo conceptual:

| Código            | Modalidad                 |
| ----------------- | ------------------------- |
| PORCENTAJE_VENTA  | % sobre venta             |
| PORCENTAJE_NETO   | % sobre neto              |
| PORCENTAJE_MARGEN | % sobre margen            |
| POR_ARTICULO      | % por artículo            |
| POR_RUBRO         | % por rubro               |
| POR_MARCA         | % por marca               |
| POR_TIPO_ARTICULO | % por tipo de artículo    |
| POR_LISTA         | % por lista de precios    |
| POR_DESCUENTO     | % según descuento         |
| POR_MEDIO_PAGO    | % según medio de pago     |
| POR_UNIDAD        | importe fijo por unidad   |
| ESCALONADA        | comisión por escala       |
| OBJETIVO          | comisión por cumplimiento |

Esta tabla permite que el sistema tenga un catálogo de modalidades.

No se debe hardcodear toda la lógica directamente en las rutas Flask.

---

# 11. Reglas de comisión

Un plan puede contener una o varias reglas.

Ejemplo:

```text
PLAN: Vendedor General

Regla 1:
Rubro = Indumentaria
Comisión = 5%

Regla 2:
Marca = Marca Premium
Comisión = 7%

Regla 3:
Descuento > 10%
Comisión = 2%
```

Las reglas deben permitir establecer criterios.

---

# 12. Criterios disponibles

Inicialmente se deben contemplar:

### Producto

```text
idarticulo
```

### Rubro

```text
articulos.idrubro
```

### Marca

```text
articulos.idmarca
```

### Tipo de artículo

```text
articulos.idtipoarticulo
```

### Lista de precios

```text
facturav.idlista
```

### Sucursal

```text
facturav.idsucursal
```

### Cliente

```text
facturav.idcliente
```

### Categoría de cliente

Utilizar la categoría existente en `clientes`.

### Descuento

Utilizar la bonificación existente en `itemsv`.

### Medio de pago

Utilizar la información existente de pagos.

### Entidad de tarjeta

Por ejemplo:

```text
Visa
Mastercard
```

La relación:

```text
tipo + entidad
```

solo debe utilizarse para tarjetas, de acuerdo con la estructura actual del ERP.

---

# 13. Prioridad de reglas

Cuando varias reglas puedan aplicarse al mismo artículo, el sistema debe tener una prioridad.

Ejemplo:

```text
Artículo específico       prioridad 100
Marca                     prioridad 80
Rubro                     prioridad 60
Tipo artículo             prioridad 40
Regla general             prioridad 10
```

Por defecto se debe aplicar la regla de mayor prioridad.

El sistema debe evitar aplicar accidentalmente múltiples porcentajes sobre la misma base salvo que el tipo de regla indique explícitamente que son acumulables.

---

# 14. Reglas acumulables

Una regla debe poder indicar si es:

```text
EXCLUSIVA
```

o:

```text
ACUMULABLE
```

Ejemplo:

```text
Comisión general: 3%
Bono por marca premium: +2%
```

Resultado:

```text
5%
```

Mientras que:

```text
Regla A: 5%
Regla B: 7%
```

podría significar que se debe utilizar solamente la de mayor prioridad.

---

# 15. Comisión por descuento

Debe permitirse configurar comisiones según el descuento aplicado.

Ejemplo:

|   Descuento | Comisión |
| ----------: | -------: |
|          0% |       5% |
|     1% a 5% |       4% |
| 5,01% a 10% |       2% |
|       > 10% |       0% |

La regla debe poder definir:

```text
desde_descuento
hasta_descuento
porcentaje
```

---

# 16. Comisión por medio de pago

Debe poder configurarse una comisión diferente según el medio de pago.

Ejemplo:

| Medio            | Comisión |
| ---------------- | -------: |
| Efectivo         |       5% |
| Débito           |       4% |
| Crédito          |       3% |
| Cuenta corriente |       2% |

En caso de tarjeta, podrá utilizarse además:

```text
entidad
```

Ejemplo:

```text
Crédito + Visa → 3%
Crédito + Mastercard → 2,5%
```

---

# 17. Comisión por margen

El cálculo debe utilizar el costo histórico almacenado en `itemsv`.

Ejemplo:

```text
Precio venta:       $20.000
Costo unitario:     $12.000
Cantidad:           2

Venta = $40.000
Costo = $24.000

Margen = $16.000
```

Si la comisión es:

```text
10%
```

entonces:

```text
Comisión = $1.600
```

La definición exacta de margen debe ser configurable y documentada.

---

# 18. Comisiones escalonadas

El sistema debe soportar escalas.

Ejemplo:

|      Desde |      Hasta |  % |
| ---------: | ---------: | -: |
|         $0 | $1.000.000 | 2% |
| $1.000.001 | $2.000.000 | 3% |
| $2.000.001 | sin límite | 5% |

Debe soportar dos modos diferentes.

### Modo A — Tasa alcanzada

Si el vendedor vende:

```text
$2.500.000
```

y alcanza el tercer tramo:

```text
$2.500.000 × 5%
```

### Modo B — Progresiva

```text
$1.000.000 × 2%
$1.000.000 × 3%
$500.000 × 5%
```

El plan debe almacenar cuál de los dos comportamientos utiliza.

---

# 19. Objetivos

Debe contemplarse una estructura para objetivos mensuales.

Ejemplo:

```text
Objetivo: $5.000.000

Ventas:
$4.500.000 → sin bono

Ventas:
$5.000.000 → bono 2%

Ventas:
$6.000.000 → bono 3%
```

Los objetivos deben poder estar asociados a:

* Usuario.
* Plan.
* Período.
* Sucursal.
* Monto.
* Cantidad de unidades.

Esta funcionalidad puede implementarse en una segunda etapa si no resulta necesaria para la primera versión.

---

# 20. Notas de crédito

Las Notas de Crédito deben **restar comisión**.

La identificación debe utilizar la estructura existente:

```text
facturav
    ↓
tipo_comprobantes
    ↓
tipo_comp_aplica
```

El motor debe identificar si el comprobante corresponde a:

```text
VENTA
NOTA DE CREDITO
NOTA DE DEBITO
```

Regla inicial:

```text
Venta              → comisión positiva
Nota de crédito    → comisión negativa
Nota de débito     → comisión positiva
```

Ejemplo:

Venta:

```text
$100.000
Comisión 5%
Comisión = $5.000
```

Nota de crédito:

```text
$20.000
Comisión 5%
Comisión = -$1.000
```

Comisión neta:

```text
$4.000
```

El detalle de comisión debe conservar la referencia al comprobante que originó el movimiento.

---

# 21. Liquidaciones

Una liquidación representa el cierre de un período de comisiones.

Tabla conceptual:

```text
comisiones_liquidaciones
```

Campos mínimos:

```text
id
periodo_desde
periodo_hasta
fecha_liquidacion
estado
total
observaciones
idusuario_creacion
fecha_creacion
fecha_modificacion
```

Estados:

```text
BORRADOR
CALCULADA
CONFIRMADA
PAGADA
ANULADA
```

---

# 22. Detalle de liquidación

Tabla:

```text
comisiones_detalle
```

Campos mínimos:

```text
id
id_liquidacion
id_usuario
id_factura
id_item
tipo_movimiento
tipo_comision
base_calculo
cantidad
costo_unitario
importe_venta
importe_costo
importe_margen
porcentaje
importe_comision
id_regla
observaciones
```

Esto permite conocer exactamente de dónde salió cada comisión.

---

# 23. Auditoría

El usuario debe poder consultar:

```text
Vendedor
    ↓
Liquidación
    ↓
Venta
    ↓
Artículo
    ↓
Regla aplicada
    ↓
Base de cálculo
    ↓
Porcentaje
    ↓
Comisión
```

Ejemplo:

```text
Juan Pérez

Venta: FC A 0001-00012345
Artículo: Camisa X
Cantidad: 2

Venta neta:       $50.000
Costo:            $30.000
Margen:           $20.000

Regla:
Marca Premium

Porcentaje:
7%

Comisión:
$1.400
```

---

# 24. Modelo de datos propuesto

Crear inicialmente las siguientes tablas:

```text
comisiones_planes
comisiones_reglas
comisiones_tramos
comisiones_asignaciones
comisiones_liquidaciones
comisiones_detalle
```

Opcionalmente:

```text
comisiones_objetivos
```

---

# 25. comisiones_planes

Propuesta:

```sql
CREATE TABLE comisiones_planes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    activo TINYINT(1) NOT NULL DEFAULT 1,
    fecha_desde DATE NOT NULL,
    fecha_hasta DATE NULL,
    tipo_calculo VARCHAR(30) NOT NULL,
    base_calculo VARCHAR(30) NOT NULL,
    modo_escalas VARCHAR(20) NULL,
    observaciones TEXT NULL,
    creado_por INT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_por INT NULL,
    fecha_actualizacion DATETIME NULL
);
```

Los valores de `tipo_calculo`, `base_calculo` y `modo_escalas` deben manejarse mediante constantes/catálogos del sistema y no mediante strings dispersos por el código.

---

# 26. comisiones_reglas

Propuesta conceptual:

```sql
CREATE TABLE comisiones_reglas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_plan INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    tipo_regla VARCHAR(40) NOT NULL,
    criterio VARCHAR(40) NULL,
    valor_criterio VARCHAR(100) NULL,
    porcentaje DECIMAL(10,6) NULL,
    importe_fijo DECIMAL(20,6) NULL,
    prioridad INT NOT NULL DEFAULT 0,
    acumulable TINYINT(1) NOT NULL DEFAULT 0,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    fecha_desde DATE NULL,
    fecha_hasta DATE NULL,
    FOREIGN KEY (id_plan) REFERENCES comisiones_planes(id)
);
```

La implementación final deberá adaptarse a las convenciones y tipos de datos ya utilizados en la base existente.

---

# 27. comisiones_tramos

```sql
CREATE TABLE comisiones_tramos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_plan INT NOT NULL,
    desde DECIMAL(20,6) NOT NULL,
    hasta DECIMAL(20,6) NULL,
    porcentaje DECIMAL(10,6) NOT NULL,
    importe_fijo DECIMAL(20,6) NULL,
    orden INT NOT NULL,
    FOREIGN KEY (id_plan) REFERENCES comisiones_planes(id)
);
```

---

# 28. comisiones_asignaciones

```sql
CREATE TABLE comisiones_asignaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_plan INT NOT NULL,
    fecha_desde DATE NOT NULL,
    fecha_hasta DATE NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    FOREIGN KEY (id_plan) REFERENCES comisiones_planes(id)
);
```

Debe impedirse tener dos planes activos para el mismo usuario durante el mismo período.

---

# 29. comisiones_liquidaciones

```sql
CREATE TABLE comisiones_liquidaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    periodo_desde DATE NOT NULL,
    periodo_hasta DATE NOT NULL,
    fecha_liquidacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) NOT NULL,
    total DECIMAL(20,6) NOT NULL DEFAULT 0,
    observaciones TEXT NULL,
    idusuario INT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

# 30. comisiones_detalle

```sql
CREATE TABLE comisiones_detalle (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_liquidacion INT NOT NULL,
    id_usuario INT NOT NULL,
    id_factura INT NOT NULL,
    id_item INT NULL,
    id_regla INT NULL,
    tipo_movimiento VARCHAR(20) NOT NULL,
    tipo_comision VARCHAR(40) NOT NULL,
    base_calculo DECIMAL(20,6) NOT NULL DEFAULT 0,
    cantidad DECIMAL(20,6) NOT NULL DEFAULT 0,
    costo_unitario DECIMAL(20,6) NOT NULL DEFAULT 0,
    importe_venta DECIMAL(20,6) NOT NULL DEFAULT 0,
    importe_costo DECIMAL(20,6) NOT NULL DEFAULT 0,
    importe_margen DECIMAL(20,6) NOT NULL DEFAULT 0,
    porcentaje DECIMAL(10,6) NOT NULL DEFAULT 0,
    importe_comision DECIMAL(20,6) NOT NULL DEFAULT 0,
    observaciones TEXT NULL,
    FOREIGN KEY (id_liquidacion)
        REFERENCES comisiones_liquidaciones(id)
);
```

---

# 31. Modificación de itemsv

Agregar:

```sql
ALTER TABLE itemsv
ADD COLUMN costo_unitario DECIMAL(20,6) NOT NULL DEFAULT 0;
```

El proceso de venta deberá copiar el costo vigente del artículo al momento de guardar el detalle.

Debe analizarse el código actual de ventas antes de implementar la modificación para asegurarse de que el valor se capture dentro de la misma transacción de venta.

---

# 32. Motor de comisiones

No implementar el cálculo dentro de las rutas Flask.

Crear una capa específica:

```text
comisiones/
    calculator.py
```

Clase principal:

```python
class CalculadorComisiones:
    def calcular_venta(self, venta):
        ...

    def calcular_item(self, venta, item, contexto):
        ...

    def obtener_plan(self, usuario, fecha):
        ...

    def obtener_reglas(self, plan):
        ...

    def aplicar_regla(self, regla, contexto):
        ...
```

---

# 33. Contexto de cálculo

Crear un objeto/contexto de cálculo que contenga la información necesaria.

Conceptualmente:

```python
contexto = {
    "venta": venta,
    "item": item,
    "articulo": articulo,
    "cliente": cliente,
    "usuario": usuario,
    "sucursal": sucursal,
    "lista_precio": lista_precio,
    "medio_pago": medio_pago,
    "entidad_pago": entidad_pago,
}
```

Esto evita que cada función tenga que consultar independientemente toda la información.

---

# 34. Resultado del cálculo

El motor no debe devolver únicamente un número.

Debe devolver información suficiente para auditoría.

Ejemplo conceptual:

```python
{
    "id_factura": 12345,
    "id_item": 55,
    "id_usuario": 8,
    "id_regla": 12,
    "tipo_comision": "PORCENTAJE_MARGEN",
    "base_calculo": 20000,
    "porcentaje": 7,
    "importe_comision": 1400,
}
```

---

# 35. Transacciones

El registro de la venta y la captura del costo histórico deben ejecutarse dentro de una transacción.

Ejemplo conceptual:

```text
BEGIN TRANSACTION

guardar facturav
guardar itemsv
    ↓
copiar costo actual de articulos
    ↓
guardar pagos
    ↓
COMMIT
```

Si algo falla:

```text
ROLLBACK
```

---

# 36. Idempotencia

El cálculo de comisiones debe ser idempotente.

No se debe permitir que una misma venta genere dos veces la misma comisión dentro de una misma liquidación.

Debe existir una restricción o mecanismo equivalente que permita identificar:

```text
liquidación + factura + item + regla
```

y evitar duplicados.

El diseño debe aprovechar, cuando corresponda, el concepto de `idempotency_key` que ya existe en `facturav`, pero no debe depender exclusivamente de él para identificar una comisión.

---

# 37. Anulación de liquidaciones

Una liquidación confirmada no debe modificarse directamente.

Si existe un error:

```text
Liquidación confirmada
        ↓
ANULAR
        ↓
Nueva liquidación corregida
```

Debe mantenerse el historial.

---

# 38. Interfaz Flask

Crear un Blueprint:

```text
comisiones_bp
```

Estructura:

```text
app/
    comisiones/
        __init__.py
        routes.py
        services.py
        calculator.py
        repositories.py
        models.py
        constants.py
        validators.py
```

Templates:

```text
templates/
    comisiones/
        index.html
        planes.html
        plan_form.html
        reglas.html
        asignaciones.html
        calcular.html
        liquidaciones.html
        liquidacion_detalle.html
        reportes.html
```

JavaScript:

```text
static/js/
    comisiones.js
```

---

# 39. Pantalla principal

Crear:

```text
Comisiones
```

Con acceso a:

```text
Planes de comisión
Reglas
Asignaciones
Objetivos
Calcular período
Liquidaciones
Reportes
```

---

# 40. Administración de planes

Debe permitir:

```text
Nuevo plan
Editar
Activar
Desactivar
Duplicar
Consultar
```

La opción **Duplicar** es importante.

Ejemplo:

```text
Plan "Vendedores 2026"
```

Duplicar:

```text
Plan "Vendedores 2027"
```

y modificar las reglas sin afectar el anterior.

---

# 41. Asignación de vendedores

Pantalla:

```text
Vendedor       Plan                  Desde       Hasta
------------------------------------------------------
Juan Pérez     Vendedor General      01/01/26    -
Pedro Gómez    Premium               01/01/26    -
Ana López      Escalonado             01/03/26    -
```

Debe existir validación de superposición de períodos.

---

# 42. Cálculo de período

Pantalla:

```text
Desde: [01/09/2026]
Hasta: [30/09/2026]

Vendedor: [Todos]

[ PREVISUALIZAR ]

[ CALCULAR LIQUIDACIÓN ]
```

Primero debe existir una etapa de previsualización.

El usuario debe poder ver:

```text
Vendedor
Ventas
Base
Comisión
Notas de crédito
Comisión neta
```

antes de confirmar.

---

# 43. Detalle de liquidación

Debe permitir expandir:

```text
Juan Pérez
    $150.000 comisión

        Venta 0001-000123
            Artículo A
            $50.000
            5%
            $2.500

        Venta 0001-000124
            Artículo B
            $100.000
            3%
            $3.000

        NC 0001-000020
            -$20.000
            -$600
```

---

# 44. Reportes

Crear inicialmente:

### Comisión por vendedor

```text
Vendedor
Ventas
Notas de crédito
Base
Comisión
```

### Comisión por período

```text
Mes
Ventas
Comisiones
```

### Comisión por artículo

```text
Artículo
Cantidad
Venta
Margen
Comisión
```

### Comisión por regla

```text
Regla
Aplicaciones
Venta
Comisión
```

---

# 45. Seguridad

Las funcionalidades deberán respetar el sistema actual de usuarios/perfiles del ERP.

Se recomienda diferenciar:

### Administrador

Puede:

* Crear planes.
* Modificar reglas.
* Asignar planes.
* Calcular liquidaciones.
* Confirmar liquidaciones.
* Anular liquidaciones.

### Supervisor

Puede:

* Consultar.
* Previsualizar.
* Calcular según permisos.

### Vendedor

Puede:

* Consultar sus propias comisiones.
* Consultar liquidaciones propias.

---

# 46. Reglas de negocio importantes

## Regla 1

Nunca utilizar el costo actual de `articulos` para calcular una comisión histórica basada en margen.

Utilizar:

```text
itemsv.costo_unitario
```

---

## Regla 2

Una Nota de Crédito debe generar una comisión negativa.

---

## Regla 3

Las liquidaciones confirmadas no deben recalcularse automáticamente.

---

## Regla 4

Cambiar un plan de comisión no debe modificar liquidaciones anteriores.

---

## Regla 5

No permitir asignaciones superpuestas para un mismo vendedor.

---

## Regla 6

Una venta no puede generar dos veces la misma comisión dentro de la misma liquidación.

---

## Regla 7

Toda comisión debe poder explicarse.

Es decir, debe ser posible responder:

```text
¿Por qué este vendedor cobró esta comisión?
```

mostrando:

```text
Plan
Regla
Base
Porcentaje
Venta
Artículo
Costo
Margen
Resultado
```

---

# 47. Arquitectura del código

Se debe evitar:

```text
routes.py
    ↓
1000 líneas de cálculo
```

Utilizar:

```text
routes
   ↓
service
   ↓
calculator
   ↓
repository
   ↓
database
```

Ejemplo:

```text
routes.py
    ↓
ComisionesService
    ↓
CalculadorComisiones
    ↓
ComisionesRepository
```

---

# 48. Separación de responsabilidades

### routes.py

Responsable de:

* HTTP.
* Validaciones básicas.
* Respuestas.
* Renderizado.
* Permisos.

### services.py

Responsable de:

* Procesos de negocio.
* Coordinación de operaciones.
* Transacciones.

### calculator.py

Responsable exclusivamente de:

* Determinar reglas.
* Calcular bases.
* Calcular porcentajes.
* Generar resultados.

### repositories.py

Responsable de:

* Consultas SQL.
* Inserciones.
* Actualizaciones.
* Recuperación de datos.

### constants.py

Responsable de:

* Tipos de comisión.
* Estados.
* Modos de escala.
* Tipos de movimiento.

---

# 49. SQL y rendimiento

El motor debe evitar realizar una consulta SQL por cada artículo.

No implementar:

```text
1000 artículos
↓
1000 consultas
```

Preferir:

```text
1 consulta de ventas
1 consulta de detalles
1 consulta de artículos
1 consulta de clientes
...
```

y trabajar con estructuras en memoria.

Se debe analizar la cantidad de registros esperada antes de optimizar prematuramente.

---

# 50. Índices

Analizar y agregar índices necesarios para:

```text
facturav.fecha
facturav.idusuario
facturav.idsucursal
facturav.idcliente
itemsv.idfactura
itemsv.idarticulo
comisiones_asignaciones.id_usuario
comisiones_asignaciones.fecha_desde
comisiones_asignaciones.fecha_hasta
comisiones_detalle.id_liquidacion
comisiones_detalle.id_usuario
comisiones_detalle.id_factura
```

Antes de crear índices duplicados, verificar los índices existentes.

---

# 51. Primera versión funcional

La primera versión debe implementar:

```text
1. Planes
2. Asignación de planes
3. Comisión % venta
4. Comisión % neto
5. Comisión % margen
6. Comisión por artículo
7. Comisión por rubro
8. Comisión por marca
9. Comisión por descuento
10. Notas de crédito negativas
11. Costo histórico
12. Cálculo por período
13. Liquidación
14. Detalle auditable
15. Reportes básicos
```

---

# 52. Segunda etapa

Agregar:

```text
Comisión por lista de precios
Comisión por tipo de artículo
Comisión por medio de pago
Comisión por entidad de tarjeta
Comisión por sucursal
Comisión por categoría de cliente
```

---

# 53. Tercera etapa

Agregar:

```text
Objetivos
Escalas
Bonificaciones
Aceleradores
Comisiones progresivas
Bonos especiales
```

---

# 54. Cuarta etapa

Preparar:

```text
Comisión por cobranza diferida
Cuenta corriente
Comisiones pendientes
Comisiones pagadas
Integración con pagos
```

No implementar esta complejidad en la primera versión si el flujo actual de venta/cobranza ocurre simultáneamente.

---

# 55. Pruebas

Crear pruebas unitarias para cada modalidad.

Casos mínimos:

### Comisión básica

```text
Venta = 100.000
Comisión = 5%

Resultado = 5.000
```

### Comisión sobre neto

```text
Neto = 80.000
5%

Resultado = 4.000
```

### Comisión sobre margen

```text
Venta = 100.000
Costo = 70.000
Margen = 30.000
10%

Resultado = 3.000
```

### Nota de crédito

```text
Venta = 100.000
5% = 5.000

NC = 20.000
5% = -1.000

Resultado = 4.000
```

### Cambio de plan

Verificar que una modificación del plan no altere liquidaciones históricas.

### Escala

Verificar tanto:

```text
Tasa alcanzada
```

como:

```text
Progresiva
```

### Descuento

Verificar correctamente los límites:

```text
0%
5%
5,01%
10%
10,01%
```

### Costo histórico

Verificar que modificar `articulos.costo` después de una venta no modifique el margen histórico.

---

# 56. Migraciones

No modificar directamente la estructura productiva sin generar una migración SQL.

La migración inicial debe contemplar:

```text
ALTER itemsv
ADD costo_unitario
```

y la creación de:

```text
comisiones_planes
comisiones_reglas
comisiones_tramos
comisiones_asignaciones
comisiones_liquidaciones
comisiones_detalle
```

Las migraciones deben poder ejecutarse de manera segura más de una vez o detectar previamente si las estructuras ya existen.

---

# 57. Compatibilidad con el ERP existente

Antes de implementar cambios, analizar:

```text
estructura actual de itemsv
flujo de ventas
flujo de notas de crédito
flujo de pagos
usuarios
perfiles
clientes
listas de precio
articulos
rubros
marcas
tipo_articulos
medios de pago
```

No reemplazar funcionalidades existentes.

El módulo debe integrarse con la arquitectura actual.

---

# 58. Regla fundamental del diseño

El motor no debe asumir que existe una única forma de calcular comisiones.

Debe trabajar conceptualmente así:

```text
VENDEDOR
   ↓
PLAN
   ↓
REGLAS
   ↓
CONTEXTO DE VENTA
   ↓
MOTOR
   ↓
RESULTADO
```

Esto permite que en el futuro un cliente pueda decir:

> "Quiero utilizar el modelo de comisión A."

y posteriormente:

> "A partir del mes próximo quiero utilizar el modelo B."

sin modificar el código.

---

# 59. Ejemplo completo

Plan:

```text
"Vendedores Premium"
```

Regla:

```text
Base: Margen
Comisión: 10%
```

Venta:

```text
Artículo: Camisa
Cantidad: 2
Precio: $25.000
Costo histórico: $15.000
```

Cálculo:

```text
Venta = 2 × 25.000
      = 50.000

Costo = 2 × 15.000
      = 30.000

Margen = 50.000 - 30.000
       = 20.000

Comisión = 20.000 × 10%
         = 2.000
```

Posteriormente:

```text
Nota de crédito
Cantidad: 1
```

Entonces:

```text
Venta NC = 25.000
Costo NC = 15.000

Margen NC = 10.000

Comisión NC = -1.000
```

Resultado:

```text
Comisión neta = 1.000
```

---

# 60. Criterio de implementación

El agente de VSCode debe:

1. Analizar primero el proyecto existente.
2. Identificar la estructura actual de Flask.
3. Identificar Blueprints existentes.
4. Identificar patrón actual de acceso a MySQL.
5. Identificar modelos/repositorios existentes.
6. Identificar estructura exacta de `facturav` e `itemsv`.
7. Identificar cómo se guardan actualmente las ventas.
8. Identificar cómo se guardan las notas de crédito.
9. Identificar cómo se guardan los pagos.
10. Identificar los perfiles/permisos actuales.
11. No asumir nombres de campos que no hayan sido verificados.
12. No modificar código existente sin analizar primero su impacto.
13. Crear el módulo de comisiones respetando las convenciones existentes.
14. Crear migraciones SQL.
15. Implementar primero la infraestructura.
16. Implementar posteriormente el motor.
17. Implementar luego las interfaces.
18. Implementar pruebas.
19. Verificar integración con ventas y notas de crédito.

---

# 61. Orden recomendado de implementación

## Fase 1 — Base de datos

Implementar:

```text
costo_unitario en itemsv

comisiones_planes
comisiones_reglas
comisiones_tramos
comisiones_asignaciones
comisiones_liquidaciones
comisiones_detalle
```

---

## Fase 2 — Backend

Implementar:

```text
Blueprint
Repositories
Services
Calculator
Validators
Constants
```

---

## Fase 3 — Motor básico

Implementar:

```text
% venta
% neto
% margen
por artículo
por rubro
por marca
por descuento
```

---

## Fase 4 — Notas de crédito

Implementar:

```text
venta → +
nota de crédito → -
```

y pruebas correspondientes.

---

## Fase 5 — Interfaz

Implementar:

```text
Planes
Reglas
Asignaciones
Cálculo
Liquidaciones
Detalle
Reportes
```

---

## Fase 6 — Pruebas

Crear pruebas unitarias y de integración.

---

## Fase 7 — Funciones avanzadas

Posteriormente:

```text
listas de precio
medios de pago
entidades
objetivos
escalas
bonos
aceleradores
```

---

# 62. Resultado esperado

Al finalizar la primera versión, el usuario debe poder:

```text
1. Crear un plan de comisión.

2. Elegir cómo calcularlo.

3. Definir reglas.

4. Asignarlo a un vendedor.

5. Registrar ventas normalmente.

6. Calcular las comisiones de un período.

7. Visualizar cómo se calculó cada comisión.

8. Aplicar notas de crédito como comisión negativa.

9. Generar una liquidación.

10. Confirmar la liquidación.

11. Consultar posteriormente la liquidación sin que
    cambios futuros en las reglas modifiquen el resultado.
```

---

# 63. Restricciones

No hacer:

* Cálculos de comisión directamente en templates.
* Cálculos complejos dentro de rutas Flask.
* Dependencia del costo actual del artículo para liquidaciones históricas.
* Recalcular automáticamente liquidaciones confirmadas.
* Duplicar comisiones.
* Hardcodear porcentajes.
* Hardcodear un único modelo de comisión.
* Modificar ventas históricas al cambiar un plan.
* Crear consultas SQL innecesarias por cada artículo.

---

# 64. Consideración final de arquitectura

El sistema debe quedar preparado para evolucionar desde:

```text
COMISIÓN SIMPLE
```

hacia:

```text
MOTOR DE COMISIONES
```

sin tener que rediseñar posteriormente toda la base de datos.

La prioridad inicial es construir una base sólida, auditable y flexible antes que intentar implementar todas las modalidades posibles en la primera versión.

El código debe privilegiar:

```text
claridad
mantenibilidad
trazabilidad
extensibilidad
integridad transaccional
```

por encima de soluciones rápidas o excesivamente complejas.
