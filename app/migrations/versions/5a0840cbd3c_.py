"""empty message

Revision ID: 5a0840cbd3c
Revises: b1f665d4b0
Create Date: 2015-09-28 22:41:05.726189

"""

# revision identifiers, used by Alembic.
revision = '5a0840cbd3c'
down_revision = 'b1f665d4b0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('mail_notify', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'mail_notify')
    ### end Alembic commands ###
