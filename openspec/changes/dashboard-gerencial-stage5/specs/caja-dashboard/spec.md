# Caja Dashboard — Specification (Stage 5)

## Purpose

KPIs y rendiciones recientes de caja chica en el dashboard gerencial. Fuente: `rendiciones_caja`. Filtra por sucursal (tiene `idsucursal`).

---

## Requirements

### F26: KPIs Caja

The system SHALL compute 3 metrics from `rendiciones_caja`:

| KPI | Formula |
|-----|---------|
| Total efectivo rendido | `SUM(total_efectivo)` en período |
| Total otros valores | `SUM(total_otros_valores)` en período |
| Cantidad rendiciones | `COUNT(id)` en período |

**Parámetros**: `desde`, `hasta`, `id_sucursal` (opcional).

**Query**:
```sql
SELECT
  COALESCE(SUM(rc.total_efectivo), 0) AS total_efectivo,
  COALESCE(SUM(rc.total_otros_valores), 0) AS total_otros_valores,
  COUNT(rc.id) AS cantidad_rendiciones
FROM rendiciones_caja rc
WHERE rc.fecha BETWEEN :desde AND :hasta
  [AND rc.idsucursal = :id_sucursal]
```

**Display**: 2 KPI cards — Total Efectivo ($), Rendiciones del Mes (count badge). Total otros valores se muestra como sub-dato.

#### Scenario: Rendiciones con filtro sucursal

- GIVEN 3 rendiciones en sucursal 1 ($50000, $30000, $20000 efectivo)
- WHEN `id_sucursal = 1`
- THEN total_efectivo = $100.000,00
- AND cantidad_rendiciones = 3

#### Scenario: Sin rendiciones en período

- GIVEN no hay rendiciones en el período seleccionado
- WHEN se consultan KPIs
- THEN total_efectivo = $0, total_otros_valores = $0, cantidad_rendiciones = 0
- AND widget muestra "No hay rendiciones en este período"

---

### F27: Rendiciones Recientes

The system SHALL return the last N rendiciones ordered by fecha DESC.

**Parámetros**: `limite` (default 10), `id_sucursal` (opcional).

**Query**:
```sql
SELECT
  rc.fecha,
  u.nombre AS usuario,
  s.nombre AS sucursal,
  rc.total_ventas,
  rc.total_efectivo,
  rc.total_otros_valores
FROM rendiciones_caja rc
JOIN usuarios u ON rc.idusuario = u.id
JOIN sucursales s ON rc.idsucursal = s.id
WHERE 1=1
  [AND rc.idsucursal = :id_sucursal]
ORDER BY rc.fecha DESC
LIMIT :limite
```

**Display**: Tabla con columnas Fecha, Usuario, Sucursal, Total Ventas, Efectivo, Otros Valores. Valores formateados como moneda.

#### Scenario: Últimas 10 rendiciones

- GIVEN 15 rendiciones en la base
- WHEN se piden rendiciones recientes (limite=10)
- THEN se muestran 10 filas ordenadas por fecha DESC
- AND la más reciente aparece primera

#### Scenario: Rendición sin usuario

- GIVEN rendición con `idusuario` que no existe en `usuarios`
- WHEN se consulta
- THEN el JOIN falla silenciosamente y la rendición no aparece (INNER JOIN)
- AND no se inventa nombre de usuario

---

## Edge Cases

| Case | Behavior |
|------|----------|
| `rendiciones_caja` vacía | KPIs = 0, tabla "No hay rendiciones recientes" |
| Solo 1 rendición en mes | KPIs muestran esa rendición, tabla con 1 fila |
| Filtro sucursal sin rendiciones | "No hay rendiciones en este período" |
| `total_otros_valores = 0` | Se muestra $0,00 (sin omitir la columna) |
