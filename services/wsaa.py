"""
    <source>cn=wsaa,ou={cuit},o=AFIP,c=ar,serialNumber=CUIT {cuit}</source>
    <destination>cn=wsaa,o=AFIP,c=ar,serialNumber=CUIT 33693450239</destination>
    
"""
import logging
from flask import current_app
import base64
import subprocess
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
from requests import Session
from zeep import Client, Transport
import tempfile
import os

class LoginTicket:
    def __init__(self, cuit_emisor, verbose=False):
        self.cuit_emisor = cuit_emisor
        self.verbose = verbose
        self.global_unique_id = 0
        self.xml_template = """<loginTicketRequest version="1.0">
                                    <header>
                                        <uniqueId>{uniqueId}</uniqueId>
                                        <generationTime>{generationTime}</generationTime>
                                        <expirationTime>{expirationTime}</expirationTime>
                                    </header>
                                    <service>{service}</service>
                                </loginTicketRequest>"""

    def obtener_login_ticket_response(self, servicio, url_wsaa, cert_path, password):
        try:
            now = datetime.now()
            unique_id = int(now.timestamp())
            gen_time = (now - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S-03:00")
            exp_time = (now + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S-03:00")
            current_app.logger.info(f"Generación del XML")
            current_app.logger.info(f"desde: {gen_time}, hasta: {exp_time}")
            xml = self.xml_template.format(
                uniqueId=unique_id,
                generationTime=gen_time,
                expirationTime=exp_time,
                service=servicio
            )
            current_app.logger.info(f"XML generado: {xml}")
            # Crear archivos temporales
            with tempfile.TemporaryDirectory() as tmpdir:
                xml_path = os.path.join(tmpdir, "request.xml")
                pem_path = os.path.join(tmpdir, "cert.pem")
                cms_path = os.path.join(tmpdir, "signed.cms")

                # Guardar XML a firmar
                with open(xml_path, "w", encoding="utf-8") as f:
                    f.write(xml)

                # Extraer .pem desde el .pfx/.p12
                
                subprocess.run([
                    "openssl", "pkcs12",
                    "-in", cert_path,
                    "-out", pem_path,
                    "-nodes",
                    "-passin", f"pass:{password}"
                ], check=True)

                # Firmar con OpenSSL CMS DER + SHA1
                
                subprocess.run([
                    "openssl", "cms",
                    "-sign",
                    "-in", xml_path,
                    "-signer", pem_path,
                    "-inkey", pem_path,
                    "-outform", "DER",
                    "-out", cms_path,
                    "-nodetach",
                    "-nosmimecap",
                    "-binary"
                ], check=True)

                # Leer y codificar en base64
                with open(cms_path, "rb") as f:
                    cms_b64 = base64.b64encode(f.read()).decode("utf-8")

            # Enviar al WSAA
            session = Session()
            session.verify = False  # En producción deberías activarlo
            client = Client(url_wsaa, transport=Transport(session=session))
            response = client.service.loginCms(cms_b64)

            # Parsear XML de respuesta
            xml_resp = ET.fromstring(response)
            current_app.logger.info(f"La respuestas del loginCms es: {xml_resp}")
            return {
                'token': xml_resp.find(".//token").text,
                'sign': xml_resp.find(".//sign").text,
                'expiration_time': xml_resp.find(".//expirationTime").text,
                'error': None
            }

        except subprocess.CalledProcessError as e:
            current_app.logger.error(f"Error al ejecutar OpenSSL(1): {e}")
            return {'success': False,'error': f"OpenSSL error: {e}"}
        except Exception as e:
            current_app.logger.error(f"Error al ejecutar OpenSSL(2): {e}")
            return {'success': False,'error': str(e)}
    

# Configuración Flask
"""
@app.route('/wsaa/login', methods=['POST'])
def wsaa_login():
    try:
        data = request.json
        required_fields = ['servicio', 'cert_path', 'password']
        
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': f"Faltan campos requeridos: {required_fields}"
            }), 400

        ticket = LoginTicket(
            cuit_emisor=data.get('cuit', "20218767401"),  # Default para homologación
            verbose=data.get('verbose', False)
        )

        resultado = ticket.obtener_login_ticket_response(
            servicio=data['servicio'],
            url_wsaa=data.get('url_wsaa', "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?WSDL"),
            cert_path=data['cert_path'],
            password=data['password'],
            proxy=data.get('proxy'),
            proxy_user=data.get('proxy_user'),
            proxy_password=data.get('proxy_password')
        )

        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Error en el endpoint: {str(e)}"
        }), 500


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5000, debug=True)
"""    