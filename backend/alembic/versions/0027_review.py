"""review dismissals — the V7.1 review queue's only persisted state

Sections are computed queries; this table records "ignore this exact
finding" decisions so they survive re-flags and stay auditable
(AUDITED_MODELS) and restorable (BACKUP_TABLES). Unique on
(kind, entity_type, entity_id, fingerprint) — the fingerprint carries
the stable identity of the ignored thing (MAC pair, switch/port text).

Revision ID: 0027_review
Revises: 0026_monitoring
Create Date: 2026-09-25
"""
import sqlalchemy as sa
from alembic import op

revision = "0027_review"
down_revision = "0026_monitoring"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "review_dismissals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column(
            "fingerprint", sa.String(255), server_default="", nullable=False
        ),
        sa.Column(
            "actor", sa.String(255), server_default="system", nullable=False
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "kind",
            "entity_type",
            "entity_id",
            "fingerprint",
            name="uq_review_dismissals_key",
        ),
    )
    op.create_index(
        "ix_review_dismissals_kind", "review_dismissals", ["kind"]
    )


def downgrade() -> None:
    op.drop_table("review_dismissals")
