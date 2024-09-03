from utils.db import db

class AlcIva(db.Model):
    __tablename__ = 'alc_iva'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(100), nullable=False)
    alicuota = db.Column(db.Float, nullable=False)
    articulos = db.relationship('Articulo', back_populates='iva')
    
    def __init__(self, descripcion, alicuota):
        self.descripcion = descripcion
        self.alicuota = alicuota