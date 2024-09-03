from flask import Blueprint, render_template, request, redirect, flash, url_for
from models.entidades_cred import EntidadesCred
from utils.db import db

bp_entidades = Blueprint('entidades', __name__, template_folder='../templates/entidades')

@bp_entidades.route('/entidades')
def entidades():
    entidades = EntidadesCred.query.all()
    print(entidades)
    return render_template('entidades-cred.html', entidades=entidades)

@bp_entidades.route('/add_entidad', methods = ['POST','GET'])
def add_entidad():
    if request.method == 'POST':
        entidad = request.form['entidad']
        telefono = request.form['telefono']
        try:
            entidad = EntidadesCred(entidad, telefono)
            db.session.add(entidad)
            db.session.commit()
            flash('Entidad crediticia grabada')
            return redirect(url_for('entidades.entidades'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error grabado entidad crediticia: {e}')
            return redirect(url_for('entidades.entidades'))
    
    if request.method == 'GET':
        return render_template('entidades-cred.html')
    
@bp_entidades.route('/update_entidad/<id>')
def update_entidad(id):
    pass

