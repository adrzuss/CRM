from utils.db import db

class CtaCteCli(db.Model):
    __tablename__ = 'cta_cte_cli'
    id = db.Column(db.Integer, primary_key=True)
    idcliente = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    fecha = db.Column(db.Date, nullable = False)
    debe = db.Column(db.Numeric(20,6), default=0.0)
    haber = db.Column(db.Numeric(20,6), default=0.0)
    
    def __init__(self, idCliente, fecha, debe = 0, haber = 0):
        self.idcliente = idCliente
        self.fecha = fecha
        self.debe = debe
        self.haber = haber