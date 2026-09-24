"""Tests de impuestos en nuevo_gasto: fórmula total, parsing de filas
impuesto[i], filtro GET, CRUD (400/soft-delete) y recálculo autoritativo.
Mismos patrones de mocks que test_proveedores.py / test_services_ventas.py."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from configs.models import Impuestos
from proveedores.models import ItemsImpC


def _configurar_sesion(client):
    """Configura la sesión para que @check_session no redirija al login."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['tipo_iva'] = '1'
        sess['id_empresa'] = 1
        sess['permisos_menu'] = []


def test_calcular_total_gasto_formula_1240():
    """Fórmula: neto=1000 + iva=210 + importe=30 = 1240, en Decimal."""
    from proveedores.services import calcular_total_gasto

    total = calcular_total_gasto(
        neto=1000, iva=210, exento=0, impint=0,
        pagpersepcuenta=0, mto_percep=0, percep_iibb=0,
        importes_items=[30])

    assert isinstance(total, Decimal)
    assert total == Decimal('1240')


def test_parsear_ids_impuesto_orden_y_filtrado():
    """Extrae solo [idimpuesto], descarta vacíos y ordena por índice."""
    from proveedores.services import parsear_ids_impuesto

    form = {
        'neto': '1000',
        'impuesto[1][importe]': '30',
        'impuesto[1][idimpuesto]': '7',
        'impuesto[0][idimpuesto]': '5',
        'impuesto[2][idimpuesto]': '',
    }

    assert parsear_ids_impuesto(form) == [5, 7]


def test_nuevo_gasto_get_pasa_impuestos_activos_compras(client):
    """GET pasa impuestos= filtrando activo y compras_ventas in (compras, ambas)."""
    _configurar_sesion(client)
    imp_iibb = MagicMock()
    imp_ganancias = MagicMock()

    mock_query_imp = MagicMock()
    mock_query_imp.filter.return_value = mock_query_imp
    mock_query_imp.all.return_value = [imp_iibb, imp_ganancias]

    mock_db_query = MagicMock()
    mock_db_query.join.return_value = mock_db_query
    mock_db_query.all.return_value = []

    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)), \
         patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)), \
         patch('proveedores.routes.render_template', return_value='') as mock_render, \
         patch('configs.models.PlanCtas.query') as mock_plan, \
         patch('utils.db.db.session.query', return_value=mock_db_query), \
         patch('configs.models.Impuestos.query', mock_query_imp):
        mock_plan.all.return_value = []
        response = client.get('/proveedores/nuevo_gasto')

    assert response.status_code == 200
    kwargs = mock_render.call_args[1]
    assert kwargs['impuestos'] == [imp_iibb, imp_ganancias]
    criterios = ' '.join(str(arg) for arg in mock_query_imp.filter.call_args[0])
    assert 'impuestos.activo' in criterios
    assert 'impuestos.compras_ventas' in criterios


def test_htmx_add_impuesto_descripcion_vacia_devuelve_400(client):
    """Descripción vacía → 400 con partial de error y sin fila creada."""
    _configurar_sesion(client)

    response = client.post('/configuracion/htmx/add_impuesto',
                           data={'descripcion': '', 'alicuota': '3',
                                 'compras_ventas': 'compras'})

    assert response.status_code == 400
    assert 'La descripción es obligatoria' in response.get_data(as_text=True)


def test_htmx_add_impuesto_alicuota_invalida_devuelve_400(client):
    """Alícuota ≤ 0 → 400 con partial de error."""
    _configurar_sesion(client)

    response = client.post('/configuracion/htmx/add_impuesto',
                           data={'descripcion': 'IIBB', 'alicuota': '0',
                                 'compras_ventas': 'compras'})

    assert response.status_code == 400
    assert 'mayor a 0' in response.get_data(as_text=True)


def test_htmx_delete_impuesto_borrado_logico(client):
    """Delete setea activo=False (soft) y hace commit; no borra la fila."""
    _configurar_sesion(client)
    impuesto = MagicMock()

    with patch('configs.routes.db.get_or_404',
               return_value=impuesto) as mock_get, \
         patch('configs.routes.db.session.commit') as mock_commit, \
         patch('configs.routes.render_tabla_impuestos', return_value=''):
        response = client.post('/configuracion/htmx/delete_impuesto/5')

    assert response.status_code == 200
    mock_get.assert_called_once_with(Impuestos, 5)
    assert impuesto.activo is False
    mock_commit.assert_called_once()


def test_procesar_nuevo_gasto_recalcula_total_1240(app):
    """AC: neto=1000 + iva=210 + IIBB 3% (=30) → total 1240 exacto en Decimal.

    El total posteado ('99999') se ignora (la fórmula del servidor manda) y el
    impuesto desactivado (activo=False en DB) igual genera fila en items_imp_c.
    """
    from proveedores.services import procesar_nuevo_gasto

    form = {
        'idproveedor': '1',
        'fecha': '2026-01-15',
        'periodo': '2026-01',
        'id_tipo_comprobante': '2',
        'id_plan_cuenta': '3',
        'nro_factura': '0001-00000001',
        'neto': '1000',
        'iva': '210',
        'total': '99999',       # ignorado: total lo recalcula el servidor
        'efectivo': '0',
        'ctacte': '0',
        'impuesto[0][idimpuesto]': '5',
        'impuesto[0][importe]': '30',  # posteada: display-only, no confiar
    }

    agregados = []
    mock_session = MagicMock()
    mock_session.add.side_effect = lambda obj: agregados.append(obj)
    mock_session.flush.side_effect = lambda: setattr(agregados[0], 'id', 1)
    impuesto_bd = MagicMock()
    impuesto_bd.alicuota = Decimal('3.000000')
    impuesto_bd.activo = False  # desactivado: snapshot en items_imp_c
    mock_session.get.return_value = impuesto_bd

    with app.test_request_context():
        from flask import session
        session['user_id'] = 1
        with patch('proveedores.services.db.session', mock_session):
            procesar_nuevo_gasto(form, idsucursal=1)

    factura = agregados[0]
    items = [obj for obj in agregados if isinstance(obj, ItemsImpC)]

    assert isinstance(factura.total, Decimal)
    assert factura.total == Decimal('1240')
    assert factura.neto == Decimal('1000')
    assert len(items) == 1
    assert items[0].idfactura == 1
    assert items[0].idimpuesto == 5
    assert items[0].alicuota == Decimal('3.000000')  # alícuota de la DB
    assert items[0].importe == Decimal('30')
    mock_session.get.assert_called_once_with(Impuestos, 5)
    mock_session.commit.assert_called_once()


def _form_gasto_minimo(neto=None):
    """Form mínimo que alcanza el parse de neto (el guard va antes del add)."""
    form = {'idproveedor': '1', 'fecha': '2026-01-15', 'periodo': '2026-01',
            'id_tipo_comprobante': '2', 'id_plan_cuenta': '3',
            'nro_factura': '0001-00000001'}
    if neto is not None:
        form['neto'] = neto
    return form


def _rechazar_neto(form):
    """procesar_nuevo_gasto debe tirar ValueError sin tocar la sesión."""
    from proveedores.services import procesar_nuevo_gasto
    mock_session = MagicMock()
    with patch('proveedores.services.db.session', mock_session):
        with pytest.raises(ValueError, match='Neto inválido'):
            procesar_nuevo_gasto(form, idsucursal=1)
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()


def test_procesar_nuevo_gasto_neto_ausente_rechazado():
    """neto ausente (tab viejo / cliente scripted) → ValueError, sin persistir."""
    _rechazar_neto(_form_gasto_minimo())


@pytest.mark.parametrize('neto', ['0', '-5', 'NaN'])
def test_procesar_nuevo_gasto_neto_invalido_rechazado(neto):
    """neto=0 / negativo / NaN → rechazado igual, sin persistir el gasto."""
    _rechazar_neto(_form_gasto_minimo(neto))


def test_nuevo_gasto_post_neto_ausente_flash_error_sin_grabar(client):
    """POST sin neto → flash de error, redirige y NO flash 'Gasto grabado'."""
    _configurar_sesion(client)
    with client.session_transaction() as sess:
        sess['id_sucursal'] = 1
    with patch('utils.msg_alertas.obtener_alertas', return_value=([], 0)), \
         patch('utils.msg_alertas.obtener_mensajes', return_value=([], 0)):
        response = client.post('/proveedores/nuevo_gasto', data=_form_gasto_minimo())
    assert response.status_code == 302
    assert '/proveedores/nuevo_gasto' in response.headers['Location']
    with client.session_transaction() as sess:
        flash_messages = [mensaje for _, mensaje in sess.get('_flashes', [])]
    assert 'Gasto grabado' not in flash_messages
    assert any('Neto inválido' in mensaje for mensaje in flash_messages)
