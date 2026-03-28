import InvoiceHandler from './invoice_handler.js';

const invoiceHandler = new InvoiceHandler();
const statusEl = document.getElementById('status');

// Mostrar mensaje de estado
function showStatus(message, isError = false) {
    statusEl.textContent = message;
    statusEl.className = isError ? 'error' : 'success';
    statusEl.style.display = 'block';
    
    if (!isError) {
        setTimeout(() => {
            statusEl.style.display = 'none';
        }, 3000);
    }
}
// Imprimir factura
document.getElementById('printBtn').addEventListener('click', async () => {
    invoiceHandler.setPrinterType('pos');
    const facturaId = document.getElementById('id').value;
    if (!facturaId) {
        showStatus('Ingrese un ID de factura válido', true);
        return;
    }
    
    try {
        const cae = document.getElementById('cae').value;
        let result;
        if (cae.length === 0 || cae === 'None') {
            //console.log('No CAE, imprimiendo como remito');
            result = await invoiceHandler.printDelivery(facturaId);
        } else {    
            // console.log('Si CAE, imprimiendo como factura');
            result = await invoiceHandler.printInvoice(facturaId);
        }    
        if (result.success) {
            showStatus(result.message);
        } else {
            showStatus(result.error, true);
        }
    } catch (error) {
        showStatus(error.message, true);
    }
});