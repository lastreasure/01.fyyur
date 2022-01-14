"""updating genre for artist

Revision ID: 07542e759c80
Revises: 187e91e663cd
Create Date: 2022-01-14 15:55:20.391675

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07542e759c80'
down_revision = '187e91e663cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    # ### end Alembic commands ###