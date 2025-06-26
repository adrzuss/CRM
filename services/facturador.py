from services.afip import AFIP
from services.configs import discrimina_iva_afip

class Facturador:
    def __init__(self, config):
        self.afip = AFIP(
            cert_path=config['cert_path'],
            cert_password=config['cert_password'],
            punto_venta=config['punto_venta'],
            service="wsfe",
            verbose=config.get('verbose', False)
        )
    
    def emitir_factura(self, cliente, items, tipo_comprobante=1, punto_venta=1):
        """Emitir una factura electrónica"""
        # Calcular totales
        
        importe_neto = sum(item['precio'] * item['cantidad'] for item in items)
        iva = sum(item['importe_iva'] * item['cantidad'] for item in items)
        importe_total = importe_neto + iva
        
        # Construir datos para AFIP
        if  not discrimina_iva_afip(tipo_comprobante):
            if self.afip.verbose:
                print('--------------------------------------------------------')   
                print('No discrimina IVA, se envía importe total sin IVA')
                print('--------------------------------------------------------')
            
            invoice_data = {
                'punto_venta': punto_venta,  # Número de punto de venta
                'tipo_comprobante': tipo_comprobante,  # 1=Factura A, 6=Factura B
                'concepto': 1,  # 1=Productos, 2=Servicios, etc.
                'tipo_doc': cliente['tipo_doc'],  # 80=CUIT, 96=DNI
                'nro_doc': cliente['nro_doc'],
                'condicion_iva_receptor': cliente['tipo_iva'],
                'nro_cbte': self._get_proximo_numero(punto_venta, tipo_comprobante),  # Obtener último número +1
                'importe_total': round(importe_total, 2),
                'importe_neto': round(importe_neto, 2),
                'importe_iva': round(0, 2)
            }
             
        else:    
            if self.afip.verbose:
                print('--------------------------------------------------------')
                print('Discrimina IVA, se envía importe total con IVA')
                print('--------------------------------------------------------')
            invoice_data = {
                'punto_venta': punto_venta,  # Número de punto de venta
                'tipo_comprobante': tipo_comprobante,  # 1=Factura A, 6=Factura B
                'concepto': 1,  # 1=Productos, 2=Servicios, etc.
                'tipo_doc': cliente['tipo_doc'],  # 80=CUIT, 96=DNI
                'nro_doc': cliente['nro_doc'],
                'condicion_iva_receptor': cliente['tipo_iva'],
                'nro_cbte': self._get_proximo_numero(punto_venta, tipo_comprobante),  # Obtener último número +1
                'importe_total': round(importe_total, 2),
                'importe_neto': round(importe_neto, 2),
                'importe_iva': round(iva, 2),
                'alicuotas': self._build_alicuotas(items)
            }
        # Enviar a AFIP
        invoice = self.afip.create_invoice(invoice_data, tipo_comprobante)
        return invoice
    
    def _get_proximo_numero(self, pto_vta, cbte_tipo):
        """Obtiene el próximo número de comprobante"""
        try:
            response = self.afip.get_last_invoice(pto_vta, cbte_tipo)
            ultimo = response['CbteNro']
            return ultimo + 1
        except Exception as e:
            print("Error al consultar último comprobante autorizado:", e)
            return None
        
    def _get_condicion_IVAReceptor(self, nro_doc, cbte_tipo):
        try:
            print(f'Obteniendo condición IVA del receptor: {nro_doc} para tipo de comprobante: {cbte_tipo}')
            response = self.afip.get_condicion_IVAReceptor(nro_doc, cbte_tipo)
            print(response['Desc'])
            print(response['Cmp_Clase'])
            return response['id']
        except Exception as e:
            print("Error al obtener condición IVA receptor:", e)
            return None
    
    def _build_alicuotas(self, items):
        """Agrupa items por alícuota de IVA"""
        alicuotas = {}
        for item in items:
            key = item['iva']
            if key not in alicuotas:
                alicuotas[key] = {
                    'id': self._get_afip_iva_code(item['iva']),
                    'base_imp': 0,
                    'importe': 0
                }
            alicuotas[key]['base_imp'] += round(item['precio'] * item['cantidad'], 2)
            alicuotas[key]['importe'] += round(item['precio'] * item['cantidad'] * item['iva'] / 100, 2)
        
        return list(alicuotas.values())
    
    def _get_afip_iva_code(self, iva_percentage):
        """Mapea porcentaje de IVA a código AFIP"""
        iva_map = {
            21.0: 5,   # 21%
            10.5: 4,   # 10.5%
            5.0: 8,    # 5%
            2.5: 9,    # 2.5%
            0.0: 3     # 0%
        }
        return iva_map.get(iva_percentage, 3)