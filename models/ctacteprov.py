from utils.db import db


class CtaCteProv(db.Model):
    __tablename__ = 'cta_cte_prov'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idproveedor = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    fecha = db.Column(db.Date, nullable = False)
    debe = db.Column(db.Numeric(20,6), nullable = False)
    haber = db.Column(db.Numeric(20,6), nullable = False)
    idfactura = db.Column(db.Integer, db.ForeignKey('facturac.id'), nullable=False)
    
    def __init__(self, idproveedor, idfactura, fecha, debe, haber):
        self.idproveedor = idproveedor
        self.idfactura = idfactura
        self.fecha = fecha
        self.debe = debe
        self.haber = haber