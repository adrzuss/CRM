from utils.db import db
from index import app

with app.app_context():
    # Check if table exists
    result = db.session.execute(db.text("SHOW TABLES LIKE 'reglas_redondeo'"))
    exists = list(result)
    if exists:
        print("Table reglas_redondeo already exists")
    else:
        print("Creating table reglas_redondeo...")
        db.session.execute(db.text("""
            CREATE TABLE reglas_redondeo (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(50) NOT NULL,
                desde_precio DECIMAL(12,2) NOT NULL,
                hasta_precio DECIMAL(12,2) NOT NULL,
                multiplo INT NOT NULL,
                tipo_redondeo ENUM('arriba', 'abajo', 'cercano') DEFAULT 'cercano',
                restar_unidades INT DEFAULT 0,
                activo BOOLEAN DEFAULT TRUE
            )
        """))
        db.session.commit()
        print("Table reglas_redondeo created successfully")
