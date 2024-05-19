"""migrate table users to sqlalchemy

Revision ID: b914b760c1fe
Revises: 
Create Date: 2024-05-18 11:24:25.333965

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b914b760c1fe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
       op.create_table('users',
              sa.Column('id', sa.Integer(), nullable=False),
              sa.Column('username', sa.String(length=100), nullable=True),
              sa.Column('password', sa.String(length=50), nullable=True),
              sa.Column('email', sa.String(length=100), nullable=True),
              sa.PrimaryKeyConstraint('id')
       )


def downgrade():
       op.drop_table('users')

# ### end Alembic commands ###
