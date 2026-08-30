# Design: Aplicar Redondeo en Cambio de Precio

## Technical Approach

Intercept the `precio_nuevo` calculation in `obtenerArticulosMarcaRubro()` (articulos.py:305) to apply commercial rounding rules from `ReglaRedondeo`. The rounding logic is extracted into a pure-function module (`redondeo.py`) with no DB dependency, keeping it testable in isolation. Rules are queried once per request before the article loop, converted to dicts, and passed to the calculation function.

## Architecture Decisions

### Decision: Pure functions in separate module

**Choice**: Create `services/articulos/redondeo.py` with two pure functions: `aplicar_redondeo()` and `calcular_precio_comercial()`.

**Alternatives considered**:
- Method on `ReglaRedondeo` model — couples rounding logic to ORM, harder to unit test
- Inline in `obtenerArticulosMarcaRubro` — violates single responsibility, untestable

**Rationale**: Pure functions are trivially testable without DB mocks. Separation matches the existing services pattern where business logic lives in service functions, not models.

### Decision: Query rules once, convert to dicts

**Choice**: Query `ReglaRedondeo.query.filter_by(activo=True)` once before the loop, convert to `list[dict]`, pass to `calcular_precio_comercial()`.

**Alternatives considered**:
- Query per article — N+1 queries, unacceptable for large article sets
- Cache in `current_app.config` — premature optimization; rules change rarely but cache invalidation is complex

**Rationale**: Single query is sufficient (<20 rules typical). Dict conversion decouples the rounding module from SQLAlchemy entirely. If performance becomes an issue later, cache is a straightforward addition.

### Decision: Fallback passthrough when no rule matches

**Choice**: If no rule matches `desde_precio <= precio_nuevo <= hasta_precio`, return `round(precio_teorico, 2)` unchanged.

**Alternatives considered**:
- Raise error — breaks existing workflow when rules aren't fully configured
- Require at least one rule — same problem; partial configuration is a valid state

**Rationale**: Backward compatible. Current behavior (no rounding) is preserved when no rules exist or when a price falls outside all ranges. This matches REQ-003/SCE-007.

### Decision: `math.ceil`/`math.floor` with float conversion

**Choice**: Use `math.ceil`/`math.floor` on `float` for the rounding calculation, not `Decimal`-native operations.

**Alternatives considered**:
- Pure `Decimal` arithmetic — more precise but `Decimal` lacks `ceil`/`floor` without quantize gymnastics

**Rationale**: The rounding multiplo is always an integer (100, 1000, etc.) and prices are 2-decimal. Float precision is sufficient for this calculation. The final result is returned as-is (already a clean multiple of the integer multiplo).

## Data Flow

```
obtenerArticulosMarcaRubro(marca, rubro, lista_precio, porcentaje)
  │
  ├─ 1. ReglaRedondeo.query.filter_by(activo=True)  ← ONE DB query
  │
  ├─ 2. Convert to list of dicts:
  │     [{desde_precio, hasta_precio, multiplo, tipo_redondeo, restar_unidades}, ...]
  │
  ├─ 3. For each article:
  │     │
  │     ├─ precio_nuevo = precio_actual * (1 + porcentaje/100)
  │     │
  │     └─ calcular_precio_comercial(precio_nuevo, porcentaje, reglas_dict)
  │           │
  │           ├─ Buscar regla: desde_precio <= precio_teorico <= hasta_precio
  │           │
  │           ├─ Si encontrada → aplicar_redondeo(precio_teorico, multiplo, tipo, restar)
  │           │
  │           └─ Si no        → round(precio_teorico, 2)  [sin cambios]
  │
  └─ 4. Return [{codigo, descripcion, precio_actual, precio_nuevo}, ...]
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `services/articulos/redondeo.py` | Create | Pure rounding functions: `aplicar_redondeo()` and `calcular_precio_comercial()` |
| `services/articulos/articulos.py` | Modify | L290+: query rules once, replace L305 calculation with `calcular_precio_comercial()` call |
| `services/articulos/__init__.py` | Modify | Add exports: `aplicar_redondeo`, `calcular_precio_comercial` |

## Interfaces / Contracts

### `aplicar_redondeo(precio_base, multiplo=100, tipo='cercano', restar=0)`

- `precio_base`: `float` — calculated price before rounding
- `multiplo`: `int` — multiple to round to (0 or negative → passthrough)
- `tipo`: `str` — `'arriba'` | `'abajo'` | `'cercano'`
- `restar`: `int` — units to subtract after rounding (if result >= restar)
- Returns: `float` — rounded price

### `calcular_precio_comercial(precio_lista, porcentaje, reglas_db)`

- `precio_lista`: `float` — current list price
- `porcentaje`: `float` — percentage increase
- `reglas_db`: `list[dict]` — active rules with keys: `desde_precio`, `hasta_precio`, `multiplo`, `tipo_redondeo`, `restar_unidades`
- Returns: `float` — new price (rounded or as-is)

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | `aplicar_redondeo()`: all 4 types (arriba, abajo, cercano, con restar), edge cases (multiplo=0, precioExactoMultiplo) | Pure function tests, no mocks needed |
| Unit | `calcular_precio_comercial()`: rule found, no rule, multiple rules selecting correct one | Pure function with dict inputs |
| Integration | `obtenerArticulosMarcaRubro()` with active rules in DB | Mock `ReglaRedondeo.query`, verify `precio_nuevo` values |
| Integration | `obtenerArticulosMarcaRubro()` with no active rules | Verify backward-compatible passthrough |

## Migration / Rollout

No migration required. `ReglaRedondeo` model and table already exist. Feature is opt-in: if no rules are configured (`activo=True`), behavior is identical to current.

## Open Questions

None. All design decisions have clear rationale from proposal, spec, and codebase analysis.
