from flask import Blueprint, render_template, request, redirect, flash, url_for, g, session
from datetime import datetime
from sqlalchemy import func
from models.clientes import Clientes
from models.ctactecli import CtaCteCli
from models.entidades_cred import EntidadesCred
from services.ctactecli import saldo_ctacte, procesar_movimiento_cta_cte, get_lst_vencidas
from utils.db import db
from utils.utils import check_session
from utils.msg_alertas import alertas_mensajes

bp_ctactecli = Blueprint('ctactecli', __name__, template_folder='../templates/ctactecli')

@bp_ctactecli.route('/addCtaCteCli', methods = ['POST','GET'])
@check_session
@alertas_mensajes
def add_cta_cte_cli():
    if request.method == 'POST':
        try:
            ctacte_cli = procesar_movimiento_cta_cte(request.form)
            flash('Movimiento de cta cte grabado')
            return redirect(url_for('ctactecli.lst_cta_cte_cli', id=ctacte_cli.idcliente))
        except Exception as e:
            flash(f'Error grabado ctacte: {e}')
            return redirect(url_for('ctactecli.lst_cta_cte_cli', id=ctacte_cli.idcliente))
    
    if request.method == 'GET':
        return render_template('ctacte-cli.html', alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_ctactecli.route('/lstctactecli/<id>)')
@check_session
@alertas_mensajes
def lst_cta_cte_cli(id):
    cliente = Clientes.query.get_or_404(id)
    entidades = EntidadesCred.query.all()
    movimientos = CtaCteCli.query.filter_by(idcliente=cliente.id).order_by(CtaCteCli.fecha.desc()).all()
    saldo_total = saldo_ctacte(cliente.id)
    saldoTotal = saldo_total['total_debe'] - saldo_total['total_haber']
    
    return render_template('lst-ctactecli.html', movimientos=movimientos, idCliente=cliente.id, nomCliente=cliente.nombre, entidades=entidades, saldoTotal=saldoTotal, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

@bp_ctactecli.route('/saldosctactecli', methods=['GET'])
@check_session
@alertas_mensajes
def saldosctactecli():
    # Realizar la consulta agregada
    saldos = db.session.query(
        Clientes.nombre,
        Clientes.id.label('idcliente'),
        func.sum(func.coalesce(CtaCteCli.debe, 0)).label('total_debe'),  # Usar coalesce para devolver 0 si es NULL
        func.sum(func.coalesce(CtaCteCli.haber, 0)).label('total_haber')
    ).outerjoin(
        CtaCteCli, CtaCteCli.idcliente == Clientes.id
    ).filter(
        Clientes.ctacte == True
    ).group_by(
        Clientes.nombre,
        Clientes.id
    ).all()
    print(saldos)
    # Pasar los resultados a la plantilla
    return render_template('saldos-ctactecli.html', saldos=saldos,  alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)



# Obtiene el detalle de los saldos de lac cta cte de los clientes
@bp_ctactecli.route('/movsctactecli', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def movsctactecli():
    if request.method == 'POST':
        # Obtener la fecha del formulario
        fecha_str = request.form['fecha']
        
        # Convertir la fecha a un objeto datetime
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
        
        # Realizar la consulta agregada
        saldos = db.session.query(
            Clientes.nombre,
            CtaCteCli.idcliente,
            func.sum(CtaCteCli.debe).label('total_debe'),
            func.sum(CtaCteCli.haber).label('total_haber')
        ).join(
            Clientes, Clientes.id == CtaCteCli.idcliente        
        ).filter(
            CtaCteCli.fecha >= fecha
        ).group_by(
            Clientes.nombre,
            CtaCteCli.idcliente
        ).all()

        # Pasar los resultados a la plantilla
        return render_template('movs-ctactecli.html', saldos=saldos, desde=fecha_str, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
    desde = datetime.today().replace(day=1).strftime("%Y-%m-%d")
    return render_template('movs-ctactecli.html', desde=desde, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)

# Obtiene el detalle de los saldos de lac cta cte de los clientes
@bp_ctactecli.route('/lst_cc_cli_vencidas', methods=['GET'])
@check_session
@alertas_mensajes
def lst_cc_cli_vencidas():
    vencidas = get_lst_vencidas()
    return render_template('lst-ctacte-vencidas.html', vencidas=vencidas, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas, mensajes=g.mensajes, cantidadMensajes=g.cantidadMensajes)
   