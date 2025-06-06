import logging
from flask import session, current_app
from datetime import datetime
from zeep import Client, Transport
from requests import Session
from services.wsaa import LoginTicket  # Asumiendo que tienes el código anterior en wsaa.py

from models.configs import PuntosVenta, Configuracion
from services.configs import discrimina_iva_afip
from utils.db import db

class AFIP:
    def __init__(self, cert_path, cert_password, punto_venta, service="wsfe", verbose=False):
        self.cert_path = cert_path
        self.cert_password = cert_password
        self.punto_venta = punto_venta
        self.service = service
        self.verbose = verbose
        #self.wsaa_url = "https://wsaa.afip.gov.ar/ws/services/LoginCms?WSDL" # Para producción
        self.wsaa_url = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?WSDL" # Para pruebas en ambiente de homologación
        self.wsfe_url = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"
        self.auth = None
    
    def save_auth_data(self):
        """Guarda los datos de autenticación en archivo"""
        print('Vamos a guardar los datos del TA')
        puntos_vta = PuntosVenta.query.get(self.punto_venta)
        if puntos_vta:
            try:
                puntos_vta.token = self.auth['Token'],
                puntos_vta.sign = self.auth['Sign'],
                puntos_vta.expiration = self.auth['ExpirationTime']
                db.session.commit()
                return {'success': True, 'error': None}    
            except Exception as e:  
                db.session.rollback()
                print(f"Error al guardar datos de autenticación: {str(e)}")
                return {'success': False, 'error': str(e)}    
        else:        
            return {'success': False, 'error': f'No existe el punto de venta {self.punto_venta} en la base de datos'}    
        
    def authenticate(self):
        #Si el token ya existe y no ha expirado, no es necesario volver a autenticar
        self.verbose = True
        puntoVta = PuntosVenta.query.get(self.punto_venta)
        if puntoVta:
            ahora = datetime.now()
            if puntoVta.expiration and puntoVta.expiration > ahora:
                self.auth = {
                    'Token': puntoVta.token,
                    'Sign': puntoVta.sign,
                    'ExpirationTime': puntoVta.expiration,
                    'Cuit': self._get_cuit_from_certificate()
                }
                if self.verbose:
                    print('------------------------------------------------')
                    print('Token ya existe y no ha expirado')
                    print('Auth:', self.auth)
                    print('------------------------------------------------')
            else:
                """Obtiene ticket de autenticación (TA)"""
                print('Servicio:', self.service)
                current_app.logger.debug(f"Servicio: {self.service}")
                login = LoginTicket(self._get_cuit_from_certificate(), verbose=self.verbose)
                current_app.logger.info(f"Obtener TA y respuesta")
                ta = login.obtener_login_ticket_response(
                    servicio=self.service,
                    url_wsaa=self.wsaa_url,
                    cert_path=self.cert_path,
                    password =self.cert_password
                )
                if self.verbose:
                    print('------------------------------------------------')
                    print('Login ticket obtenido')
                    print('TA:', ta)
                    print('------------------------------------------------')
                print('vamos a ver si el TA tiene error')    
                current_app.logger.info(f"vamos a ver si el TA tiene error")
                print('Error TA:', ta)
                current_app.logger.info(f"Error TA:: {ta}")
                if ta.get('error') == None:
                    print('sin error obteniendo TA')
                    try:
                        self.auth = {
                            'Token': ta.get('token'),
                            'Sign': ta.get('sign'),
                            'ExpirationTime': ta.get('expiration_time'),
                            'Cuit': self._get_cuit_from_certificate()
                        }
                    except Exception as e:
                        print(f"Error al obtener datos del CUIT: {str(e)}")
                        return {'success': False, 'error': f'Error obteniendo datos del CUIT:{e}'}
                    print('Auth:', self.auth)
                    self.save_auth_data()    
                    if self.verbose:
                        print('------------------------------------------------')
                        print('Datos autenticación')
                        print('Auth:', self.auth)
                        print('------------------------------------------------')
                    return self.auth
                else:
                    print('Error al obtener datos de autenticación')
                    print('Error:', ta.error)
                    current_app.logger.error('Error al obtener datos de autenticación')
                    current_app.logger.error(f'Error:', ta.error)
                    return {'success': False, 'error': f'Error obteniendo ta:{ta.error}'}
        else:
            print('No existe punto de venta con ese ID')    
            return {'success': False, 'error': 'No existe punto de venta con ese ID'}
        # Si no existe el punto de venta, se puede crear uno nuevo o manejar el error según sea necesario
    
    def _get_cuit_from_certificate(self):
        """Extrae el CUIT del certificado"""
        # Implementación para extraer CUIT del certificado
        # Esto depende de cómo esté estructurado tu certificado
        # Lo voy a extraer desde la configuración de la aplicación
        config = Configuracion.query.get(session['id_empresa'])
        return config.documento
        
    
    def get_last_invoice(self, pto_vta, cbte_tipo):
        # Conexión a WSFE
        print('last_invoice')
        print(self.auth)
        if not self.auth:
            self.authenticate()
        session = Session()
        transport = Transport(session=session)
        client = Client(self.wsfe_url, transport=transport)
        auth = {
            'Token': self.auth['Token'],
            'Sign': self.auth['Sign'],
            'Cuit': self.auth['Cuit']
        }
        response = client.service.FECompUltimoAutorizado(Auth=auth, PtoVta=pto_vta, CbteTipo=cbte_tipo)
        return response
    
    def create_invoice(self, invoice_data, tipo_comprobante):
        """Crea una factura electrónica"""
        if not self.auth:
            self.authenticate()
            
        # Conexión a WSFE
        session = Session()
        transport = Transport(session=session)
        client = Client(self.wsfe_url, transport=transport)
        
        # Datos básicos de la factura
        auth = {
            'Token': self.auth['Token'],
            'Sign': self.auth['Sign'],
            'Cuit': self.auth['Cuit']
        }
        if self.verbose:
            print('------------------------------------------------')
            print('auth ya solicitando:', auth)
            print('------------------------------------------------')
        
        # Construir solicitud de factura
        if not discrimina_iva_afip(tipo_comprobante):
            request = {
                'FeCAEReq': {
                    'FeCabReq': {
                        'CantReg': 1,  # Cantidad de comprobantes
                        #'PtoVta': invoice_data['punto_venta'],
                        'PtoVta': self.punto_venta,
                        'CbteTipo': invoice_data['tipo_comprobante'],
                    },
                    'FeDetReq': {
                        'FECAEDetRequest': [{
                            'Concepto': invoice_data['concepto'],
                            'DocTipo': invoice_data['tipo_doc'],
                            'DocNro': invoice_data['nro_doc'],
                            'CbteDesde': invoice_data['nro_cbte'],
                            'CbteHasta': invoice_data['nro_cbte'],
                            'CbteFch': datetime.now().strftime("%Y%m%d"),
                            'ImpTotal': invoice_data['importe_total'],
                            'ImpTotConc': 0,  # Importe neto no gravado
                            'ImpNeto': invoice_data['importe_neto'],
                            'ImpOpEx': 0,  # Importe exento
                            'ImpIVA': invoice_data['importe_iva'],
                            'ImpTrib': 0,  # Importe de tributos
                            'MonId': 'PES',  # Moneda
                            'MonCotiz': 1
                        }]
                    }
                }
            }
        
        else:
            request = {
                'FeCAEReq': {
                    'FeCabReq': {
                        'CantReg': 1,  # Cantidad de comprobantes
                        #'PtoVta': invoice_data['punto_venta'],
                        'PtoVta': self.punto_venta,
                        'CbteTipo': invoice_data['tipo_comprobante'],
                    },
                    'FeDetReq': {
                        'FECAEDetRequest': [{
                            'Concepto': invoice_data['concepto'],
                            'DocTipo': invoice_data['tipo_doc'],
                            'DocNro': invoice_data['nro_doc'],
                            'CbteDesde': invoice_data['nro_cbte'],
                            'CbteHasta': invoice_data['nro_cbte'],
                            'CbteFch': datetime.now().strftime("%Y%m%d"),
                            'ImpTotal': invoice_data['importe_total'],
                            'ImpTotConc': 0,  # Importe neto no gravado
                            'ImpNeto': invoice_data['importe_neto'],
                            'ImpOpEx': 0,  # Importe exento
                            'ImpIVA': invoice_data['importe_iva'],
                            'ImpTrib': 0,  # Importe de tributos
                            'MonId': 'PES',  # Moneda
                            'MonCotiz': 1,   # Cotización de la moneda
                            'Iva': self._build_iva_array(invoice_data['alicuotas'])
                        }]
                    }
                }
            }
        
        # Llamar al webservice
        try:
            if self.verbose:
                print('------------------------------------------------')
                print('1.2- Llamando al WSFE')
                print('------------------------------------------------')
                print('1.2.1- Datos de autenticación:', auth)
                print('------------------------------------------------')
                print('1.2.2- Datos de la solicitud:', request)
                print('------------------------------------------------')
            response = client.service.FECAESolicitar(auth, request['FeCAEReq'])
            if self.verbose:
                print('------------------------------------------------')
                print('1.2.3- Respuesta del WSFE:', response)
                print('------------------------------------------------')
                
            return self._process_response(response)
        except Exception as e:
            print(f"Error al crear factura: {str(e)}")
            return {"success": False, "error": str(e)}
    
                 
    
    def _build_iva_array(self, alicuotas):
        """Construye array de IVA para la factura"""
        return [{
            'Id': item['id'],  # 5 para 21%, 4 para 10.5%, etc.
            'BaseImp': item['base_imp'],
            'Importe': item['importe']
        } for item in alicuotas]
    
    def _process_response(self, response):
        """Procesa la respuesta del WSFE"""
        
        result = response['FeDetResp']['FECAEDetResponse'][0]
        if self.verbose:
            print('------------------------------------------------')
            print('1.2.4- Procesando respuesta del WSFE')
            print('------------------------------------------------')
            print('1.2.4.1- Respuesta del WSFE:', response)
        try:    
            respuesta = {
                'cae': result['CAE'],
                'cae_fch_vto': result['CAEFchVto'],
                'nro_cbte': result['CbteDesde'],
                'resultado': result['Resultado'],
                'observaciones': [obs['Msg'] for obs in result['Observaciones']['Obs']]
            }
        except Exception as e:
            respuesta = {
                'error': str(e)
            }    
        return respuesta