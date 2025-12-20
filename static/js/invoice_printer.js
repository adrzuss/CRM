/**
 * Clase base para servicios de impresión
 */
class BasePrinterService {
    constructor() {
        this.printerName = null;
    }
    
    /**
     * Lista impresoras disponibles
     * @returns {Promise<Object>} Resultado de la operación
     */
    async listPrinters() {
        return { 
            success: false, 
            error: "Método no implementado en la clase base" 
        };
    }
    
    /**
     * Imprime una factura
     * @param {Object|Array} factura - Datos de la factura
     * @param {Array} items - Items de la factura
     * @param {Object} empresa - Datos de la empresa
     * @returns {Promise<Object>} Resultado de la operación
     */
    async printInvoice(factura, items, empresa) {
        return { 
            success: false, 
            error: "Método no implementado en la clase base" 
        };
    }
    
    /**
     * Formatea el contenido de la factura para impresión
     * Adaptado para mantener el mismo formato que la versión Python
     */
    _formatInvoice(factura, items, empresa) {
        // Determinar si factura es un array o un objeto
        const esArray = Array.isArray(factura);
        const numero = esArray ? factura[7] : factura.nro_comprobante;
        const fecha = esArray ? factura[1] : factura.fecha;
        const cliente = esArray ? factura[13] : factura.cliente;
        const total = esArray ? factura[2] : factura.total;
        
        const empresaNombre = typeof empresa === 'object' ? 
            empresa.nombre || empresa['nombre'] : empresa;
        
        let content = `
            <div class="header">
                <h3>${empresaNombre}</h3>
            </div>
            <div class="divider"></div>
            <p>Factura: ${numero}</p>
            <p>Fecha: ${fecha}</p>
            <p>Cliente: ${cliente}</p>
            <div class="divider"></div>
        `;
        
        items.forEach(item => {
            // Determinar si el item es un array o un objeto
            const esItemArray = Array.isArray(item);
            const cantidad = esItemArray ? item[1] : item.cantidad;
            const descripcion = esItemArray ? item[6] : item.descripcion;
            const precio = esItemArray ? item[3] : item.precio_total;
            
            content += `
                <div class="item-row">
                    <div class="item-desc">${cantidad} x ${descripcion}</div>
                    <div class="item-price">$ ${parseFloat(precio).toFixed(2)}</div>
                </div>
            `;
        });
        
        content += `
            <div class="divider"></div>
            <div class="total">TOTAL: $ ${parseFloat(total).toFixed(2)}</div>
        `;
        
        return content;
    }
}

/**
 * Servicio de impresión para navegadores web estándar
 */
class BrowserPrinterService extends BasePrinterService {
    constructor() {
        super();
    }
    
    async listPrinters() {
        // Los navegadores no pueden listar impresoras directamente por seguridad
        return { 
            success: false, 
            error: "Los navegadores no pueden listar impresoras por restricciones de seguridad",
            system: "browser" 
        };
    }
    
    async printInvoice(factura, items, empresa) {
        try {
            const content = this._formatInvoice(factura, items, empresa);
            
            // Crear ventana de impresión
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <html>
                    <head>
                        <title>Factura</title>
                        <style>
                            body { font-family: monospace; max-width: 300px; margin: 0 auto; }
                            .header { text-align: center; margin-bottom: 10px; }
                            .divider { border-top: 1px dashed #000; margin: 10px 0; }
                            .item-row { display: flex; justify-content: space-between; margin: 5px 0; }
                            .item-desc { flex: 2; }
                            .item-price { flex: 1; text-align: right; }
                            .total { font-weight: bold; text-align: right; margin-top: 5px; }
                            @media print {
                                body { width: 80mm; margin: 0; }
                                @page { margin: 10px; }
                            }
                        </style>
                    </head>
                    <body>
                        ${content}
                    </body>
                </html>
            `);
            
            // Ejecutar impresión
            printWindow.document.close();
            printWindow.focus();
            printWindow.print();
            printWindow.close();
            
            return { success: true, message: 'Documento enviado a impresión' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
}

/**
 * Servicio de impresión para impresoras térmicas usando WebUSB
 */
class ThermalPrinterService extends BasePrinterService {
    constructor() {
        super();
        this.device = null;
        this.vendorId = null;
        this.productId = null;
    }
    
    async listPrinters() {
        try {
            if (!navigator.usb) {
                throw new Error("WebUSB no está soportado en este navegador");
            }
            
            const devices = await navigator.usb.getDevices();
            const printers = devices.map(device => ({
                vendor_id: '0x' + device.vendorId.toString(16),
                product_id: '0x' + device.productId.toString(16),
                manufacturer: device.manufacturerName || 'Desconocido',
                product: device.productName || 'Dispositivo USB'
            }));
            
            return { success: true, printers, system: 'usb' };
        } catch (error) {
            return { success: false, error: error.message, system: 'usb' };
        }
    }
    
    async connect() {
        try {
            if (!navigator.usb) {
                throw new Error("WebUSB no está soportado en este navegador");
            }
            
            // Si ya tenemos los IDs, intentamos conectar directamente
            if (this.vendorId && this.productId) {
                const devices = await navigator.usb.getDevices();
                this.device = devices.find(d => 
                    d.vendorId === this.vendorId && 
                    d.productId === this.productId);
            }
            
            // Si no encontramos el dispositivo, pedimos al usuario que seleccione uno
            if (!this.device) {
                this.device = await navigator.usb.requestDevice({
                    filters: [] // Sin filtros para mostrar todos los dispositivos
                });
                
                this.vendorId = this.device.vendorId;
                this.productId = this.device.productId;
            }
            
            if (this.device) {
                await this.device.open();
                if (this.device.configuration === null) {
                    await this.device.selectConfiguration(1);
                }
                await this.device.claimInterface(0);
                
                return { 
                    success: true, 
                    message: 'Impresora conectada', 
                    printer: {
                        vendor_id: '0x' + this.device.vendorId.toString(16),
                        product_id: '0x' + this.device.productId.toString(16)
                    }
                };
            }
            
            throw new Error("No se pudo encontrar una impresora");
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    async printInvoice(factura, items, empresa) {
        try {
            if (!this.device) {
                const result = await this.connect();
                if (!result.success) {
                    throw new Error(result.error);
                }
            }
            
            // Aquí implementaríamos la comunicación directa con la impresora térmica
            // usando comandos ESC/POS. Esta es una versión simplificada.
            
            // Ejemplo de comandos ESC/POS en forma de ArrayBuffer
            const encoder = new TextEncoder();
            
            // Formato para impresora térmica
            const esArray = Array.isArray(factura);
            const numero = esArray ? factura[7] : factura.numero;
            const fecha = esArray ? factura[1] : factura.fecha;
            const cliente = esArray ? factura[13] : factura.cliente;
            const total = esArray ? factura[2] : factura.total;
            
            const empresaNombre = typeof empresa === 'object' ? 
                empresa.nombre || empresa['nombre'] : empresa;
            
            // Crear buffer de comandos
            let commands = [];
            
            // Inicializar
            commands.push(new Uint8Array([0x1B, 0x40])); // ESC @
            
            // Centrado
            commands.push(new Uint8Array([0x1B, 0x61, 0x01])); // ESC a 1
            
            // Nombre empresa
            commands.push(encoder.encode(empresaNombre + "\n"));
            commands.push(encoder.encode("--------------------------------\n"));
            
            // Alineación izquierda
            commands.push(new Uint8Array([0x1B, 0x61, 0x00])); // ESC a 0
            
            // Datos factura
            commands.push(encoder.encode(`Factura: ${numero}\n`));
            commands.push(encoder.encode(`Fecha: ${fecha}\n`));
            commands.push(encoder.encode(`Cliente: ${cliente}\n`));
            commands.push(encoder.encode("--------------------------------\n"));
            
            // Items
            for (const item of items) {
                const esItemArray = Array.isArray(item);
                const cantidad = esItemArray ? item[1] : item.cantidad;
                const descripcion = esItemArray ? item[6] : item.descripcion;
                const precio = esItemArray ? item[3] : item.precio_total;
                
                commands.push(encoder.encode(`${cantidad} x ${descripcion}\n`));
                
                // Alineación derecha
                commands.push(new Uint8Array([0x1B, 0x61, 0x02])); // ESC a 2
                commands.push(encoder.encode(`$ ${parseFloat(precio).toFixed(2)}\n`));
                
                // Volver a izquierda
                commands.push(new Uint8Array([0x1B, 0x61, 0x00])); // ESC a 0
            }
            
            commands.push(encoder.encode("--------------------------------\n"));
            
            // Total (negrita y alineado derecha)
            commands.push(new Uint8Array([0x1B, 0x61, 0x02])); // ESC a 2
            commands.push(new Uint8Array([0x1B, 0x45, 0x01])); // ESC E 1
            commands.push(encoder.encode(`TOTAL: $ ${parseFloat(total).toFixed(2)}\n`));
            commands.push(new Uint8Array([0x1B, 0x45, 0x00])); // ESC E 0
            
            // Cortar papel
            commands.push(encoder.encode("\n\n\n\n"));
            commands.push(new Uint8Array([0x1D, 0x56, 0x00])); // GS V 0
            
            // Enviamos datos a la impresora
            for (const cmd of commands) {
                const endpointOut = this.device.configuration.interfaces[0].alternate.endpoints.find(e => e.direction === 'out');
                await this.device.transferOut(endpointOut.endpointNumber, cmd);
            }
            
            return { success: true, message: 'Impresión enviada con éxito' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
}

/**
 * Factory para obtener el servicio de impresión adecuado
 */
function getPrinterService(type = 'browser') {
    switch (type) {
        case 'thermal':
            return new ThermalPrinterService();
        case 'browser':
        default:
            return new BrowserPrinterService();
    }
}

// Exportamos las clases y la función factory
export {
    BasePrinterService,
    BrowserPrinterService,
    ThermalPrinterService,
    getPrinterService
};