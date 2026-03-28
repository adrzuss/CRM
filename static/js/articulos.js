
async function eliminarArticulo(id) {
    const confirmado = await confirmarEliminar('¿Estás seguro de que deseas eliminar este artículo?');
    if (confirmado) {
        fetch(`${BASE_URL}/articulos/api/eliminar/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarExito('Artículo eliminado correctamente.');
                tabla.ajax.reload(); // Recargar la tabla después de eliminar
            } else {
                mostrarError('Error al eliminar el artículo: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error al eliminar el artículo:', error);
            mostrarError('Ocurrió un error al intentar eliminar el artículo.');
        });
    }
}