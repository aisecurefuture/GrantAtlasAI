"""AI narrative columns on score tables

Revision ID: 0003_ai_narratives
Revises: 0002_contracting_v2
Create Date: 2026-07-10 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_ai_narratives"
down_revision = "0002_contracting_v2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("opportunity_scores", sa.Column("ai_narrative", sa.Text(), nullable=True))
    op.add_column("contract_scores", sa.Column("ai_narrative", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("contract_scores", "ai_narrative")
    op.drop_column("opportunity_scores", "ai_narrative")
