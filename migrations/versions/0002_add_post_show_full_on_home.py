"""Add the homepage full-post display option.

Revision ID: 0002_add_post_show_full_on_home
Revises: 0001_initial
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_add_post_show_full_on_home"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "posts",
        sa.Column("show_full_on_home", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade():
    op.drop_column("posts", "show_full_on_home")
