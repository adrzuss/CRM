from flask import render_template, Blueprint
from routes.ventas import get_vta_hoy, get_vta_semana, ventas_por_mes, pagos_hoy
from routes.ctactecli import get_saldo_clientes
from routes.ctacteprov import get_saldo_proveedores

bp_tableros = Blueprint('tableros', __name__, template_folder='../templates/tableros')

@bp_tableros.route('/tablero-inicial')
def tablero_inicial():
    vta_hoy = get_vta_hoy()
    vta_semana = get_vta_semana()
    vta_6_meses = ventas_por_mes()
    saldo_clientes = get_saldo_clientes()
    saldo_proveedores = get_saldo_proveedores()
    pagosHoy = pagos_hoy()
    return render_template('tablero.html', vta_hoy=vta_hoy, vta_semana=vta_semana, saldo_clientes=saldo_clientes, saldo_proveedores=saldo_proveedores, meses=vta_6_meses['meses'], operaciones=vta_6_meses['operaciones'], tipoPagoss=pagosHoy['tipo_pago'], cantPagoss=pagosHoy['total_pago'])