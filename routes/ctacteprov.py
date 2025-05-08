from flask import Blueprint, render_template, request, redirect, flash, url_for
from sqlalchemy import func
from datetime import datetime
from utils.utils import format_currency
from models.proveedores import Proveedores
from models.ctacteprov import CtaCteProv
from services.ctacteprov import saldo_ctacte
from utils.db import db
from utils.utils import check_session, alertas_mensajes

bp_ctacteprov = Blueprint('ctacteprov', __name__, template_folder='../templates/ctacteprov')

@bp_ctacteprov.route('/addCtaCteProv', methods = ['POST','GET'])
@check_session
def add_cta_cte_prov():
    if request.method == 'POST':
        idproveedor = request.form['idproveedor']
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
            ctacteprov = CtaCteProv(idproveedor, fecha, debe, haber)
            db.session.add(ctacteprov)
            db.session.commit()
            flash('Movimiento de cta cte grabado')
            return redirect(url_for('ctacteprov.lst_cta_cte_prov', id=idproveedor))
        except Exception as e:
            db.session.rollback()
            flash(f'Error grabado ctacte: {e}')
            return redirect(url_for('ctacteprov.lst_cta_cte_prov', id=idproveedor))
    
    if request.method == 'GET':
        return render_template('ctacte-prov.html')

@bp_ctacteprov.route('/lstctacteprov/<id>)')
@check_session
@alertas_mensajes
def lst_cta_cte_prov(id):
    proveedor = Proveedores.query.get_or_404(id)
    movimientos = CtaCteProv.query.filter_by(idproveedor=proveedor.id).all()
    saldo_total = saldo_ctacte(proveedor.id)
    saldoTotal = saldo_total['total_debe'] - saldo_total['total_haber']
    return render_template('lst-ctacteprov.html', movimientos=movimientos, idProveedor=proveedor.id, nomProveedor=proveedor.nombre, saldoTotal=saldoTotal, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)

@bp_ctacteprov.route('/saldosprov', methods=['GET', 'POST'])
@check_session
@alertas_mensajes
def saldosprov():
    if request.method == 'POST':
        # Obtener la fecha del formulario
        fecha_str = request.form['fecha']
        
        # Convertir la fecha a un objeto datetime
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
        
        # Realizar la consulta agregada
        saldos = db.session.query(
            Proveedores.nombre,
            CtaCteProv.idproveedor,
            func.sum(CtaCteProv.debe).label('total_debe'),
            func.sum(CtaCteProv.haber).label('total_haber')
        ).join(
            Proveedores, Proveedores.id == CtaCteProv.idproveedor        
        ).filter(
            CtaCteProv.fecha >= fecha
        ).group_by(
            Proveedores.nombre,
            CtaCteProv.idproveedor
        ).all()

        # Pasar los resultados a la plantilla
        return render_template('saldos-ctacteprov.html', saldos=saldos, desde=fecha_str, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)
    desde = datetime.today().replace(day=1).strftime("%Y-%m-%d")
    return render_template('saldos-ctacteprov.html', desde=desde, alertas=g.alertas, cantidadAlertas=g.cantidadAlertas)
