"""initial grantatlas schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-04 20:40:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


role = sa.Enum("OWNER", "ADMIN", "GRANT_WRITER", "REVIEWER", "VIEWER", name="role")
opportunitystatus = sa.Enum("NEW", "MONITORING", "APPLIED", "SKIPPED", "REQUIRES_PARTNER", name="opportunitystatus")
recommendedaction = sa.Enum("APPLY", "PARTNER", "MONITOR", "SKIP", name="recommendedaction")


def upgrade() -> None:
    role.create(op.get_bind(), checkfirst=True)
    opportunitystatus.create(op.get_bind(), checkfirst=True)
    recommendedaction.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "tenants",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False, unique=True),
        sa.Column("plan", sa.String(length=80), nullable=False),
        sa.Column("subscription_status", sa.String(length=80), nullable=False),
        sa.Column("trial_end", sa.DateTime(timezone=True)),
        sa.Column("stripe_customer_id", sa.String(length=255)),
        sa.Column("stripe_subscription_id", sa.String(length=255)),
        sa.Column("usage_limits", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_super_admin", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table(
        "organization_profiles",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("organization_name", sa.String(length=255), nullable=False),
        sa.Column("ein", sa.String(length=32)),
        sa.Column("uei", sa.String(length=32)),
        sa.Column("sam_status", sa.String(length=120)),
        sa.Column("grants_gov_status", sa.String(length=120)),
        sa.Column("nonprofit_status", sa.String(length=120)),
        sa.Column("mission", sa.Text(), nullable=False),
        sa.Column("vision", sa.Text(), nullable=False),
        sa.Column("programs", sa.JSON(), nullable=False),
        sa.Column("focus_areas", sa.JSON(), nullable=False),
        sa.Column("geographic_service_area", sa.Text(), nullable=False),
        sa.Column("target_populations", sa.JSON(), nullable=False),
        sa.Column("past_performance", sa.Text(), nullable=False),
        sa.Column("key_staff_bios", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "opportunities",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("agency", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("source_url", sa.String(length=1000)),
        sa.Column("opportunity_number", sa.String(length=160)),
        sa.Column("assistance_listing", sa.String(length=120)),
        sa.Column("posted_date", sa.DateTime(timezone=True)),
        sa.Column("close_date", sa.DateTime(timezone=True)),
        sa.Column("award_floor", sa.Integer()),
        sa.Column("award_ceiling", sa.Integer()),
        sa.Column("expected_awards", sa.Integer()),
        sa.Column("eligibility", sa.Text(), nullable=False),
        sa.Column("cost_share_required", sa.Boolean(), nullable=False),
        sa.Column("required_partners", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("categories", sa.JSON(), nullable=False),
        sa.Column("keywords", sa.JSON(), nullable=False),
        sa.Column("attachments", sa.JSON(), nullable=False),
        sa.Column("contact_info", sa.JSON(), nullable=False),
        sa.Column("status", opportunitystatus, nullable=False),
        sa.Column("assigned_owner_id", sa.String(length=36), sa.ForeignKey("users.id")),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "source", "opportunity_number", name="uq_opportunity_source_number"),
    )
    op.create_index("ix_opportunities_tenant_id", "opportunities", ["tenant_id"])
    op.create_index("ix_opportunities_source", "opportunities", ["source"])
    op.create_index("ix_opportunities_close_date", "opportunities", ["close_date"])
    op.create_table(
        "opportunity_scores",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("opportunity_id", sa.String(length=36), sa.ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("total_score", sa.Float(), nullable=False),
        sa.Column("mission_fit", sa.Float(), nullable=False),
        sa.Column("eligibility_fit", sa.Float(), nullable=False),
        sa.Column("deadline_urgency", sa.Float(), nullable=False),
        sa.Column("funding_size", sa.Float(), nullable=False),
        sa.Column("proposal_complexity", sa.Float(), nullable=False),
        sa.Column("partnership_fit", sa.Float(), nullable=False),
        sa.Column("past_performance_fit", sa.Float(), nullable=False),
        sa.Column("strategic_value", sa.Float(), nullable=False),
        sa.Column("probability_of_success", sa.Float(), nullable=False),
        sa.Column("recommended_action", recommendedaction, nullable=False),
        sa.Column("reasons", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_opportunity_scores_tenant_id", "opportunity_scores", ["tenant_id"])
    op.create_table(
        "proposal_workspaces",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("opportunity_id", sa.String(length=36), sa.ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("outline", sa.JSON(), nullable=False),
        sa.Column("compliance_matrix", sa.JSON(), nullable=False),
        sa.Column("required_attachments", sa.JSON(), nullable=False),
        sa.Column("tasks", sa.JSON(), nullable=False),
        sa.Column("budget", sa.JSON(), nullable=False),
        sa.Column("narrative_sections", sa.JSON(), nullable=False),
        sa.Column("internal_notes", sa.Text(), nullable=False),
        sa.Column("reviewer_comments", sa.JSON(), nullable=False),
        sa.Column("version_history", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_proposal_workspaces_tenant_id", "proposal_workspaces", ["tenant_id"])
    op.create_table(
        "library_items",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_library_items_tenant_id", "library_items", ["tenant_id"])
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), sa.ForeignKey("tenants.id", ondelete="SET NULL")),
        sa.Column("actor_user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("action", sa.String(length=160), nullable=False),
        sa.Column("target_type", sa.String(length=120), nullable=False),
        sa.Column("target_id", sa.String(length=36)),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_logs_tenant_id", "audit_logs", ["tenant_id"])


def downgrade() -> None:
    for table in [
        "audit_logs",
        "library_items",
        "proposal_workspaces",
        "opportunity_scores",
        "opportunities",
        "organization_profiles",
        "users",
        "tenants",
    ]:
        op.drop_table(table)
    recommendedaction.drop(op.get_bind(), checkfirst=True)
    opportunitystatus.drop(op.get_bind(), checkfirst=True)
    role.drop(op.get_bind(), checkfirst=True)

