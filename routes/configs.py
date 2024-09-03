from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify
from models.configs import AlcIva
from models.articulos import ListasPrecios
from utils.db import db

bp_configuraciones = Blueprint('configuraciones', __name__, template_folder='../templates/configuracion')

@bp_configuraciones.route('/configuraciones')
def configuraciones():
    alcIva = AlcIva.query.all()
    listas_precios = ListasPrecios.query.all()
    return render_template('configuraciones.html', alicuotas=alcIva, listas_precios=listas_precios)

"""
@bp_configuraciones.route('/alc_iva')
def alc_iva():
    alcIva = AlcIva.query.all()
    return render_template('alicuotas-iva.html', alicuotas=alcIva)
"""    

@bp_configuraciones.route('/add_alc_iva', methods=['POST'])
def add_alc_iva():
    descripcion = request.form['descripcion']
    alicuota = request.form['alicuota']
    alciva = AlcIva(descripcion, alicuota)
    db.session.add(alciva)
    db.session.commit()
    flash('Alicuota de IVA grabada')
    return redirect('configuraciones')

@bp_configuraciones.route('/add_lista_precio', methods=['POST'])
def add_lista_precio():
    try:
        nombre_lista_precio = request.form['lista_precio']
        markup = request.form['markup']
        print(markup)
        lista_precio = ListasPrecios(nombre_lista_precio, markup)
        db.session.add(lista_precio)
        db.session.commit()
        flash('Lista de precios grabada')
        return redirect('configuraciones')
    except Exception as e:
        flash(f'Error grabando lista de precios: {e}', 'error')
        return redirect('configuraciones')    