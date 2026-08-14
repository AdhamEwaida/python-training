"""Add user table for portal authentication.

Revision ID: 6c81d9aa02ef
Revises: 15d4d7d0bbfb
Create Date: 2026-08-14
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "6c81d9aa02ef"
down_revision = "15d4d7d0bbfb"
branch_labels = None
depends_on = None


def upgrade():
    """Create the table used by Flask-Login accounts."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )


def downgrade():
    """Remove the authentication table."""
    op.drop_table("users")
