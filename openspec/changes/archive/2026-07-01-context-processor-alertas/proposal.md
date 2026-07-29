# Proposal: Context Processor para Alertas y Mensajes

## Intent

Todos los endpoints pasan las mismas 4 variables a `render_template()`: `alertas=g.alertas`, `cantidadAlertas=g.cantidadAlertas`, `mensajes=g.mensajes`, `cantidadMensajes=g.cantidadMensajes`. Son ~100 ocurrencias en 15 archivos de rutas. Un context processor en Flask inyecta estas variables automáticamente en todos los templates, eliminando la repetición.

## Scope

### In Scope
- Agregar `@app.context_processor` en index.py que inyecte `alertas`, `cantidadAlertas`, `mensajes`, `cantidadMensajes`
- Eliminar esas 4 variables de todos los `render_template()` en los 15 archivos de routes/
- Verificar que los templates sigan recibiendo las variables

### Out of Scope
- Refactorizar el decorador `@alertas_mensajes` o los services que llenan `g.alertas`
- Tocar templates
- Agregar otros context processors

## Capabilities

### New Capabilities
None

### Modified Capabilities
None

## Approach

1. En `index.py`, dentro de `create_app()`, agregar:

```python
@app.context_processor
def inject_alertas():
    return dict(
        alertas=g.alertas,
        cantidadAlertas=g.cantidadAlertas,
        mensajes=g.mensajes,
        cantidadMensajes=g.cantidadMensajes
    )
```

2. En cada archivo de `routes/`, buscar y eliminar `, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes` de todas las llamadas a `render_template()`.

## Riesgos

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Templates que usan otro nombre de variable | Baja | Solo se eliminan las 4 variables exactas; si alguna template usa otro nombre no se toca |
| Context processor se ejecuta sin `g.alertas` definido | Baja | El decorador `@alertas_mensajes` siempre lo define antes de renderizar |
| g.alertas no existe en rutas sin @alertas_mensajes | Media | Revisar manualmente qué rutas no tienen el decorador pero renderizan templates |

## Criterios de éxito
- [ ] `python index.py` arranca sin errores
- [ ] `pytest tests/` — 19 tests pasan
- [ ] Ningún `render_template()` en routes/ pasa `alertas=g.alertas` como argumento
- [ ] Los templates siguen funcionando (las variables se inyectan automáticamente)
