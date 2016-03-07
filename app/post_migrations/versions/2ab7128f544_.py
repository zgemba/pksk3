"""empty message

Revision ID: 2ab7128f544
Revises: 44ee29fb684
Create Date: 2016-03-05 18:09:49.554022

"""

# revision identifiers, used by Alembic.
revision = '2ab7128f544'
down_revision = '44ee29fb684'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post_image', sa.Column('is_headline', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post_image', 'is_headline')
    ### end Alembic commands ###
