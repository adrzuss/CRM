# Proposal: Modal de confirmación de salida reutilizable

## Intent

Actualmente 10 archivos JS usan `window.onbeforeunload` para preguntar si el usuario quiere salir de una página con datos sin guardar. El mensaje por defecto del navegador es feo, no es personalizable, y en navegadores modernos ya ni se muestra. Queremos reemplazarlo por una modal de confirmación con SweetAlert2 que sea reutilizable.

## Scope

### In Scope
- Crear función `confirmarSalida()` en `static/js/swal-helpers.js` (ya existe el archivo)
- Reemplazar `window.onbeforeunload` en los 10 archivos JS por la nueva función
- La función debe: mostrar modal al intentar salir / cerrar pestaña, detectar si hay cambios sin guardar

### Out of Scope
- Templates HTML (no se modifican)
- Lógica de detección de cambios sucios (cada formulario ya la tiene)

## Approach

1. En `swal-helpers.js`, crear función:

```js
let sinGuardar = false;

function marcarSinGuardar() {
    sinGuardar = true;
}

function confirmarSalida(e) {
    if (!sinGuardar) return;
    e.preventDefault();
    e.returnValue = '';  // necesario para mostrar el diálogo nativo
}
```

2. En cada JS que tenga `onbeforeunload`, reemplazar por `confirmarSalida` y en los cambios del formulario llamar `marcarSinGuardar()`

3. El `beforeunload` del navegador se muestra igual (no podemos evitarlo por seguridad), pero la experiencia es más limpia y centralizada.

## Success Criteria

- [ ] Los 10 archivos JS ya no tienen `window.onbeforeunload` directo
- [ ] Todos usan `confirmarSalida()` desde `swal-helpers.js`
- [ ] No hay regresiones en la funcionalidad existente
