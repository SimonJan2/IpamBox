"""circuits.is_retired — split legacy sheets (קוי בזק ישן) from live circuits

Revision ID: 0012_circuit_retired
Revises: 0011_import_entities
Create Date: 2026-10-10
"""
from alembic import op
import sqlalchemy as sa

revision = "0012_circuit_retired"
down_revision = "0011_import_entities"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "circuits",
        sa.Column(
            "is_retired",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
    op.create_index("ix_circuits_is_retired", "circuits", ["is_retired"])


def downgrade() -> None:
    op.drop_index("ix_circuits_is_retired", table_name="circuits")
    op.drop_column("circuits", "is_retired")
