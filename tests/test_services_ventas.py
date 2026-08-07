"""
Tests para los servicios de ventas del proyecto CRM.

Verifica funciones del módulo services/ventas con mocking de DB y sesión.
Se testean:

  - getNroComprobante: incremento de numeración según tipo de comprobante
  - Fórmulas de cálculo matemático en procesar_pagos (cálculo de intereses)

Estrategia de mocks:
  - flask.session: se usa el session real dentro de app.test_request_context()
    (NO se parchea, porque patch sobre LocalProxy causa problemas con AsyncMock)
  - Modelos (PuntosVenta): se parchea .query.get para retornar datos de prueba
  - db.session: se parchea commit/rollback para evitar DB real
  - PagosFV, MovEntidades, CtaCteCli, Creditos: se parchean a nivel del módulo
    donde se usan (services.ventas.ventas) porque fueron importados con
    `from models.xxx import ...`
"""

from unittest.mock import patch, MagicMock
from decimal import Decimal


# ──────────────────────────────────────────────
# Tests para getNroComprobante
# ──────────────────────────────────────────────

def _setup_mock_punto_vta():
    """Crea un MagicMock que simula un PuntosVenta con contadores."""
    pv = MagicMock()
    pv.ultima_fac_a = 5
    pv.ultima_fac_b = 10
    pv.ultima_tkt = 20
    pv.ultima_nc_a = 3
    pv.ultima_nc_b = 7
    pv.ultima_deb_c = 1
    pv.ultima_fac_c = 15
    pv.ultima_nc_c = 2
    pv.ultimo_rem_x = 0
    return pv


def test_get_nro_comprobante_factura_a(app):
    """
    Test getNroComprobante con tipo 1 (Factura A).

    Usa app.test_request_context() y el session real de Flask
    (NO parchea flask.session). Luego parchea PuntosVenta.query
    y db.session.commit.

    Verifica que:
      - Retorna el formato '0001-00000005' (punto_vta + nro formateado)
      - El contador ultima_fac_A se incrementa en 1
    """
    mock_pv = _setup_mock_punto_vta()

    with app.test_request_context():
        # Usamos el session real de Flask dentro del request context
        from flask import session
        session['idPuntoVenta'] = '0001'

        with patch('services.ventas.facturacion.db.session.get', return_value=mock_pv):
            with patch('utils.db.db.session.commit'):

                from services.ventas.facturacion import getNroComprobante

                resultado = getNroComprobante(1)

                assert resultado == '0001-00000005'
                assert mock_pv.ultima_fac_a == 6


def test_get_nro_comprobante_factura_b(app):
    """Test getNroComprobante con tipo 2 (Factura B)."""
    mock_pv = _setup_mock_punto_vta()

    with app.test_request_context():
        from flask import session
        session['idPuntoVenta'] = '0001'

        with patch('services.ventas.facturacion.db.session.get', return_value=mock_pv):
            with patch('utils.db.db.session.commit'):

                from services.ventas.facturacion import getNroComprobante

                resultado = getNroComprobante(2)

                assert resultado == '0001-00000010'
                assert mock_pv.ultima_fac_b == 11


def test_get_nro_comprobante_nota_credito_a(app):
    """Test getNroComprobante con tipo 4 (Nota de Crédito A)."""
    mock_pv = _setup_mock_punto_vta()

    with app.test_request_context():
        from flask import session
        session['idPuntoVenta'] = '0001'

        with patch('services.ventas.facturacion.db.session.get', return_value=mock_pv):
            with patch('utils.db.db.session.commit'):

                from services.ventas.facturacion import getNroComprobante

                resultado = getNroComprobante(4)

                assert resultado == '0001-00000003'
                assert mock_pv.ultima_nc_a == 4


def test_get_nro_comprobante_factura_c(app):
    """Test getNroComprobante con tipo 10 (Factura C)."""
    mock_pv = _setup_mock_punto_vta()

    with app.test_request_context():
        from flask import session
        session['idPuntoVenta'] = '0002'

        with patch('services.ventas.facturacion.db.session.get', return_value=mock_pv):
            with patch('utils.db.db.session.commit'):

                from services.ventas.facturacion import getNroComprobante

                resultado = getNroComprobante(10)

                assert resultado == '0002-00000015'
                assert mock_pv.ultima_fac_c == 16


def test_get_nro_comprobante_remito(app):
    """Test getNroComprobante con tipo 20 (Remito)."""
    mock_pv = _setup_mock_punto_vta()

    with app.test_request_context():
        from flask import session
        session['idPuntoVenta'] = '0001'

        with patch('services.ventas.facturacion.db.session.get', return_value=mock_pv):
            with patch('utils.db.db.session.commit'):

                from services.ventas.facturacion import getNroComprobante

                resultado = getNroComprobante(20)

                assert resultado == '0001-00000000'
                assert mock_pv.ultimo_rem_x == 1


# ──────────────────────────────────────────────
# Tests para cálculos matemáticos en procesar_pagos
# ──────────────────────────────────────────────

def test_procesar_pagos_intereses_sin_tarjeta(app):
    """
    Test de cálculo de intereses en procesar_pagos sin pago con tarjeta.

    Si tarjeta=0, los intereses deben ser 0.
    Verifica que el cálculo matemático es correcto:
      intereses = 0.0 (sin tarjeta)
      totalPagos = efectivo + ctacte + bonificacion + credito - total

    Parcheamos los modelos en el namespace de services.ventas.ventas
    porque allí fueron importados con `from models.xxx import Yyy`.
    """
    from services.ventas.ventas import procesar_pagos

    with app.test_request_context():
        with patch('services.ventas.ventas.PagosFV') as mock_pagos_fv:
            with patch('services.ventas.ventas.MovEntidades') as mock_mov_ent:
                with patch('services.ventas.ventas.CtaCteCli'):
                    with patch('services.ventas.ventas.Creditos'):
                        with patch('utils.db.db.session') as mock_db:
                            mock_db.session.add.return_value = None

                            procesar_pagos(
                                1, 1, '2024-06-15',
                                Decimal('1000'),  # total
                                Decimal('500'),   # efectivo
                                Decimal('0'),     # tarjeta
                                0, 1, 1, '', '',  # entidad, cuotas, coef, doc, tel
                                Decimal('300'),   # ctacte
                                Decimal('200'),   # bonificacion
                                None,             # idcredito
                                Decimal('0'),     # credito
                                0,                # nota_credito
                                None,             # id_vale
                                None              # vale
                            )

                            # Verificar que se agregaron pagos:
                            # efectivo=500, ctacte=300, bonificacion=200, total=1000
                            # intereses=0, totalPagos=500+300+200-1000=0
                            # → sin vuelto. Se deben haber creado 3 PagosFV
                            assert mock_pagos_fv.call_count == 3
                            # Verificar pagos llamados con los totales correctos
                            calls = mock_pagos_fv.call_args_list
                            # efectivo=500
                            assert calls[0][1]['total'] == Decimal('500')
                            # ctacte=300
                            assert calls[1][1]['total'] == Decimal('300')
                            # bonificacion=200
                            assert calls[2][1]['total'] == Decimal('200')


# ──────────────────────────────────────────────
# Tests para idempotencia en procesar_nueva_venta
# ──────────────────────────────────────────────


def _make_form_dict(data):
    """Convierte un dict en un objeto que soporta form['key'] y form.get()."""
    d = dict(data)
    m = MagicMock()
    m.get.side_effect = lambda key, default=None: d.get(key, default)
    m.__getitem__.side_effect = lambda key: d[key]
    return m


def test_idempotency_uuid_invalido(app):
    """
    REQ-01: UUID inválido debe lanzar ValueError (envuelto en Exception
    por el except general de procesar_nueva_venta).
    """
    with app.test_request_context():
        from flask import session
        session['user_id'] = 1
        session['idPuntoVenta'] = '0001'

        form = _make_form_dict({'_idempotency_key': 'no-es-un-uuid'})

        import pytest
        with pytest.raises(Exception, match="Formato de clave de idempotencia inválido"):
            from services.ventas.ventas import procesar_nueva_venta
            procesar_nueva_venta(form, 1)


def test_idempotency_early_return(app):
    """
    REQ-02: Si la factura con la misma key ya existe, retorna early
    (nro_comprobante, id) sin procesar items/pagos.
    """
    with app.test_request_context():
        from flask import session
        session['user_id'] = 1
        session['idPuntoVenta'] = '0001'

        form = MagicMock()
        form.get.side_effect = lambda key, default=None: {
            '_idempotency_key': '550e8400-e29b-41d4-a716-446655440000',
        }.get(key, default)

        mock_factura = MagicMock()
        mock_factura.id = 42
        mock_factura.nro_comprobante = '0001-00000005'

        with patch('services.ventas.ventas.Factura') as mock_factura_cls:
            mock_factura_cls.query.filter_by.return_value.first.return_value = mock_factura

            from services.ventas.ventas import procesar_nueva_venta
            resultado = procesar_nueva_venta(form, 1)

            assert resultado == ('0001-00000005', 42)
            mock_factura_cls.query.filter_by.assert_called_once_with(
                idempotency_key='550e8400-e29b-41d4-a716-446655440000'
            )


def test_no_idempotency_key_skips_check(app):
    """
    REQ-01: Sin _idempotency_key, el bloque de idempotencia se salta
    (verificamos que NO se llama a Factura.query.filter_by).
    """
    with app.test_request_context():
        from flask import session
        session['user_id'] = 1
        session['idPuntoVenta'] = '0001'

        form = _make_form_dict({
            'idcliente': '1',
            'fecha': '2024-06-15',
            'idlista': '1',
            'id_tipo_comprobante': '1',
            'efectivo': '1000',
            'tarjeta': '0',
            'cuotas': '1',
            'coeficiente': '1',
            'documento': '',
            'telefono': '',
            'entidad': '0',
            'ctacte': '0',
            'bonificacion': '0',
            'totalFactura': '1000',
            'nro_comprobante': '',
        })

        from models.ventas import Factura as FacturaModel
        with patch('services.ventas.ventas.Factura', spec=FacturaModel) as mock_factura:
            with patch('services.ventas.ventas.procesar_items', return_value=(0, 0, 0, 0, 0, 0)):
                with patch('services.ventas.ventas.procesar_pagos'):
                    with patch('services.ventas.ventas.getNroComprobante', return_value='0001-00000001'):
                        with patch('utils.db.db.session.commit'):
                            with patch('utils.db.db.session'):
                                from services.ventas.ventas import procesar_nueva_venta

                                resultado = procesar_nueva_venta(form, 1)

                                assert resultado is not None
                                filter_by_calls = mock_factura.query.filter_by.call_args_list
                                idempotency_calls = [
                                    c for c in filter_by_calls
                                    if 'idempotency_key' in str(c)
                                ]
                                assert len(idempotency_calls) == 0


def test_idempotency_integrity_error_rollback_recovery(app):
    """
    REQ-02: IntegrityError en commit → rollback + re-query por key + 
    retorna factura existente.
    """
    from sqlalchemy.exc import IntegrityError
    from models.ventas import Factura as FacturaModel

    with app.test_request_context():
        from flask import session
        session['user_id'] = 1
        session['idPuntoVenta'] = '0001'

        form = _make_form_dict({
            '_idempotency_key': '550e8400-e29b-41d4-a716-446655440000',
            'idcliente': '1',
            'fecha': '2024-06-15',
            'idlista': '1',
            'id_tipo_comprobante': '1',
            'efectivo': '1000',
            'tarjeta': '0',
            'cuotas': '1',
            'coeficiente': '1',
            'documento': '',
            'telefono': '',
            'entidad': '0',
            'ctacte': '0',
            'bonificacion': '0',
            'totalFactura': '1000',
            'nro_comprobante': '',
        })

        mock_factura_existente = MagicMock()
        mock_factura_existente.id = 42
        mock_factura_existente.nro_comprobante = '0001-00000005'

        with patch('services.ventas.ventas.Factura', spec=FacturaModel) as mock_factura_cls:
            mock_factura_cls.query.filter_by.side_effect = [
                MagicMock(first=lambda: None),                    # 1ra: early check → None
                MagicMock(first=lambda: mock_factura_existente),  # 2da: tras IntegrityError
            ]

            with patch('services.ventas.ventas.procesar_items', return_value=(Decimal('1000'), Decimal('800'), Decimal('0'), Decimal('200'), Decimal('0'), Decimal('0'))):
                with patch('services.ventas.ventas.procesar_pagos'):
                    with patch('services.ventas.ventas.getNroComprobante', return_value='0001-00000005'):
                        with patch('utils.db.db.session') as mock_session:
                            mock_session.commit.side_effect = IntegrityError("test", "orig", "stmt")

                            from services.ventas.ventas import procesar_nueva_venta

                            resultado = procesar_nueva_venta(form, 1)

                            assert resultado == ('0001-00000005', 42)
                            assert mock_session.rollback.called
    """
    Test de cálculo de intereses y vuelto en procesar_pagos con tarjeta.

    Verifica que:
      - tarjeta=1100, coeficiente=1.1 → intereses=1000
      - total = 1000
      - efectivo=500, tarjeta=1100, ctacte=0, bonificacion=0, credito=0
      - totalPagos = 500 + (1100-1000) + 0 + 0 + 0 = 600
      - totalPagos - total = 600 - 1000 = -400 → NO hay vuelto (negativo)
      - efectivo no se modifica
    """
    from services.ventas.ventas import procesar_pagos

    with app.test_request_context():
        with patch('services.ventas.ventas.PagosFV') as mock_pagos_fv:
            with patch('services.ventas.ventas.MovEntidades') as mock_mov_ent:
                with patch('services.ventas.ventas.CtaCteCli'):
                    with patch('services.ventas.ventas.Creditos'):
                        with patch('utils.db.db.session') as mock_db:
                            mock_db.session.add.return_value = None

                            procesar_pagos(
                                1, 1, '2024-06-15',
                                Decimal('1000'),  # total
                                Decimal('500'),   # efectivo
                                Decimal('1100'),  # tarjeta
                                5, 1, Decimal('1.1'),
                                '12345678', '555-1234',
                                Decimal('0'),    # ctacte
                                Decimal('0'),    # bonificacion
                                None,            # idcredito
                                Decimal('0'),    # credito
                                0,               # nota_credito
                                None,            # id_vale
                                None             # vale
                            )

                            # Verificar que se agregaron 2 PagosFV (efectivo + tarjeta)
                            assert mock_pagos_fv.call_count == 2
                            # Verificar que se creó un MovEntidades
                            mock_mov_ent.assert_called_once()
                            # Verificar totales correctos
                            calls = mock_pagos_fv.call_args_list
                            # efectivo=500 (totalPagos negativo, no hay vuelto)
                            assert calls[0][1]['total'] == Decimal('500')
                            # tarjeta=1100
                            assert calls[1][1]['total'] == Decimal('1100')
