from utils.db import db


class CtaCteProv(db.Model):
    __tablename__ = 'cta_cte_prov'
    id = db.Column(db.Integer, primary_key=True)
    idproveedor = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    fecha = db.Column(db.Date, nullable = False)
    debe = db.Column(db.Numeric(20,6), nullable = False)
    haber = db.Column(db.Numeric(20,6), nullable = False)
    
    def __init__(self, idproveedor, fecha, debe = 0, haber = 0):
        self.idproveedor = idproveedor
        self.fecha = fecha
        self.debe = debe
        self.haber = haber