from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime

def generar_pdf(datos_factura, articulos):
    # Crear el PDF
    archivo = f"factura_{datos_factura['tipo']}_{datos_factura['punto_venta']}_{datos_factura['nro_comprobante']}.pdf"
    c = canvas.Canvas(archivo, pagesize=A4)

    # Título del Comprobante (ORIGINAL, DUPLICADO, TRIPLICADO)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, 28 * cm, f"{datos_factura['tipo']}")

    # Datos del Emisor
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, 26 * cm, f"Razón Social: {datos_factura['razon_social']}")
    c.drawString(2 * cm, 25.5 * cm, f"CUIT: {datos_factura['cuit']}")
    c.drawString(2 * cm, 25 * cm, f"Domicilio: {datos_factura['domicilio']}")
    c.drawString(2 * cm, 24.5 * cm, f"IVA: {datos_factura['iva']}")

    # Datos del Comprobante
    c.drawString(12 * cm, 28 * cm, f"Cód. {datos_factura['codigo']}")
    c.drawString(12 * cm, 27.5 * cm, f"Punto de Venta: {datos_factura['punto_venta']}")
    c.drawString(12 * cm, 27 * cm, f"Comp. Nro: {datos_factura['nro_comprobante']}")
    c.drawString(12 * cm, 26.5 * cm, f"Fecha: {datos_factura['fecha_emision'].strftime('%d/%m/%Y')}")

    # Detalle de los Artículos
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, 23 * cm, "Código")
    c.drawString(6 * cm, 23 * cm, "Descripción")
    c.drawString(12 * cm, 23 * cm, "Cantidad")
    c.drawString(15 * cm, 23 * cm, "Precio Unit.")
    c.drawString(18 * cm, 23 * cm, "Subtotal")

    y = 22
    for articulo in articulos:
        c.setFont("Helvetica", 10)
        c.drawString(2 * cm, y * cm, str(articulo['codigo']))
        c.drawString(6 * cm, y * cm, articulo['descripcion'])
        c.drawString(12 * cm, y * cm, str(articulo['cantidad']))
        c.drawString(15 * cm, y * cm, f"${articulo['precio_unitario']:.2f}")
        c.drawString(18 * cm, y * cm, f"${articulo['subtotal']:.2f}")
        y -= 0.7

    # Totales
    c.setFont("Helvetica-Bold", 12)
    c.drawString(15 * cm, (y - 1) * cm, f"Total: ${datos_factura['total']:.2f}")

    # Guardar PDF
    c.showPage()
    c.save()

    return archivo
