"""Tenant is_active flag for deactivation lifecycle

Revision ID: 0004_tenant_lifecycle
Revises: 0003_ai_narratives
Create Date: 2026-07-10 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_tenant_lifecycle"
down_revision = "0003_ai_narratives"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade() -> None:
    op.drop_column("tenants", "is_active")
