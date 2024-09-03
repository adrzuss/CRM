from flask import Blueprint, render_template, request, redirect, flash, url_for
from sqlalchemy import func
from utils.utils import format_currency
from models.proveedores import Proveedores
from models.ctacteprov import CtaCteProv
from utils.db import db

bp_ctacteprov = Blueprint('ctacteprov', __name__)

@bp_ctacteprov.route('/addCtaCte', methods = ['POST','GET'])
def add_cta_cte():
    if request.method == 'POST':
        idproveedor = request.form['idproveedor']
        fecha = request.form['fecha']
        debe = request.form['debe']
        haber = request.form['haber']
        try:
            ctacteprov = CtaCteProv(idproveedor, fecha, debe, haber)
            db.session.add(ctacteprov)
            db.session.commit()
            flash('Movimiento de cta cte grabado')
            return redirect(url_for('proveedores.home'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error grabado ctacte: {e}')
            return redirect(url_for('ctactecli.add_cta_cte'))
    
    if request.method == 'GET':
        return render_template('ctacte-prov.html')

@bp_ctacteprov.route('/lstctacte/<id>)')
def lst_cta_cte(id):
    proveedor = Proveedores.query.get_or_404(id)
    movimientos = CtaCteProv.query.filter_by(idProveedor=proveedor.id).all()
    return render_template('lst-ctacteprov.html', movimientos=movimientos)

def get_saldo_proveedores():
    try:
        saldos_cta_cte = db.session.query(func.sum(CtaCteProv.debe).label('debe'), func.sum(CtaCteProv.haber).label('haber')).all()
        saldos = format_currency(saldos_cta_cte[0][0] - saldos_cta_cte[0][1])
        return saldos
    except: 
        return format_currency(0.0)