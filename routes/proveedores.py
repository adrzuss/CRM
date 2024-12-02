from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify, current_app, session
from datetime import date
from models.proveedores import Proveedores, FacturaC, ItemC, PagosFC
from models.articulos import Articulo, Stock
from models.ctacteprov import CtaCteProv
from utils.utils import check_session
from utils.db import db

bp_proveedores = Blueprint('proveedores', __name__, template_folder='../templates/proveedores')

#------------------ proveedores --------------

@bp_proveedores.route('/proveedores')
@check_session
def proveedores():
    proveedores = Proveedores.query.all()
    return render_template('proveedores.html', proveedores=proveedores)

@bp_proveedores.route('/add_proveedor', methods=['POST'])
@check_session
def add_proveedor():
    nombre = request.form['nombre']
    mail = request.form['mail']
    telefono = request.form['telefono']
    documento = request.form['documento']
    proveedores = Proveedores(nombre, mail, telefono, documento)
    db.session.add(proveedores)
    db.session.commit()
    flash('Proveedor agregado')
    return redirect(url_for('proveedores.proveedores'))

@bp_proveedores.route('/proveedor/<id>')
@check_session
def get_proveedor(id):
    proveedor = Proveedores.query.get(id)
    if proveedor:
        return jsonify(success=True, proveedor={"id": proveedor.id, "nombre": proveedor.nombre})
    else:
        return jsonify(success=False)

@bp_proveedores.route('/update_proveedor/<id>', methods=['GET', 'POST'])
@check_session
def update_proveedor(id):
    proveedor = Proveedores.query.get(id)
    if request.method == 'GET':
        return render_template('upd-proveedor.html', proveedor = proveedor)
    if request.method == 'POST':
        proveedor.nombre = request.form['nombre']
        proveedor.email = request.form['mail']
        proveedor.telefono = request.form['telefono']
        proveedor.docuemto = request.form['documento']
        db.session.commit()
        flash('Proveedor grabado')
        return redirect(url_for('proveedores.proveedores'))

@bp_proveedores.route('/delete_proveedor/<id>')
@check_session
def delete_proveedor(id):
    proveedor = Proveedores.query.get(id)
    db.session.delete(proveedor)
    db.session.commit()
    flash('Proveedor eliminado')
    return redirect(url_for('home'))

# ----------------- compras ------------------
@bp_proveedores.route('/compras', methods=['GET', 'POST'])
@check_session
def compras():
    if request.method == 'GET':
        desde = date.today()
        hasta = date.today()
    if request.method == 'POST':
        desde = request.form['desde']
        hasta = request.form['hasta']
    facturas = FacturaC.query.filter(FacturaC.fecha >= desde, FacturaC.fecha <= hasta)
    return render_template('compras.html', facturas=facturas, desde=desde, hasta=hasta)
    
@bp_proveedores.route('/nueva_compra', methods=['GET', 'POST'])
@check_session
def nueva_compra():
    if request.method == 'POST':
        idproveedor = request.form['idproveedor']
        fecha = request.form['fecha']
        total = 0  # Esto se calculará más tarde
        
        efectivo = float(request.form['efectivo'])
        ctacte = float(request.form['ctacte'])

        nueva_factura = FacturaC(idproveedor=idproveedor, fecha=fecha, total=total, idsucursal=session['id_sucursal'])
        db.session.add(nueva_factura)
        db.session.commit()

        idfactura = nueva_factura.id
        
        items = request.form  # Obtener todo el formulario
        item_count = 0  # Contador de items agregados

        item_count = len([key for key in items.keys() if key.startswith('items') and key.endswith('[idarticulo]')])
        idstock = current_app.config['IDSTOCK']

        for i in range(item_count):
            idarticulo = request.form[f'items[{i}][idarticulo]']
            cantidad = int(request.form[f'items[{i}][cantidad]'])
            costo = float(request.form[f'items[{i}][articulo_precio]'])
            articulo = Articulo.query.get(idarticulo)
            articulo.costo = costo
            precio_unitario = costo
            precio_total = precio_unitario * cantidad

            nuevo_item = ItemC(idfactura=idfactura, id=i, idarticulo=idarticulo, cantidad=cantidad, precio_unitario=precio_unitario, precio_total=precio_total)
            db.session.add(nuevo_item)
            total += precio_total
             # Actualizar la tabla de stocks
            stock = Stock.query.filter_by(idstock=idstock, idarticulo=idarticulo).first()
            if stock:
                stock.actual += cantidad
                if stock.actual < 0:
                    stock.actual = 0  # Para evitar cantidades negativas
            else:
                stock = Stock(idstock=idstock, idarticulo=idarticulo, actual=+cantidad, maximo=0, deseable=0)
                db.session.add(stock)
        
        nueva_factura = FacturaC.query.get(idfactura)
        nueva_factura.total = total
        
        if efectivo > 0:
            pagosfc = PagosFC(idfactura, 1, 0, efectivo)
            db.session.add(pagosfc)
            db.session.commit()
               
            
        if ctacte > 0:
            pagosfc = PagosFC(idfactura, 3, 0, ctacte)
            db.session.add(pagosfc)
            db.session.commit()
            
            debe = ctacte
            haber = 0
            try:
                ctacteprov = CtaCteProv(idproveedor, fecha, debe, haber)
                db.session.add(ctacteprov)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(f'Error grabado entidad crediticia: {e}')
        
        db.session.commit()
        flash('Factura grabada')
        return redirect(url_for('index'))

    hoy = date.today()
    return render_template('nueva_compra.html', hoy=hoy)

@bp_proveedores.route('/nuevo_gasto', methods=['GET', 'POST'])
@check_session
def nuevo_gasto():
    if request.method == 'POST':
        idproveedor = request.form['idproveedor']
        fecha = request.form['fecha']
        gasto = float(request.form['total'])

        nueva_gasto = FacturaC(idproveedor=idproveedor, fecha=fecha, total=gasto, idsucursal=session['id_sucursal'])
        db.session.add(nueva_gasto)
        db.session.commit()

        idfactura = nueva_gasto.id
        flash('Gasto grabado')
        return redirect(url_for('index'))
    else:
        return render_template('nuevo_gasto.html')
        
        