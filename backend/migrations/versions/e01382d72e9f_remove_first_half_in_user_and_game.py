"""remove first half in user and game

Revision ID: e01382d72e9f
Revises: e5e9f270e0b5
Create Date: 2020-05-17 15:25:00.828362

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e01382d72e9f'
down_revision = 'e5e9f270e0b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('game', 'firsthalf')
    op.drop_column('user', 'firsthalf')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('firsthalf', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('game', sa.Column('firsthalf', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    # ### end Alembic commands ###