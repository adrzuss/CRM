# Comisiones — Specification

## Purpose

Módulo configurable de comisiones para el ERP: planes con reglas flexibles, cálculo por período, liquidaciones con trazabilidad completa, notas de crédito negativas, costo histórico, acceso por roles.

---

## Data Model

### ALTER itemsv

```sql
ALTER TABLE itemsv ADD costo_unitario DECIMAL(20,6) NOT NULL DEFAULT 0;
```

### 6 Tables

| Table | PK | Key Columns | Purpose |
|-------|----|-------------|---------|
| `comisiones_planes` | id | nombre, tipo_calculo, base_calculo, modo_escalas, activo, fecha_desde/hasta | Plan de comisión con configuración de cálculo |
| `comisiones_reglas` | id | id_plan→planes, tipo_regla, criterio, valor_criterio, porcentaje, importe_fijo, prioridad, acumulable | Reglas que un plan aplica al cálculo |
| `comisiones_tramos` | id | id_plan→planes, desde, hasta, porcentaje, importe_fijo, orden | Escalas de comisión por volumen |
| `comisiones_asignaciones` | id | id_usuario, id_plan→planes, fecha_desde, fecha_hasta, activo | Asignación temporal de plan a vendedor |
| `comisiones_liquidaciones` | id | periodo_desde, periodo_hasta, estado, total, idusuario | Cierre de período de comisiones |
| `comisiones_detalle` | id | id_liquidacion→liquidaciones, id_usuario, id_factura, id_item, id_regla→reglas, tipo_movimiento, tipo_comision, base_calculo, porcentaje, importe_comision | Trazabilidad de cada comisión calculada |

**Constraints:**
- `UNIQUE(id_liquidacion, id_factura, id_item, id_regla)` en detalle → idempotencia
- `FOREIGN KEY` en reglas→planes, tramos→planes, asignaciones→planes, detalle→liquidaciones
- Estados liquidación: BORRADOR → CALCULADA → CONFIRMADA → PAGADA → ANULADA

---

## Functional Requirements

| ID | Requirement | Scenario |
|----|-------------|----------|
| FR-01 | CRUD de planes: crear, editar, activar/desactivar, duplicar | GIVEN un admin WHEN duplica un plan THEN se crea copia con reglas/tramos |
| FR-02 | Reglas con prioridad: mayor prioridad se aplica primero, flag acumulable | GIVEN regla 100 (marca) y 60 (rubro) WHEN calcula THEN aplica marca |
| FR-03 | Modalidades v1: %venta, %neto, %margen, por artículo, rubro, marca, descuento | GIVEN un plan con regla de rubro WHEN procesa venta THEN aplica % al rubro del artículo |
| FR-04 | Escalas: tasa alcanzada o progresiva, configurada en plan | GIVEN escala 0-1M→2%, 1M-2M→3%, >2M→5% modo alcanzada, venta $2.5M THEN comisión = $2.5M × 5% |
| FR-05 | Asignación temporal: sin superposición para mismo vendedor | GIVEN vendedor con plan vigente 01/01-31/03 WHEN asigna 15/02-30/06 THEN validación rechaza |
| FR-06 | Costo histórico: itemsv.costo_unitario copiado al registrar venta | GIVEN artículo con costo $8.000 WHEN se vende 2 unidades THEN itemsv.costo_unitario = $8.000 |
| FR-07 | Notas de crédito generan comisión negativa | GIVEN venta $100K comisión 5% y NC $20K THEN comisión neta = $4.000 |
| FR-08 | Cálculo por período con previsualización | GIVEN período 01/09-30/09 WHEN previsualiza THEN muestra vendedor, ventas, base, comisión, NC |
| FR-09 | Liquidación inmutable: confirmada no se recalcula | GIVEN liquidación CONFIRMADA WHEN modifica plan THEN liquidación mantiene valores originales |
| FR-10 | Idempotencia: misma factura+item+regla no duplica en liquidación | GIVEN item ya procesado WHEN reintenta THEN se omite (UNIQUE constraint) |
| FR-11 | Detalle auditable completo | GIVEN comisión calculada WHEN consulta THEN muestra plan, regla, base, %, venta, costo, margen, resultado |
| FR-12 | Roles: admin (CRUD+calcular+confirmar), supervisor (consulta+previsualizar), vendedor (sus datos) | GIVEN vendedor WHEN consulta liquidaciones THEN solo ve las propias |

---

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | Queries batch: 1 consulta ventas, 1 items, 1 artículos, 1 clientes — sin N+1 |
| NFR-02 | Índices en: facturav.fecha, facturav.idusuario, itemsv.idfactura, comisiones_asignaciones.id_usuario+fecha_desde, comisiones_detalle.id_liquidacion+id_usuario+id_factura |
| NFR-03 | Transacción única para venta + costo_unitario (BEGIN → guardar facturav → itemsv con costo → COMMIT/ROLLBACK) |
| NFR-04 | Motor de cálculo separado de rutas (calculator.py recibe contexto, devuelve resultado auditado) |
| NFR-05 | Compatible con ventas, notas de crédito y pagos existentes (no romper flujo actual) |

---

## Business Rules

| ID | Rule |
|----|------|
| BR-01 | Nunca usar articulos.costo actual para comisiones históricas; usar itemsv.costo_unitario |
| BR-02 | Nota de crédito → comisión negativa; nota de débito → comisión positiva |
| BR-03 | Liquidaciones confirmadas NO se recalculan automáticamente |
| BR-04 | Cambiar plan no modifica liquidaciones anteriores |
| BR-05 | No permitir asignaciones superpuestas para mismo vendedor en mismo período |
| BR-06 | Una venta no puede generar dos veces la misma comisión dentro de la misma liquidación |
| BR-07 | Toda comisión debe poder explicarse: plan, regla, base, %, venta, artículo, costo, margen, resultado |

---

## API / Service Specs

| Layer | Module | Responsibility |
|-------|--------|----------------|
| Routes | `routes/comisiones.py` → `bp_comisiones` | HTTP, validación básica, permisos, renderizado |
| Services | `services/comisiones/planes.py` | CRUD planes, reglas, tramos, duplicar |
| Services | `services/comisiones/asignaciones.py` | Asignar/desasignar vendedores, validar superposición |
| Services | `services/comisiones/liquidaciones.py` | Procesar período, previsualizar, confirmar, anular |
| Calculator | `services/comisiones/calculator.py` | `CalculadorComisiones`: calcular_venta(), calcular_item(), obtener_plan(), obtener_reglas(), aplicar_regla() |
| Repositories | `services/comisiones/repositories.py` | Queries batch (ventas, items, artículos, clientes) |
| Constants | `services/comisiones/constants.py` | Tipos comisión, estados liquidación, modos escala |
| Validators | `services/comisiones/validators.py` | Superposición, reglas, permisos |

---

## UI Specs

| Screen | Templates | Key Features |
|--------|-----------|--------------|
| Index | `comisiones/index.html` | Acceso a: Planes, Reglas, Asignaciones, Calcular, Liquidaciones, Reportes |
| Planes CRUD | `comisiones/planes.html`, `plan_form.html` | Listar, nuevo, editar, activar/desactivar, duplicar |
| Reglas | `comisiones/reglas.html` | CRUD reglas por plan, selector de tipo/criterio |
| Asignaciones | `comisiones/asignaciones.html` | Asignar vendedor a plan con fechas, validación superposición |
| Calcular | `comisiones/calcular.html` | Selector período, vendedor, previsualizar, calcular liquidación |
| Liquidaciones | `comisiones/liquidaciones.html` | Listar con estados, expandir detalle por vendedor |
| Detalle | `comisiones/liquidacion_detalle.html` | Trazabilidad: vendedor → venta → artículo → regla → base → comisión |
| Reportes | `comisiones/reportes.html` | Por vendedor, período, artículo, regla |

---

## Migration Specs

1. `SQL/001_alter_itemsv_costo_unitario.sql` — ALTER TABLE itemsv ADD costo_unitario
2. `SQL/002_create_comisiones_planes.sql` — CREATE TABLE + índices
3. `SQL/003_create_comisiones_reglas.sql` — CREATE TABLE + FK
4. `SQL/004_create_comisiones_tramos.sql` — CREATE TABLE + FK
5. `SQL/005_create_comisiones_asignaciones.sql` — CREATE TABLE + FK + UNIQUE
6. `SQL/006_create_comisiones_liquidaciones.sql` — CREATE TABLE
7. `SQL/007_create_comisiones_detalle.sql` — CREATE TABLE + FK + UNIQUE(id_liquidacion,id_factura,id_item,id_regla)

Cada script debe ser idempotente (IF NOT EXISTS).

---

## Rollback Criteria

1. **DB**: Script inverso DROP TABLE comisiones_* + ALTER TABLE itemsv DROP COLUMN costo_unitario
2. **Code**: Revert commits en orden: templates → routes → services → models → index.py
3. **Sales flow**: Columna costo_unitario DEFAULT 0 no afecta ventas existentes
4. **Liquidaciones**: Inmutables; rollback no borra datos históricos
