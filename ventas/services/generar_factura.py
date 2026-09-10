from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

def cortar(texto, max_chars):
    return texto if len(texto) <= max_chars else texto[:max_chars - 3]

def generar_factura_pdf(pdf_path, datos_factura, items):
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    bold = ParagraphStyle('Bold', parent=normal, fontName='Helvetica-Bold')

    elements = []

    # Generar las 3 copias
    copias = ['ORIGINAL', 'DUPLICADO', 'TRIPLICADO']
    for i, copia in enumerate(copias):
        elements.extend(generar_cuerpo_factura(copia, datos_factura, items, normal, bold))
        if i < 2:
            elements.append(PageBreak())

    # Usamos una función interna para capturar datos dinámicos
    def encabezado_con_datos(copia):
        def draw(canvas, doc):
            draw_background(canvas, doc, datos_factura, copia)
        return draw

    # Crear documento con encabezado dinámico
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    doc.build(elements, onFirstPage=encabezado_con_datos(copias[0]), onLaterPages=encabezado_con_datos(copias[1]))
    print(f"PDF generado en {pdf_path}")

def generar_cuerpo_factura(copia, datos, items, normal, bold):
    elements = []

    elements.append(Spacer(1, 140))  # espacio para dejar lugar al encabezado

    # Tabla de ítems
    table_data = [['Código', 'Descripción', 'Cantidad', 'U. Medida', 'Precio Unit.', 'Subtotal']]
    for item in items:
        item['descripcion'] = cortar(item['descripcion'], 35)  # Cortar descripción si es necesario
        row = [item['codigo'], item['descripcion'], item['cantidad'], item['unidad_medida'],
               f"${item['precio_unitario']:.2f}", f"${item['subtotal']:.2f}"]
        table_data.append(row)

    table = Table(table_data, colWidths=[60, 200, 60, 60, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"<b>Subtotal:</b> ${datos['subtotal']:.2f}", normal))
    elements.append(Paragraph(f"<b>Total:</b> ${datos['total']:.2f}", bold))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"<b>CAE N°:</b> {datos['cae']}", normal))
    elements.append(Paragraph(f"<b>Fecha Vto. de CAE:</b> {datos['vencimiento_cae']}", normal))
    elements.append(Paragraph("<b>Comprobante Autorizado</b>", bold))
    return elements


def draw_background(canvas, doc, datos, copia):
    canvas.saveState()
    
    width, height = A4
    margin = 20
    canvas.setLineWidth(1)

    # RECTÁNGULO GENERAL
    canvas.rect(margin, margin, width - 2 * margin, height - 2 * margin)

    # COORDENADAS BASE
    left_x = margin
    right_x = width - margin
    top_y = height - margin
    encabezado_altura = 100

    # RECUADRO ENCABEZADO
    canvas.rect(left_x, top_y - encabezado_altura, right_x - left_x, encabezado_altura)

    # DIVISIÓN HORIZONTAL bajo el título
    canvas.line(left_x, top_y - 30, right_x, top_y - 30)

    # COPIA (ORIGINAL / DUPLICADO / TRIPLICADO)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawCentredString((left_x + right_x)/2, top_y - 18, copia)

    # BLOQUE IZQUIERDO – Emisor
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(left_x + 5, top_y - 42, datos['emisor_nombre'])
    canvas.setFont("Helvetica", 9)
    canvas.drawString(left_x + 5, top_y - 55, "Razón Social:")
    canvas.drawString(left_x + 90, top_y - 55, datos['emisor_nombre'])

    canvas.drawString(left_x + 5, top_y - 68, "Domicilio Comercial:")
    canvas.drawString(left_x + 90, top_y - 68, datos['emisor_domicilio'])

    canvas.drawString(left_x + 5, top_y - 81, "Condición frente al IVA:")
    canvas.drawString(left_x + 105, top_y - 81, datos['emisor_condicion_iva'])

    # BLOQUE CENTRAL – C y COD. 011 en recuadro
    box_width = 40
    box_height = 45
    center_x = (left_x + right_x) / 2
    box_left = center_x - box_width / 2
    box_bottom = top_y - 30 - box_height

    canvas.rect(box_left, box_bottom, box_width, box_height)

    canvas.setFont("Helvetica-Bold", 24)
    canvas.drawCentredString(center_x, box_bottom + box_height - 20, datos['letra_comprobante'])

    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(center_x, box_bottom + 5, "COD. " + str(datos['tipo_comprobante']).zfill(3))

    # BLOQUE DERECHO – Datos de la factura
    right_block_x = right_x - 160
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(right_block_x + 10, top_y - 42, "FACTURA")

    canvas.setFont("Helvetica", 9)
    canvas.drawString(right_block_x + 10, top_y - 55, f"Punto de Venta:     {datos['punto_venta']}")
    canvas.drawString(right_block_x + 10, top_y - 68, f"Comp. Nro:     {datos['nro_comprobante']}")
    canvas.drawString(right_block_x + 10, top_y - 81, f"Fecha de Emisión: {datos['fecha_emision']}")

    # PERÍODO FACTURADO
    py = top_y - encabezado_altura - 20
    canvas.setFont("Helvetica", 9)
    canvas.line(left_x, py, right_x, py)
    canvas.drawString(left_x + 5, py + 5, "Período Facturado Desde:")
    canvas.drawString(left_x + 145, py + 5, datos['periodo_desde'])
    canvas.drawString(left_x + 220, py + 5, "Hasta:")
    canvas.drawString(left_x + 260, py + 5, datos['periodo_hasta'])
    canvas.drawString(right_x - 180, py + 5, f"Fecha de Vto. para el pago: {datos['vto_pago']}")

    canvas.restoreState()
