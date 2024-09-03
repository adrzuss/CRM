from flask import Blueprint, render_template, request, redirect, flash, url_for
from datetime import datetime
from sqlalchemy import func
from utils.utils import format_currency
from models.clientes import Clientes
from models.ctactecli import CtaCteCli
from datetime import date
from utils.db import db

bp_ctactecli = Blueprint('ctactecli', __name__, template_folder='../templates/ctactecli')

@bp_ctactecli.route('/addCtaCte', methods = ['POST','GET'])
def add_cta_cte():
    if request.method == 'POST':
        idcliente = request.form['idcliente']
        fecha = request.form['fecha']
        debe = request.form['debe']
        haber = request.form['haber']
        try:
            ctactecli = CtaCteCli(idcliente, fecha, debe, haber)
            db.session.add(ctactecli)
            db.session.commit()
            flash('Movimiento de cta cte grabado')
            return redirect(url_for('ctactecli.lst_cta_cte', id=idcliente))
        except Exception as e:
            db.session.rollback()
            flash(f'Error grabado ctacte: {e}')
            return redirect(url_for('ctactecli.lst_cta_cte', id=idcliente))
    
    if request.method == 'GET':
        return render_template('ctacte-cli.html')

@bp_ctactecli.route('/lstctacte/<id>)')
def lst_cta_cte(id):
    cliente = Clientes.query.get_or_404(id)
    movimientos = CtaCteCli.query.filter_by(idcliente=cliente.id).all()
    return render_template('lst-ctactecli.html', movimientos=movimientos, nomCliente=cliente.nombre)

@bp_ctactecli.route('/saldos', methods=['GET', 'POST'])
def saldos():
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
        return render_template('saldos-ctacte.html', saldos=saldos, desde=fecha_str)
    desde = datetime.today().replace(day=1).strftime("%Y-%m-%d")
    return render_template('saldos-ctacte.html', desde=desde)

def get_saldo_clientes():
    try:
        saldos_cta_cte = db.session.query(func.sum(CtaCteCli.debe).label('debe'), func.sum(CtaCteCli.haber).label('haber')).all()
        saldos =  format_currency( float(saldos_cta_cte[0][0] - saldos_cta_cte[0][1]))
        return saldos
    except:
        return format_currency(0.0)