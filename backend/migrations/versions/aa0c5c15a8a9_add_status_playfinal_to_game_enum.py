"""add PLAYFINAL to Game status enum

Revision 09cd18d4b64a was meant to add the status PLAYFINAL but never changed
the column, so starting a final failed on MySQL with
"Data truncated for column 'status'".

Revision ID: aa0c5c15a8a9
Revises: 2c71994ad95b
Create Date: 2026-10-26 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = 'aa0c5c15a8a9'
down_revision = '2c71994ad95b'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('game', 'status',
                    existing_type=mysql.ENUM('WAITING', 'STARTED', 'ROUNDFINISCH', 'GAMEFINISCH'),
                    type_=sa.Enum('WAITING', 'STARTED', 'ROUNDFINISCH', 'PLAYFINAL', 'GAMEFINISCH', name='status'),
                    existing_nullable=True)


def downgrade():
    # games in the final can not keep their status without PLAYFINAL
    op.execute("UPDATE game SET status = 'STARTED' WHERE status = 'PLAYFINAL'")
    op.alter_column('game', 'status',
                    existing_type=sa.Enum('WAITING', 'STARTED', 'ROUNDFINISCH', 'PLAYFINAL', 'GAMEFINISCH', name='status'),
                    type_=mysql.ENUM('WAITING', 'STARTED', 'ROUNDFINISCH', 'GAMEFINISCH'),
                    existing_nullable=True)
