"""add impuestos e items_imp_c

Crea el catalogo de impuestos y la tabla de items de impuestos por
factura (items_imp_c), en ese orden para respetar las llaves foraneas:

  - items_imp_c.idfactura  -> facturac.id
  - items_imp_c.idimpuesto -> impuestos.id

Ambas operaciones estan guardadas con inspect().has_table, de modo que
re-ejecutar la revision sobre un esquema ya migrado es un no-op seguro.

Revision ID: f3a91c2b7e40
Revises: c2d3df6d5f32
Create Date: 2026-09-23 21:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'f3a91c2b7e40'
down_revision = 'c2d3df6d5f32'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)

    # Orden FK: primero impuestos (padre), despues items_imp_c (hijo).
    if not inspector.has_table('impuestos'):
        op.create_table(
            'impuestos',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('descripcion', sa.String(length=100), nullable=False),
            sa.Column('alicuota', sa.Numeric(20, 6), nullable=False),
            sa.Column('activo', sa.Boolean(), nullable=False,
                      server_default=sa.true()),
            sa.Column('alta', sa.Date(), nullable=False),
            sa.Column('compras_ventas',
                      sa.Enum('compras', 'ventas', 'ambas',
                              name='compras_ventas'),
                      nullable=False),
        )

    if not inspector.has_table('items_imp_c'):
        op.create_table(
            'items_imp_c',
            sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column('idfactura', sa.Integer(), nullable=False),
            sa.Column('idimpuesto', sa.Integer(), nullable=False),
            sa.Column('alicuota', sa.Numeric(20, 6), nullable=False),
            sa.Column('importe', sa.Numeric(20, 6), nullable=False),
            sa.ForeignKeyConstraint(['idfactura'], ['facturac.id']),
            sa.ForeignKeyConstraint(['idimpuesto'], ['impuestos.id']),
        )


def downgrade():
    conn = op.get_bind()
    inspector = inspect(conn)

    # Orden inverso: primero el hijo, despues el padre.
    if inspector.has_table('items_imp_c'):
        op.drop_table('items_imp_c')
    if inspector.has_table('impuestos'):
        op.drop_table('impuestos')
