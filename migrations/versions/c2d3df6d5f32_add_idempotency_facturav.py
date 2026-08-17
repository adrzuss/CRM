"""add_idempotency_facturav

Agrega soporte de idempotencia a facturav (columna idempotency_key + indices
unicos) para prevenir duplicados de comprobantes.

Contexto: el SQL manual (SQL/migration_idempotencia.sql) ya fue aplicado en
produccion por el DBA. Esta revision usa DDL de existencia-verificada, de modo
que aplicarla sobre un esquema ya migrado manualmente es un no-op seguro
(no duplica objetos ni falla). Si existen correlativos duplicados historicos,
idx_uq_comprobante se difiere con un warning y se crea en una revision
posterior tras la limpieza de datos.

Revision ID: c2d3df6d5f32
Revises: 806cfc3bfdf2
Create Date: 2026-08-17 17:30:21.376145

"""
from alembic import op
from sqlalchemy import inspect, text

# revision identifiers, used by Alembic.
revision = 'c2d3df6d5f32'
down_revision = '806cfc3bfdf2'
branch_labels = None
depends_on = None


def _columna(conn, nombre):
    """Devuelve True si la columna existe en facturav."""
    return nombre in [c['name'] for c in inspect(conn).get_columns('facturav')]


def _indice(conn, nombre):
    """Devuelve True si el indice existe en facturav."""
    return nombre in [i['name'] for i in inspect(conn).get_indexes('facturav')]


def upgrade():
    conn = op.get_bind()
    # Fase 1: columna idempotency_key (nullable = backward compatibility)
    if not _columna(conn, 'idempotency_key'):
        op.execute('ALTER TABLE facturav ADD COLUMN idempotency_key VARCHAR(36) NULL')
    # Fase 2: UNIQUE INDEX para deteccion de duplicados via idempotency_key
    if not _indice(conn, 'idx_uq_idempotency'):
        op.execute('CREATE UNIQUE INDEX idx_uq_idempotency ON facturav(idempotency_key)')
    # Fase 3: UNIQUE INDEX compuesto para evitar correlativos duplicados
    if not _indice(conn, 'idx_uq_comprobante'):
        dups = conn.execute(text(
            "SELECT punto_vta, nro_comprobante, idtipocomprobante, COUNT(*) "
            "FROM facturav GROUP BY 1,2,3 HAVING COUNT(*) > 1")).fetchall()
        if dups:
            print(f"[migracion] {len(dups)} correlativos duplicados; "
                  f"idx_uq_comprobante diferido. Muestra: {dups[:5]}")
        else:
            op.execute('CREATE UNIQUE INDEX idx_uq_comprobante '
                       'ON facturav(punto_vta, nro_comprobante, idtipocomprobante)')


def downgrade():
    conn = op.get_bind()
    if _indice(conn, 'idx_uq_comprobante'):
        op.execute('DROP INDEX idx_uq_comprobante ON facturav')
    if _indice(conn, 'idx_uq_idempotency'):
        op.execute('DROP INDEX idx_uq_idempotency ON facturav')
    if _columna(conn, 'idempotency_key'):
        op.execute('ALTER TABLE facturav DROP COLUMN idempotency_key')