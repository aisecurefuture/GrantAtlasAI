"""Tenant onboarding_dismissed flag

Revision ID: 0005_onboarding
Revises: 0004_tenant_lifecycle
Create Date: 2026-07-13 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0005_onboarding"
down_revision = "0004_tenant_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("onboarding_dismissed", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("tenants", "onboarding_dismissed")
