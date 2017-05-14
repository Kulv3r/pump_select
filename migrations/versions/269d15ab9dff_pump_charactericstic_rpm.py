"""pump charactericstic RPM

Revision ID: 269d15ab9dff
Revises: 2feefdf01979
Create Date: 2017-05-14 16:25:21.466462

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '269d15ab9dff'
down_revision = '2feefdf01979'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pump_characteristic', sa.Column('rpm', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pump_characteristic', 'rpm')
    # ### end Alembic commands ###