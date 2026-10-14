"""add impresion_directa a puntos_venta

Booleano impresion_directa (default false = vista previa) en puntos_venta,
para elegir por punto de venta entre previsualizar el ticket o enviarlo
directo a la impresora por defecto del terminal (kiosk-printing).

La columna se verifica con inspect().get_columns, de modo que
re-ejecutar la revision sobre un esquema ya migrado es un no-op seguro.
MySQL rellena las filas existentes con el
DEFAULT (0), por lo que todos los puntos de venta siguen en vista previa.

Revision ID: 7e4b92c1d5a8
Revises: c2d3df6d5f32
Create Date: 2026-10-13 23:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '7e4b92c1d5a8'
down_revision = 'c2d3df6d5f32'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)

    cols = [c['name'] for c in inspector.get_columns('puntos_venta')]
    if 'impresion_directa' not in cols:
        op.add_column(
            'puntos_venta',
            sa.Column('impresion_directa', sa.Boolean(), nullable=False,
                      server_default=sa.false()),
        )


def downgrade():
    conn = op.get_bind()
    inspector = inspect(conn)

    cols = [c['name'] for c in inspector.get_columns('puntos_venta')]
    if 'impresion_directa' in cols:
        op.drop_column('puntos_venta', 'impresion_directa')
