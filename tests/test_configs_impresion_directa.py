"""
Tests para el modo de impresion por punto de venta (impresion_directa).

Verifica:
  - get_impresion_directa: lector None-safe del modo por punto de venta
  - grabarDatosPtoVta: persistencia del radio en ambas ramas (actualizacion
    y alta) con el gate server-side (sin pos_printer se fuerza vista previa)
  - get_punto_vta: el JSON expone impresion_directa

Estrategia de mocks (estilo casa, ver test_services_ventas.py):
  - flask.session: session real dentro de app.test_request_context()
    (NO se parchea, porque patch sobre LocalProxy causa problemas)
  - db.session.get/add/commit: se parchean para evitar DB real
  - flash: se parchea a nivel de modulo configs.services
"""

from unittest.mock import MagicMock, patch


# ──────────────────────────────────────────────
# get_impresion_directa
# ──────────────────────────────────────────────

def test_get_impresion_directa_true(app):
    """Fila con impresion_directa activo retorna True."""
    mock_pv = MagicMock()
    mock_pv.impresion_directa = True

    with patch('configs.services.db.session.get', return_value=mock_pv):
        from configs.services import get_impresion_directa

        assert get_impresion_directa(1) is True


def test_get_impresion_directa_false(app):
    """Fila con impresion_directa inactivo retorna False."""
    mock_pv = MagicMock()
    mock_pv.impresion_directa = False

    with patch('configs.services.db.session.get', return_value=mock_pv):
        from configs.services import get_impresion_directa

        assert get_impresion_directa(1) is False


def test_get_impresion_directa_sin_fila(app):
    """Punto de venta inexistente retorna False."""
    with patch('configs.services.db.session.get', return_value=None):
        from configs.services import get_impresion_directa

        assert get_impresion_directa(999) is False


def test_get_impresion_directa_id_none(app):
    """id None retorna False sin consultar la base."""
    with patch('configs.services.db.session.get') as mock_get:
        from configs.services import get_impresion_directa

        assert get_impresion_directa(None) is False
        mock_get.assert_not_called()


# ──────────────────────────────────────────────
# grabarDatosPtoVta (persistencia + gate)
# ──────────────────────────────────────────────

def _form(id_puntoventa='5', pos_printer='1', impresion_directa='1'):
    """Formulario minimo del alta/edicion de punto de venta."""
    return {
        'id_puntoventa': id_puntoventa,
        'puntoVenta': 3,
        'idsucursal': 1,
        'pos_printer': pos_printer,
        'impresion_directa': impresion_directa,
    }


def test_grabar_pto_vta_actualiza_directo(app):
    """Rama de actualizacion: radio '1' con pos_printer activo persiste 1."""
    mock_pv = MagicMock()

    with app.test_request_context():
        from flask import session
        session['tipo_iva'] = 3

        with patch('configs.services.db.session.get', return_value=mock_pv), \
             patch('configs.services.db.session.commit'), \
             patch('configs.services.flash'):
            from configs.services import grabarDatosPtoVta

            resultado = grabarDatosPtoVta(_form())

            assert resultado == '5'
            assert mock_pv.impresion_directa == 1


def test_grabar_pto_vta_actualiza_preview(app):
    """Rama de actualizacion: radio '0' persiste 0 (vista previa)."""
    mock_pv = MagicMock()

    with app.test_request_context():
        from flask import session
        session['tipo_iva'] = 3

        with patch('configs.services.db.session.get', return_value=mock_pv), \
             patch('configs.services.db.session.commit'), \
             patch('configs.services.flash'):
            from configs.services import grabarDatosPtoVta

            grabarDatosPtoVta(_form(impresion_directa='0'))

            assert mock_pv.impresion_directa == 0


def test_grabar_pto_vta_gate_actualizacion(app):
    """Gate server-side: sin pos_printer, impresion_directa='1' se fuerza a 0."""
    mock_pv = MagicMock()

    with app.test_request_context():
        from flask import session
        session['tipo_iva'] = 3

        with patch('configs.services.db.session.get', return_value=mock_pv), \
             patch('configs.services.db.session.commit'), \
             patch('configs.services.flash'):
            from configs.services import grabarDatosPtoVta

            grabarDatosPtoVta(_form(pos_printer='', impresion_directa='1'))

            assert mock_pv.impresion_directa == 0


def test_grabar_pto_vta_alta_gate(app):
    """Rama de alta: sin pos_printer, impresion_directa='1' se fuerza a 0."""
    with app.test_request_context():
        from flask import session
        session['tipo_iva'] = 3

        with patch('configs.services.db.session.get') as mock_get, \
             patch('configs.services.db.session.add') as mock_add, \
             patch('configs.services.db.session.commit'), \
             patch('configs.services.flash'):
            from configs.services import grabarDatosPtoVta

            grabarDatosPtoVta(_form(id_puntoventa='', pos_printer='', impresion_directa='1'))

            mock_get.assert_not_called()
            mock_add.assert_called_once()
            pv_alta = mock_add.call_args[0][0]
            assert pv_alta.impresion_directa == 0


def test_grabar_pto_vta_alta_directo(app):
    """Rama de alta: radio '1' con pos_printer activo persiste 1."""
    with app.test_request_context():
        from flask import session
        session['tipo_iva'] = 3

        with patch('configs.services.db.session.get'), \
             patch('configs.services.db.session.add') as mock_add, \
             patch('configs.services.db.session.commit'), \
             patch('configs.services.flash'):
            from configs.services import grabarDatosPtoVta

            grabarDatosPtoVta(_form(id_puntoventa=''))

            pv_alta = mock_add.call_args[0][0]
            assert pv_alta.impresion_directa == 1


# ──────────────────────────────────────────────
# get_punto_vta (JSON de sesion)
# ──────────────────────────────────────────────

def test_get_punto_vta_incluye_impresion_directa(client):
    """El JSON de get_punto_vta expone impresion_directa."""
    with client.session_transaction() as sess:
        sess['idPuntoVenta'] = 5

    with patch('ventas.routes.getPosPrinter', return_value=('1', 1)), \
         patch('ventas.routes.get_impresion_directa', return_value=True), \
         patch('ventas.routes.db.session.execute') as mock_execute:
        mock_execute.return_value.scalar_one_or_none.return_value = None
        response = client.get('/ventas/get_punto_vta')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['impresion_directa'] is True
