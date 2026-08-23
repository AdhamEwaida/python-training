"""Add roles and profile-picture filenames.

Revision ID: 81c4d26fa902
Revises: 72f89a3bc210
Create Date: 2026-08-23
"""

from alembic import op
import sqlalchemy as sa

revision = "81c4d26fa902"
down_revision = "72f89a3bc210"
branch_labels = None
depends_on = None


def upgrade():
    """Add role and generated media filename columns."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column(
                "role",
                sa.String(length=20),
                nullable=False,
                server_default="student",
            )
        )
        batch_op.add_column(
            sa.Column("profile_picture", sa.String(length=255), nullable=True)
        )
    with op.batch_alter_table("students") as batch_op:
        batch_op.add_column(
            sa.Column("profile_picture", sa.String(length=255), nullable=True)
        )


def downgrade():
    """Remove role and generated media filename columns."""
    with op.batch_alter_table("students") as batch_op:
        batch_op.drop_column("profile_picture")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("profile_picture")
        batch_op.drop_column("role")
