"""Add explicit many-to-many course enrollments.

Revision ID: 72f89a3bc210
Revises: 6c81d9aa02ef
Create Date: 2026-08-23
"""

from alembic import op
import sqlalchemy as sa

revision = "72f89a3bc210"
down_revision = "6c81d9aa02ef"
branch_labels = None
depends_on = None


def upgrade():
    """Create the enrollment association table."""
    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["students.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "student_id",
            "course_id",
            name="uq_enrollment_student_course",
        ),
    )


def downgrade():
    """Remove explicit course enrollments."""
    op.drop_table("enrollments")
