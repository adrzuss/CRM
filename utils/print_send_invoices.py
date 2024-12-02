from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
import os

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from services.ventas import get_factura
from utils.config import Config
from models.configs import Configuracion
# Generación de factura

def generar_factura_pdf(id, footer_text=""):
    configuracion = Configuracion.query.get(1)
    logo_path=None
    factura, items, pagos = get_factura(id)
    archivo_pdf = Config.INVOICES_FOLDER + f"/factura-{id}.pdf"
    c = canvas.Canvas(archivo_pdf, pagesize=A4)
    width, height = A4

    # Encabezado
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, height - 2 * cm, "Factura")

    # Logo (si existe)
    logo_path = Config.LOGO_PATH
    if logo_path and os.path.exists(logo_path):
        c.drawImage(logo_path, width - 6 * cm, height - 4 * cm, width=4 * cm, preserveAspectRatio=True)

    # Información del cliente y fecha
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, height - 3 * cm, f"Fecha: {factura.fecha}")
    c.drawString(2 * cm, height - 3.6 * cm, f"Cliente: {factura.nombre}")
    c.drawString(2 * cm, height - 4.2 * cm, f"Dirección: {factura.direccion}")
    #c.drawString(2 * cm, height - 4.8 * cm, f"Factura No: {factura.numero}")

    # Tabla de items
    table_data = [["Cantidad", "Descripción", "Precio Unitario", "Total"]]
    for item in items:
        table_data.append([
            item.cantidad,
            item.detalle,
            f"${item.precio_unitario:.2f}",
            f"${item.precio_total:.2f}"
        ])

    # Estilo de la tabla
    table = Table(table_data, colWidths=[3 * cm, 8 * cm, 3 * cm, 3 * cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Colocar la tabla en el PDF
    table.wrapOn(c, width, height)
    table.drawOn(c, 2 * cm, height - 10 * cm)

    # Total de la factura
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, 5 * cm, f"Total a Pagar: ${factura.total:.2f}")

    # Footer personalizado
    c.setFont("Helvetica", 9)
    c.drawString(2 * cm, 3 * cm, footer_text)

    # Guardar el PDF
    c.save()
    return archivo_pdf

# Envio de mail
def enviar_factura_por_email(destinatario, pdf_path, asunto="Factura Electrónica"):
    pdf_path = Config.INVOICES_FOLDER + f"/{pdf_path}"
    configuracion = Configuracion.query.first()
    remitente = configuracion.mail  # Cambia esto con tu correo
    password = configuracion.clave  # Cambia esto con la contraseña de tu correo
        
    # Configuración de la conexión
    #server = smtplib.SMTP("smtp.gmail.com", 587)
    #server.starttls()
    #server.login("tu_correo@gmail.com", "tu_contraseña_o_contraseña_de_aplicación")
    # Configura el mensaje
    mensaje = MIMEMultipart()
    mensaje["From"] = configuracion.nombre_propietario
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto

    # Agregar un cuerpo al mensaje
    cuerpo = MIMEText("Adjunto encontrará la factura en formato PDF.", "plain")
    mensaje.attach(cuerpo)

    # Adjuntar el PDF
    with open(pdf_path, "rb") as archivo_pdf:
        adjunto_pdf = MIMEApplication(archivo_pdf.read(), _subtype="pdf")
        adjunto_pdf.add_header("Content-Disposition", "attachment", filename="Factura.pdf")
        mensaje.attach(adjunto_pdf)

    # Conecta y envía el correo
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:  # Cambia el servidor SMTP
            servidor.starttls()
            servidor.login(remitente, password)
            servidor.send_message(mensaje)
            print("Correo enviado con éxito.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")