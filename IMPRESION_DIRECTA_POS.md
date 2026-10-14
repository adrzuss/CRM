# Impresión directa de tickets POS (modo "Envío directo")

## Qué es

El CRM permite imprimir los comprobantes de venta en dos modos, configurados por punto de venta:

- **Previsualizar** (por defecto): se abre la ventana de impresión del navegador (diálogo de impresión). Es el comportamiento histórico.
- **Envío directo**: el ticket se envía en silencio a la **impresora por defecto del sistema** de la terminal, sin ventana ni diálogo. La ventana interna que arma el ticket se abre y se cierra sola en milisegundos.

## Requisito operativo por terminal (obligatorio para Envío directo)

La impresión silenciosa es una característica del navegador, no del CRM. Cada terminal POS debe lanzar Chrome/Edge con el parámetro `--kiosk-printing`:

1. Crear un acceso directo por terminal, por ejemplo:
   `"C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk-printing --app=http://<servidor>/ventas/nueva_venta`
2. Usar SIEMPRE ese acceso directo en la terminal. Si el usuario abre el navegador normal, la impresión directa no funciona (ver fallback más abajo).
3. No hace falta reiniciar nada en el CRM al cambiar el acceso directo.

## Impresora por defecto del sistema

El contrato es **una impresora por terminal**: el ticket sale por la impresora predeterminada del sistema operativo de esa terminal.

- Windows: Dispositivos e impresoras → clic derecho sobre la impresora del ticket → **Definir como predeterminada**.
- Verificar que la impresora predeterminada sea la térmica del POS, no una multifunción o una virtual (PDF).

## Configuración en el CRM

1. Ir a **Configuración > Puntos de venta** y editar el punto de venta.
2. Sección **"Configuración de impresión"**: activar **"Impresora POS"** (el modo no tiene efecto sin ella).
3. Elegir **"Modo de impresión"**: *Previsualizar* o *Envío directo*.
4. Guardar. El modo se aplica cuando el cajero (re)selecciona el punto de venta en la pantalla de nueva venta o recarga la página.

**Staleness definida**: si un administrador cambia el modo con un cajero en sesión, el cambio recién se refleja al reseleccionar el punto de vista o al recargar la venta. No es un bug.

## Comportamiento SIN `--kiosk-printing` (fallback)

Si el modo es *Envío directo* pero la terminal no lanzó el navegador con el parámetro, **se abre el diálogo de impresión normal** (equivalente a previsualizar). No es un error: la venta se completa igual y no hay pérdida de datos. El CRM no intenta detectar el parámetro (no es detectable desde JavaScript).

## Limitaciones explícitas

- No se puede detectar desde el código si el navegador tiene `--kiosk-printing`.
- Impresora única: siempre la predeterminada del sistema; no hay selección de impresora por punto de venta.
- La terminal necesita acceso a `cdn.jsdelivr.net` para generar el QR de AFIP del ticket (se carga bajo demanda en la página).
- El QR de AFIP se genera antes de imprimir; si el CDN no responde, no se imprime el ticket y el CRM abre el comprobante PDF como alternativa.

## Solución de problemas

| Síntoma | Causa probable | Acción |
|---|---|---|
| Sale por la impresora equivocada | Impresora predeterminada mal configurada en la terminal | Reconfigurar la predeterminada (sección anterior) |
| Aparece el diálogo de impresión en modo directo | La terminal no lanzó Chrome/Edge con `--kiosk-printing` | Corregir el acceso directo y usarlo |
| Se abre el PDF en lugar del ticket | Error de impresión o CDN del QR inaccesible | Revisar consola del navegador (F12) y conectividad |
| El ticket no tiene QR AFIP | `cdn.jsdelivr.net` inaccesible desde la terminal | Habilitar salida a ese dominio en la red |
| Queda una ventana abierta | Bloqueador de ventanas emergentes | Permitir ventanas emergentes para el sitio |

## Checklist de verificación manual

1. Terminal **con** `--kiosk-printing` + modo *Envío directo*: grabar venta y confirmar "Sí imprimir" → no aparece diálogo, el ticket sale por la impresora por defecto y no queda ventana abierta.
2. Terminal **sin** el parámetro + modo *Envío directo*: aparece el diálogo de impresión normal; la venta no se ve afectada.
3. Modo *Previsualizar*: aparece el diálogo; al cerrarlo la ventana se cierra sola (sin ventana colgada).
4. Remito (botón "No imprimir" o cierre del modal) en ambos modos.
5. Nota de crédito (factura y remito) en ambos modos.
6. Reimpresión desde la vista del comprobante (`/ver_factura_vta/<id>`) en ambos modos.
7. Consola del navegador sin errores CSP ("Refused to execute inline script").
8. El ticket de factura muestra el QR de AFIP.
