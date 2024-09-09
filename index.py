from flask import render_template, session
from app import create_app
from routes.ventas import get_vta_hoy, get_vta_semana, ventas_por_mes, pagos_hoy
from routes.ctactecli import get_saldo_clientes
from routes.ctacteprov import get_saldo_proveedores
from utils.db import db

app = create_app()

with app.app_context():
    db.init_app(app)
    db.create_all()   
    

@app.route('/')
def index():
    vta_hoy = get_vta_hoy()
    vta_semana = get_vta_semana()
    vta_6_meses = ventas_por_mes()
    saldo_clientes = get_saldo_clientes()
    saldo_proveedores = get_saldo_proveedores()
    pagosHoy = pagos_hoy()
    print(vta_6_meses)
    print(vta_6_meses['meses'])
    return render_template('tablero.html', vta_hoy=vta_hoy, vta_semana=vta_semana, saldo_clientes=saldo_clientes, saldo_proveedores=saldo_proveedores, meses=vta_6_meses['meses'], operaciones=vta_6_meses['operaciones'], tipoPagoss=pagosHoy['tipo_pago'], cantPagoss=pagosHoy['total_pago'])

if __name__ == "__main__":
    app.run(debug=True)