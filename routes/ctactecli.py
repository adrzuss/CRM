from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify
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
        importe = request.form['importe']
        debe_haber = request.form.get('debe_haber')
        try:
            if debe_haber == 'debe':
                debe = importe
                haber = 0
            else:
                debe = 0
                haber = importe
            ctactecli = CtaCteCli(idcliente, fecha, debe, haber)
            db.session.add(ctactecli)
            db.session.commit()
            flash('Movimiento de cta cte grabado')
            return redirect(url_for('ctactecli.lst_cta_cte_cli', id=idcliente))
        except Exception as e:
            db.session.rollback()
            flash(f'Error grabado ctacte: {e}')
            return redirect(url_for('ctactecli.lst_cta_cte_cli', id=idcliente))
    
    if request.method == 'GET':
        return render_template('ctacte-cli.html')

@bp_ctactecli.route('/lstctactecli/<id>)')
def lst_cta_cte_cli(id):
    cliente = Clientes.query.get_or_404(id)
    movimientos = CtaCteCli.query.filter_by(idcliente=cliente.id).all()
    saldo_total = saldo_ctacte(cliente.id)
    saldoTotal = saldo_total['total_debe'] - saldo_total['total_haber']
    return render_template('lst-ctactecli.html', movimientos=movimientos, idCliente=cliente.id, nomCliente=cliente.nombre, saldoTotal=saldoTotal )


# Obtiene el detalle de los saldos de lac cta cte de los clientes
@bp_ctactecli.route('/saldoscli', methods=['GET', 'POST'])
def saldoscli():
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
        return render_template('saldos-ctactecli.html', saldos=saldos, desde=fecha_str)
    desde = datetime.today().replace(day=1).strftime("%Y-%m-%d")
    return render_template('saldos-ctactecli.html', desde=desde)

def saldo_ctacte(idcliente):
    # Consulta SQLAlchemy para sumar los campos "debe" y "haber"
    result = db.session.query(
        func.sum(CtaCteCli.debe).label('total_debe'),
        func.sum(CtaCteCli.haber).label('total_haber')
    ).filter(CtaCteCli.idcliente == idcliente).one()

    # Convertir el resultado a un diccionario
    total_debe = result.total_debe if result.total_debe else 0
    total_haber = result.total_haber if result.total_haber else 0
    # Devolver el resultado como JSON
   
    return {'total_debe': total_debe, 'total_haber': total_haber}

def get_saldo_clientes():
    try:
        saldos_cta_cte = db.session.query(func.sum(CtaCteCli.debe).label('debe'), func.sum(CtaCteCli.haber).label('haber')).all()
        saldos =  format_currency( float(saldos_cta_cte[0][0] - saldos_cta_cte[0][1]))
        return saldos
    except:
        return format_currency(0.0)