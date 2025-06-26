
function eliminarArticulo(id) {
    if (confirm('¿Estás seguro de que deseas eliminar este artículo?')) {
        fetch(`${BASE_URL}/articulos/api/eliminar/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Artículo eliminado correctamente.');
                tabla.ajax.reload(); // Recargar la tabla después de eliminar
            } else {
                alert('Error al eliminar el artículo: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error al eliminar el artículo:', error);
            alert('Ocurrió un error al intentar eliminar el artículo.');
        });
    }
}