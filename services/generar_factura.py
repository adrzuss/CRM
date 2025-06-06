from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

def generar_factura_pdf(pdf_path, datos_factura, items):
    # Configuración del documento
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']

    # Títulos
    # for copia in ['ORIGINAL', 'DUPLICADO', 'TRIPLICADO']:
    
    copia = 'ORIGINAL' 
    elements.append(Paragraph(f'<b>Factura { datos_factura["tipo_comprobante"] } - {copia}</b>', styleH))
    elements.append(Spacer(1, 12))

    # Datos del Emisor y Receptor
    emisor_data = f"""
    <b>Emisor:</b> {datos_factura['emisor_nombre']}<br/>
    <b>CUIT:</b> {datos_factura['emisor_cuit']}<br/>
    <b>Condición IVA:</b> {datos_factura['emisor_condicion_iva']}<br/>
    <b>Domicilio:</b> {datos_factura['emisor_domicilio']}<br/><br/>
    """
    receptor_data = f"""
    <b>Receptor:</b> {datos_factura['receptor_nombre']}<br/>
    <b>CUIT:</b> {datos_factura['receptor_cuit']}<br/>
    <b>Condición IVA:</b> {datos_factura['receptor_condicion_iva']}<br/>
    <b>Domicilio:</b> {datos_factura['receptor_domicilio']}<br/>
    """
    elements.append(Paragraph(emisor_data, styleN))
    elements.append(Paragraph(receptor_data, styleN))
    elements.append(Spacer(1, 12))

    # Tabla de artículos
    table_data = [['Código', 'Descripción', 'Cantidad', 'U. Medida', 'Precio Unit.', 'Subtotal']]
    for item in items:
        row = [item['codigo'], item['descripcion'], item['cantidad'], item['unidad_medida'], f'${item["precio_unitario"]}', f'${item["subtotal"]}']
        table_data.append(row)

    table = Table(table_data, colWidths=[60, 200, 60, 60, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Totales y CAE
    elements.append(Paragraph(f'<b>Subtotal:</b> ${datos_factura["subtotal"]}', styleN))
    elements.append(Paragraph(f'<b>Total:</b> ${datos_factura["total"]}', styleN))
    elements.append(Paragraph(f'<b>CAE:</b> {datos_factura["cae"]}', styleN))
    elements.append(Paragraph(f'<b>Fecha Vto. CAE:</b> {datos_factura["vencimiento_cae"]}', styleN))
    elements.append(Spacer(1, 24))

    # Construcción del PDF
    doc.build(elements)
    print(f'PDF generado en: {pdf_path}')
