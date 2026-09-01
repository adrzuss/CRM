# Delta for Dashboard Gerencial Stage 1

## MODIFIED Requirements

### F1: Filtros Globales

The system SHALL provide filters: Período (desde/hasta, default últimos 30 días), Sucursal (select, default `session['id_sucursal']`, opción "Todas"), Comparar con período anterior (toggle, default off).

| Parameter | Type | Default | Validation |
|-----------|------|---------|------------|
| `desde` | date | hoy - 30 días | `>= 2020-01-01` |
| `hasta` | date | hoy | `<= hoy`, `>= desde` |
| `id_sucursal` | int | `session['id_sucursal']` | FK sucursales.id, NULL = todas |
| `comparar` | bool | false | — |

**Comparison period**: `desde_ant = desde - (hasta - desde + 1) días`, `hasta_ant = desde - 1 día`.

**Sucursal query**: The `get_sucursales_lista()` query SHALL include all active sucursales — those where `baja IS NULL` OR `baja = '0000-00-00 00:00:00'`. Rows with zero-date `baja` are considered active (historical data from ORM default).

**Keyboard shortcuts**: Alt+H (Hoy), Alt+S (Sem), Alt+M (Mes), Alt+T (Trim) SHALL update date inputs AND trigger form submit to reload the dashboard. The shortcuts SHALL NOT update dates without also dispatching the submit event.

(Previously: Query was `WHERE baja IS NULL` only; keyboard shortcuts called `setRangoFechas()` without dispatching form submit)

#### Scenario: Sucursal query includes zero-date baja rows

- GIVEN sucursales in DB: id=1 (`baja=NULL`), id=2 (`baja='0000-00-00 00:00:00'`), id=3 (`baja='2025-01-15 10:00:00'`)
- WHEN dashboard renders
- THEN dropdown shows sucursales id=1 and id=2
- AND sucursal id=3 (inactive) is excluded

#### Scenario: Keyboard shortcut updates dates and submits

- GIVEN dashboard filter form with default date range
- WHEN user presses Alt+M
- THEN date inputs update to last 30 days
- AND form submits (page reloads with new dates)
- AND dashboard content reflects the new date range

#### Scenario: Sucursal selection filters all queries

- GIVEN sucursal "Central" con id=1
- WHEN usuario selecciona sucursal y hace click en "Actualizar"
- THEN todas las queries filtran `WHERE f.idsucursal = 1`
- AND el dashboard muestra solo datos de esa sucursal

#### Scenario: Todas las sucursales

- WHEN usuario selecciona "Todas" en filtro sucursal
- THEN no se aplica filtro `idsucursal` en las queries
- AND se muestran datos agregados de todas las sucursales

---

## ADDED Requirements

### F1-FIX: Modelo de Sucursales — Default `baja`

The system SHALL default `baja = None` (NULL) for new `Sucursales` records created via the ORM `__init__` constructor. Previously, `__init__` set `self.baja = timedelta(0)` which stored a zero-date instead of NULL.

(Previously: `self.baja = timedelta(0)` — records created via ORM had non-NULL baja that was excluded by the old query)

#### Scenario: New sucursal created via ORM has baja = NULL

- GIVEN a new Sucursales record created with `Sucursales(nombre, dir, tel, email)`
- WHEN the record is committed to the database
- THEN `baja` column contains NULL
- AND the record appears in the dropdown query

#### Scenario: Existing zero-date rows still included

- GIVEN existing sucursales with `baja = '0000-00-00 00:00:00'` (created before this fix)
- WHEN the dropdown query runs
- THEN these rows ARE included (the query handles both NULL and zero-date)
- AND no data migration is required
