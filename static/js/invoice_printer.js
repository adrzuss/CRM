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

    async printDelivery(factura, items, empresa) {
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
            
            // Verificar si el navegador bloqueó la ventana emergente
            if (!printWindow || printWindow.closed || typeof printWindow.closed === 'undefined') {
                throw new Error('El navegador bloqueó la ventana emergente. Por favor, permite las ventanas emergentes para este sitio.');
            }
            
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

    async printDelivery(factura, items, empresa) {
        try {
            const content = this._formatInvoice(factura, items, empresa);
            
            // Crear ventana de impresión
            const printWindow = window.open('', '_blank');
            
            // Verificar si el navegador bloqueó la ventana emergente
            if (!printWindow || printWindow.closed || typeof printWindow.closed === 'undefined') {
                throw new Error('El navegador bloqueó la ventana emergente. Por favor, permite las ventanas emergentes para este sitio.');
            }
            
            printWindow.document.write(`
                <html>
                    <head>
                        <title>Remito</title>
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
 * Servicio de impresión para impresoras POS térmicas via navegador
 * Genera formato optimizado para tickets de 80mm
 */
class POSPrinterService extends BasePrinterService {
    constructor() {
        super();
        this._lineasCache = {}; // Cache para líneas de comprobantes
    }
    
    /**
     * Obtiene las líneas de comprobantes de un punto de venta
     * @param {number} puntoVtaId - ID del punto de venta
     * @param {boolean} soloVentas - Si true, retorna todas las líneas; si false, solo las que no son "solo_en_ventas"
     * @returns {Promise<Object>} Objeto con arrays cabecera y pie
     */
    async _getLineasComprobantes(puntoVtaId, soloVentas = true) {
        try {
            // Verificar cache
            const cacheKey = `${puntoVtaId}_${soloVentas}`;
            if (this._lineasCache[cacheKey]) {
                return this._lineasCache[cacheKey];
            }
            
            const response = await fetch(`/configuracion/api/lineas_comprobantes/${puntoVtaId}`);
            if (!response.ok) {
                console.warn('No se pudieron obtener las líneas de comprobantes');
                return { cabecera: [], pie: [] };
            }
            
            const data = await response.json();
            if (!data.success) {
                return { cabecera: [], pie: [] };
            }
            
            // Filtrar según soloVentas
            let cabecera = data.cabecera || [];
            let pie = data.pie || [];
            
            if (!soloVentas) {
                // Para remitos/delivery, excluir las líneas marcadas como "solo_en_ventas"
                cabecera = cabecera.filter(l => !l.solo_en_ventas);
                pie = pie.filter(l => !l.solo_en_ventas);
            }
            
            const resultado = { cabecera, pie };
            console.log(`Líneas comprobantes para PV ${puntoVtaId}:`, resultado);
            this._lineasCache[cacheKey] = resultado;
            return resultado;
        } catch (error) {
            console.error('Error al obtener líneas de comprobantes:', error);
            return { cabecera: [], pie: [] };
        }
    }
    
    /**
     * Genera HTML para las líneas de cabecera/pie
     * @param {Array} lineas - Array de objetos con texto
     * @returns {string} HTML de las líneas
     */
    _renderLineas(lineas) {
        if (!lineas || lineas.length === 0) return '';
        return lineas.map(l => `<p class="linea-ticket">${l.texto}</p>`).join('');
    }
    
    async listPrinters() {
        return { 
            success: false, 
            error: "Use la configuración del navegador para seleccionar la impresora POS",
            system: "pos-browser" 
        };
    }
    
    /**
     * Genera la URL del QR de AFIP
     * @param {Object} datos - Datos de la factura
     * @returns {string} URL para el QR de AFIP
     */
    _generarQrAfip(datos) {
        // Mapeo de tipos de comprobante a códigos AFIP
        const tiposComprobante = {
            1: 1,   // Factura A
            2: 2,   // Nota de Débito A
            3: 3,   // Nota de Crédito A
            6: 6,   // Factura B
            7: 7,   // Nota de Débito B
            8: 8,   // Nota de Crédito B
            11: 11, // Factura C
            12: 12, // Nota de Débito C
            13: 13  // Nota de Crédito C
        };
        
        // Mapeo de tipos de documento
        const tiposDocumento = {
            1: 80,  // CUIT
            2: 86,  // CUIL
            3: 96,  // DNI
            4: 99   // Consumidor Final
        };
        
        const qrData = {
            ver: 1,
            fecha: datos.fecha,
            cuit: parseInt(datos.cuitEmisor.replace(/-/g, '')),
            ptoVta: parseInt(datos.puntoVta),
            tipoCmp: tiposComprobante[datos.tipoComprobante] || datos.tipoComprobante,
            nroCmp: parseInt(datos.nroComprobante),
            importe: parseFloat(datos.total),
            moneda: "PES",
            ctz: 1,
            tipoDocRec: tiposDocumento[datos.tipoDocReceptor] || 99,
            nroDocRec: parseInt(datos.docReceptor.replace(/-/g, '')) || 0,
            tipoCodAut: "E",
            codAut: parseInt(datos.cae)
        };
        
        const jsonStr = JSON.stringify(qrData);
        const base64 = btoa(jsonStr);
        
        return `https://www.afip.gob.ar/fe/qr/?p=${base64}`;
    }
    
    async printInvoice(factura, items, empresa) {
        try {
            // Determinar si factura es un array o un objeto
            const esArray = Array.isArray(factura);
            const numero = esArray ? factura[7] : factura.nro_comprobante;
            const fecha = esArray ? factura[1] : factura.fecha;
            const clienteNombre = esArray ? factura[13] : (factura.cliente_nombre || factura.cliente || '');
            const total = esArray ? factura[2] : factura.total;
            const cuitCliente = esArray ? factura[15] : (factura.cliente_documento || factura.cuit || '');
            const tipoDocCliente = esArray ? factura[17] : (factura.cliente_tipo_doc || 99);
            const condicionIva = esArray ? factura[16] : (factura.condicion_iva || '');
            const cae = esArray ? factura[9] : (factura.cae || '');
            const vencimientoCae = esArray ? factura[10] : (factura.cae_vto || factura.vencimiento_cae || '');
            const puntoVta = esArray ? factura[8] : (factura.punto_vta || 1);
            const tipoComprobante = esArray ? factura[6] : (factura.id_tipo_comprobante || 11);
            const letraComprobante = esArray ? (factura[19] || '') : (factura.letra_comprobante || '');
            
            // Obtener líneas de comprobantes (todas las líneas para ventas)
            const lineasComp = await this._getLineasComprobantes(puntoVta, true);
            const lineasCabeceraHtml = this._renderLineas(lineasComp.cabecera);
            const lineasPieHtml = this._renderLineas(lineasComp.pie);
            
            // Extraer número de comprobante sin el punto de venta
            const nroComprobantePuro = numero ? parseInt(numero.toString().split('-').pop()) : 0;
            
            const empresaNombre = typeof empresa === 'object' ? 
                empresa.nombre || empresa['nombre'] : empresa;
            const empresaCuit = typeof empresa === 'object' ? 
                empresa.cuit || empresa['cuit'] || '' : '';
            const empresaDomicilio = typeof empresa === 'object' ? 
                empresa.domicilio || empresa['domicilio'] || '' : '';
            
            // Generar URL del QR de AFIP si hay CAE
            let qrUrl = '';
            if (cae && empresaCuit) {
                qrUrl = this._generarQrAfip({
                    fecha: fecha,
                    cuitEmisor: empresaCuit,
                    puntoVta: puntoVta,
                    tipoComprobante: tipoComprobante,
                    nroComprobante: nroComprobantePuro,
                    total: total,
                    tipoDocReceptor: tipoDocCliente,
                    docReceptor: cuitCliente,
                    cae: cae
                });
            }
            // Datos del QR de AFIP para debug
            console.log('==========================');
            console.log('Datos para QR de AFIP:', {
                fecha: fecha,
                cuitEmisor: empresaCuit,
                puntoVta: puntoVta,
                tipoComprobante: tipoComprobante,
                nroComprobante: nroComprobantePuro,
                total: total,
                tipoDocReceptor: tipoDocCliente,
                docReceptor: cuitCliente,
                cae: cae
            });
            console.log('URL del QR de AFIP:', qrUrl);
            console.log('==========================');
            // Construir HTML para ticket térmico
            let itemsHtml = '';
            items.forEach(item => {
                const esItemArray = Array.isArray(item);
                const cantidad = esItemArray ? item[1] : item.cantidad;
                const descripcion = esItemArray ? item[6] : item.descripcion;
                const precio = esItemArray ? item[3] : item.precio_total;
                
                itemsHtml += `
                    <tr>
                        <td class="qty">${cantidad}</td>
                        <td class="desc">${descripcion}</td>
                        <td class="price">$${parseFloat(precio).toFixed(2)}</td>
                    </tr>
                `;
            });
            
            // Crear ventana de impresión con formato POS
            const printWindow = window.open('', '_blank', 'width=300,height=600');
            
            // Verificar si el navegador bloqueó la ventana emergente
            if (!printWindow || printWindow.closed || typeof printWindow.closed === 'undefined') {
                throw new Error('El navegador bloqueó la ventana emergente. Por favor, permite las ventanas emergentes para este sitio.');
            }
            
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Ticket</title>
                    <style>
                        * { margin: 0; padding: 0; box-sizing: border-box; }
                        body { 
                            font-family: 'Courier New', monospace; 
                            font-size: 12px;
                            width: 80mm;
                            padding: 2mm;
                        }
                        .header { text-align: center; margin-bottom: 5px; }
                        .header h2 { font-size: 14px; margin-bottom: 2px; }
                        .header p { font-size: 10px; }
                        .divider { 
                            border-top: 1px dashed #000; 
                            margin: 5px 0; 
                        }
                        .info { margin: 3px 0; }
                        .info span { font-weight: bold; }
                        table { width: 100%; border-collapse: collapse; }
                        table td { padding: 2px 0; vertical-align: top; }
                        .qty { width: 15%; text-align: center; }
                        .desc { width: 55%; }
                        .price { width: 30%; text-align: right; }
                        .total-row { 
                            font-weight: bold; 
                            font-size: 14px; 
                            text-align: right;
                            margin-top: 5px;
                        }
                        .footer { 
                            text-align: center; 
                            margin-top: 10px; 
                            font-size: 10px;
                        }
                        .linea-ticket {
                            text-align: center;
                            font-size: 10px;
                            margin: 2px 0;
                        }
                        .cae-info { 
                            font-size: 9px; 
                            margin-top: 5px;
                        }
                        .qr-container {
                            text-align: center;
                            margin: 10px 0;
                        }
                        .qr-container img {
                            max-width: 150px;
                            height: auto;
                        }
                        @media print {
                            body { width: 80mm; }
                            @page { 
                                size: 80mm auto;
                                margin: 0;
                            }
                        }
                    </style>
                    <script src="https://cdn.jsdelivr.net/npm/qrcode-generator@1.4.4/qrcode.min.js"></script>
                </head>
                <body>
                    <div class="header">
                        <h2>${empresaNombre}</h2>
                        ${empresaCuit ? `<p>CUIT: ${empresaCuit}</p>` : ''}
                        ${empresaDomicilio ? `<p>${empresaDomicilio}</p>` : ''}
                    </div>
                    
                    ${lineasCabeceraHtml ? `
                    <div class="lineas-cabecera">
                        ${lineasCabeceraHtml}
                    </div>
                    ` : ''}
                    
                    <div class="divider"></div>
                    
                    <div class="info">
                        <span>Comprobante:</span> ${letraComprobante ? letraComprobante + ' - ' : ''}${numero}
                    </div>
                    <div class="info">
                        <span>Fecha:</span> ${fecha}
                    </div>
                    <div class="info">
                        <span>Cliente:</span> ${clienteNombre}
                    </div>
                    ${cuitCliente ? `<div class="info"><span>CUIT/DNI:</span> ${cuitCliente}</div>` : ''}
                    ${condicionIva ? `<div class="info"><span>IVA:</span> ${condicionIva}</div>` : ''}
                    
                    <div class="divider"></div>
                    
                    <table>
                        <tbody>
                            ${itemsHtml}
                        </tbody>
                    </table>
                    
                    <div class="divider"></div>
                    
                    <div class="total-row">
                        TOTAL: $${parseFloat(total).toFixed(2)}
                    </div>
                    
                    ${cae ? `
                        <div class="divider"></div>
                        <div class="cae-info">
                            <div>CAE: ${cae}</div>
                            <div>Vto CAE: ${vencimientoCae}</div>
                        </div>
                        ${qrUrl ? `
                        <div class="qr-container">
                            <div id="qrcode"></div>
                        </div>
                        ` : ''}
                    ` : ''}
                    
                    ${lineasPieHtml ? `
                    <div class="lineas-pie">
                        ${lineasPieHtml}
                    </div>
                    ` : ''}
                    
                    <div class="footer">
                        <p>¡Gracias por su compra!</p>
                    </div>
                    
                    <script>
                        window.onload = function() {
                            ${qrUrl ? `
                            // Generar QR de AFIP
                            var qr = qrcode(0, 'M');
                            qr.addData('${qrUrl}');
                            qr.make();
                            document.getElementById('qrcode').innerHTML = qr.createImgTag(3, 4);
                            ` : ''}
                            
                            // Esperar un momento para que el QR se renderice
                            setTimeout(function() {
                                window.print();
                                setTimeout(function() { window.close(); }, 500);
                            }, 100);
                        };
                    </script>
                </body>
                </html>
            `);
            
            printWindow.document.close();
            
            return { success: true, message: 'Ticket enviado a impresión' };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    async printDelivery(factura, items, empresa) {
        try {
            // Determinar si factura es un array o un objeto
            const esArray = Array.isArray(factura);
            const numero = esArray ? factura[7] : factura.nro_comprobante;
            const fecha = esArray ? factura[1] : factura.fecha;
            const cliente = esArray ? factura[13] : factura.cliente;
            const total = esArray ? factura[2] : factura.total;
            const puntoVta = esArray ? factura[8] : (factura.punto_vta || 1);
            const cuit = esArray ? factura[15] : (factura.cuit || '');
            const condicionIva = esArray ? factura[16] : (factura.condicion_iva || '');
            const cae = esArray ? factura[9] : (factura.cae || '');
            const vencimientoCae = esArray ? factura[10] : (factura.vencimiento_cae || '');
            
            // Obtener líneas de comprobantes (solo las que NO son "solo_en_ventas" para remitos)
            const lineasComp = await this._getLineasComprobantes(puntoVta, false);
            const lineasCabeceraHtml = this._renderLineas(lineasComp.cabecera);
            const lineasPieHtml = this._renderLineas(lineasComp.pie);
            
            const empresaNombre = typeof empresa === 'object' ? 
                empresa.nombre || empresa['nombre'] : empresa;
            const empresaCuit = typeof empresa === 'object' ? 
                empresa.cuit || empresa['cuit'] || '' : '';
            const empresaDomicilio = typeof empresa === 'object' ? 
                empresa.domicilio || empresa['domicilio'] || '' : '';
            
            // Construir HTML para ticket térmico
            let itemsHtml = '';
            
            items.forEach(item => {
                const esItemArray = Array.isArray(item);
                const cantidad = esItemArray ? item[1] : item.cantidad;
                const descripcion = esItemArray ? item[6] : item.descripcion;
                const unitario = esItemArray ? item[2] : item.precio_unitario;
                const precio = esItemArray ? item[3] : item.precio_total;
                itemsHtml += `
                    <tr>
                        <td class="qty">${parseFloat(cantidad).toFixed(2)}</td>
                        <td class="desc">${descripcion}</td>
                        <td class="desc"> <small>$${parseFloat(unitario).toFixed(2)}</small></td>
                        <td class="price">$${parseFloat(precio).toFixed(2)}</td>
                    </tr>
                `;
            });
            
            // Crear ventana de impresión con formato POS
            const printWindow = window.open('', '_blank', 'width=300,height=600');
            
            // Verificar si el navegador bloqueó la ventana emergente
            if (!printWindow || printWindow.closed || typeof printWindow.closed === 'undefined') {
                throw new Error('El navegador bloqueó la ventana emergente. Por favor, permite las ventanas emergentes para este sitio.');
            }
            
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Remito</title>
                    <style>
                        * { margin: 0; padding: 0; box-sizing: border-box; }
                        body { 
                            font-family: 'Courier New', monospace; 
                            font-size: 12px;
                            width: 80mm;
                            padding: 2mm;
                        }
                        .header { text-align: center; margin-bottom: 5px; }
                        .header h2 { font-size: 14px; margin-bottom: 2px; }
                        .header p { font-size: 10px; }
                        .divider { 
                            border-top: 1px dashed #000; 
                            margin: 5px 0; 
                        }
                        .info { margin: 3px 0; }
                        .info span { font-weight: bold; }
                        table { width: 100%; border-collapse: collapse; }
                        table td { padding: 2px 0; vertical-align: top; }
                        .qty { width: 15%; text-align: center; }
                        .desc { width: 55%; }
                        .price { width: 30%; text-align: right; }
                        .total-row { 
                            font-weight: bold; 
                            font-size: 14px; 
                            text-align: right;
                            margin-top: 5px;
                        }
                        .footer { 
                            text-align: center; 
                            margin-top: 10px; 
                            font-size: 10px;
                        }
                        .linea-ticket {
                            text-align: center;
                            font-size: 10px;
                            margin: 2px 0;
                        }
                        .cae-info { 
                            font-size: 9px; 
                            margin-top: 5px;
                        }
                        @media print {
                            body { width: 80mm; }
                            @page { 
                                size: 80mm auto;
                                margin: 0;
                            }
                        }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h2>${empresaNombre}</h2>
                        ${empresaCuit ? `<p>CUIT: ${empresaCuit}</p>` : ''}
                        ${empresaDomicilio ? `<p>${empresaDomicilio}</p>` : ''}
                        <p> DOCUMENTO NO VÁLIDO COMO FACTURA</p>
                    </div>
                    
                    ${lineasCabeceraHtml ? `
                    <div class="lineas-cabecera">
                        ${lineasCabeceraHtml}
                    </div>
                    ` : ''}
                    
                    <div class="divider"></div>
                    
                    <div class="info">
                        <span>Comprobante:</span> ${numero}
                    </div>
                    <div class="info">
                        <span>Fecha:</span> ${fecha}
                    </div>
                    <div class="info">
                        <span>Cliente:</span> ${cliente}
                    </div>
                    ${cuit ? `<div class="info"><span>CUIT:</span> ${cuit}</div>` : ''}
                    ${condicionIva ? `<div class="info"><span>IVA:</span> ${condicionIva}</div>` : ''}
                    
                    <div class="divider"></div>
                    
                    <table>
                        <tbody>
                            ${itemsHtml}
                        </tbody>
                    </table>
                    
                    <div class="divider"></div>
                    
                    <div class="total-row">
                        TOTAL: $${parseFloat(total).toFixed(2)}
                    </div>
                    
                    ${cae ? `
                        <div class="divider"></div>
                        <div class="cae-info">
                            <div>CAE: ${cae}</div>
                            <div>Vto CAE: ${vencimientoCae}</div>
                        </div>
                    ` : ''}
                    
                    ${lineasPieHtml ? `
                    <div class="lineas-pie">
                        ${lineasPieHtml}
                    </div>
                    ` : ''}
                    
                    <div class="footer">
                        <p>¡Gracias por su compra!</p>
                    </div>
                    
                    <script>
                        window.onload = function() {
                            window.print();
                            setTimeout(function() { window.close(); }, 500);
                        };
                    </script>
                </body>
                </html>
            `);
            
            printWindow.document.close();
            
            return { success: true, message: 'Ticket enviado a impresión' };
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

    async printDelivery(factura, items, empresa) {
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
            
            // Datos remito
            commands.push(encoder.encode(`Remito: ${numero}\n`));
            commands.push(encoder.encode(`Fecha: ${fecha}\n`));
            commands.push(encoder.encode(`Cliente: ${cliente}\n`));
            commands.push(encoder.encode("--------------------------------\n"));
            commands.push(encoder.encode("DOCUMENTO NO VÁLIDO COMO FACTURA\n"));
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
        case 'pos':
            return new POSPrinterService();
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
    POSPrinterService,
    ThermalPrinterService,
    getPrinterService
};