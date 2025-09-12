from abc import ABC, abstractmethod
import platform


class BasePrinterService(ABC):
    """Clase base abstracta para servicios de impresión"""
    
    @abstractmethod
    def list_printers(self):
        """Listar impresoras disponibles"""
        pass

    @abstractmethod
    def print_invoice(self, factura, items, empresa):
        """Imprimir factura"""
        pass
    
    def _format_invoice(self, factura, items, empresa):
        """Método común para formatear la factura"""
        
        content = []
        content.append(f"{empresa['nombre']}\n")
        content.append("--------------------------------\n")
        content.append(f"Factura: {factura[7]}\n")
        content.append(f"Fecha: {factura[1]}\n")
        content.append(f"Cliente: {factura[13]}\n")
        content.append("--------------------------------\n")
        
        for item in items:
            content.append(f"{item[1]} x {item[6]}\n")
            content.append(f"$ {item[3]:.2f}\n")
        
        content.append("--------------------------------\n")
        content.append('\x1B\x45\x01')  # Negrita ON
        content.append(f"TOTAL: $ {factura[2]:.2f}\n")
        content.append('\x1B\x45\x00')  # Negrita OFF
        
        return content


class WindowsPrinterService(BasePrinterService):
    """Implementación para Windows usando WMI"""
    
    def __init__(self):
        self.printer_name = None
        
    def list_printers(self):
        try:
            import wmi
            printers = []
            c = wmi.WMI()
            for printer in c.Win32_Printer():
                printers.append({
                    'name': printer.Name,
                    'port': printer.PortName,
                    'is_default': printer.Default,
                    'status': printer.Status
                })
                
            return {'success': True, 'printers': printers, 'system': 'windows'}
        except Exception as e:
            return {'success': False, 'error': str(e), 'system': 'windows'}
            

    def cut_paper(self, full=True):
        feed = b'\n\n\n\n\n'
        cmd = b'\x1D\x56\x00' if full else b'\x1D\x56\x01'
        return feed + cmd

    def print_invoice(self, factura, items, empresa):
        try:
            import win32print
            if not self.printer_name:
                raise Exception("No se ha configurado una impresora")

            content = self._format_invoice(factura, items, empresa)
            content_str = "".join(content)

            hprinter = win32print.OpenPrinter(self.printer_name)
            try:
                hJob = win32print.StartDocPrinter(hprinter, 1, ("Factura", None, "RAW"))
                try:
                    win32print.StartPagePrinter(hprinter)
                    win32print.WritePrinter(hprinter, content_str.encode('utf-8'))
                    win32print.WritePrinter(hprinter, self.cut_paper(full=True))  
                    win32print.EndPagePrinter(hprinter)
                finally:
                    win32print.EndDocPrinter(hprinter)
            finally:
                win32print.ClosePrinter(hprinter)

            return {'success': True, 'message': 'Impresión exitosa'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class LinuxPrinterService(BasePrinterService):
    """Implementación para Linux usando CUPS"""
    
    def __init__(self):
        self.printer_name = None
        
    def list_printers(self):
        pass
        """
        try:
            import cups
            conn = cups.Connection()
            printers = []
            for name, printer in conn.getPrinters().items():
                printers.append({
                    'name': name,
                    'status': printer['printer-state'],
                    'is_default': printer.get('printer-is-default', False)
                })
            return {'success': True, 'printers': printers, 'system': 'linux'}
        except Exception as e:
            return {'success': False, 'error': str(e), 'system': 'linux'}
        """    

    def print_invoice(self, factura, items, empresa):
        pass
        """
        try:
            import cups, tempfile
            if not self.printer_name:
                raise Exception("No se ha configurado una impresora")

            conn = cups.Connection()
            content = self._format_invoice(factura, items, empresa)

            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write("".join(content))
                temp_path = f.name
            
            conn.printFile(self.printer_name, temp_path, "Factura", {})
            return {'success': True, 'message': 'Impresión exitosa'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        """

class USBPrinterService(BasePrinterService):
    """Implementación para impresoras USB directas"""
    
    def __init__(self):
        self.vendor_id = None
        self.product_id = None
        
    def list_printers(self):
        try:
            import usb.core, usb.util
            devices = usb.core.find(find_all=True)
            printers = []
            for device in devices:
                try:
                    printers.append({
                        'vendor_id': hex(device.idVendor),
                        'product_id': hex(device.idProduct),
                        'manufacturer': usb.util.get_string(device, device.iManufacturer),
                        'product': usb.util.get_string(device, device.iProduct)
                    })
                except:
                    continue
            return {'success': True, 'printers': printers, 'system': 'usb'}
        except Exception as e:
            return {'success': False, 'error': str(e), 'system': 'usb'}

    def print_invoice(self, factura, items, empresa):
        try:
            from escpos.printer import Usb
            if not all([self.vendor_id, self.product_id]):
                raise Exception("No se han configurado los IDs de la impresora")
                
            printer = Usb(self.vendor_id, self.product_id)
            printer.set(align='center')
            printer.text(f"{empresa['nombre']}\n")
            printer.text("--------------------------------\n")
            printer.set(align='left')
            printer.text(f"Factura: {factura['numero']}\n")
            printer.text(f"Fecha: {factura['fecha']}\n")
            printer.text(f"Cliente: {factura['cliente']}\n")
            printer.text("--------------------------------\n")
            for item in items:
                printer.text(f"{item['cantidad']} x {item['descripcion']}\n")
                printer.set(align='right')
                printer.text(f"$ {item['precio_total']:.2f}\n")
                printer.set(align='left')
            printer.text("--------------------------------\n")
            printer.set(align='right')
            printer.text(f"TOTAL: $ {factura['total']:.2f}\n")
            printer.cut()
            return {'success': True, 'message': 'Impresión exitosa'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            if 'printer' in locals():
                printer.close()


def get_printer_service():
    """Factory para crear el servicio de impresión apropiado"""
    system = platform.system().lower()
    if system == 'windows':
        return WindowsPrinterService()
    elif system == 'linux':
        return LinuxPrinterService()
    else:
        return USBPrinterService()
