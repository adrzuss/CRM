import { getPrinterService } from './invoice_printer.js';

class InvoiceHandler {
    constructor() {
        // Por defecto usamos la impresión del navegador
        this.printerService = getPrinterService('browser');
        
        // Para impresoras térmicas:
        // this.printerService = getPrinterService('thermal');
    }
    
    async printInvoice(facturaId) {
        try {
            // Obtener datos de la factura del servidor
            const response = await fetch(`${BASE_URL}/ventas/api/facturas/${facturaId}`);
            if (!response.ok) {
                throw new Error('Error al obtener la factura');
            }
            
            const data = await response.json();
            const { factura, items, empresa } = data;
            
            // Imprimir factura
            const result = await this.printerService.printInvoice(factura, items, empresa);
            
            if (result.success) {
                console.log(result.message);
                return result;
            } else {
                console.error(result.error);
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('Error al imprimir:', error);
            return { success: false, error: error.message };
        }
    }
    
    async configurePrinter() {
        // Para impresoras térmicas, necesitamos conectar primero
        if (this.printerService.constructor.name === 'ThermalPrinterService') {
            return await this.printerService.connect();
        }
        
        return { success: true, message: 'No se requiere configuración' };
    }
    
    async listPrinters() {
        return await this.printerService.listPrinters();
    }
    
    setPrinterType(type) {
        this.printerService = getPrinterService(type);
    }
}

// Exportamos la clase
export default InvoiceHandler;