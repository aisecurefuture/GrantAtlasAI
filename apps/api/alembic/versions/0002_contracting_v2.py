"""contracting v2 schema

Revision ID: 0002_contracting_v2
Revises: 0001_initial
Create Date: 2026-07-05 00:30:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_contracting_v2"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


capturestatus = postgresql.ENUM("WATCHING", "QUALIFYING", "PURSUING", "PROPOSING", "SUBMITTED", "NO_BID", name="capturestatus", create_type=False)
contractaction = postgresql.ENUM("PURSUE", "TEAM", "WATCH", "NO_BID", name="contractaction", create_type=False)


def upgrade() -> None:
    capturestatus.create(op.get_bind(), checkfirst=True)
    contractaction.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "contract_opportunities",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("notice_id", sa.String(length=160)),
        sa.Column("solicitation_number", sa.String(length=160)),
        sa.Column("department", sa.String(length=255), nullable=False),
        sa.Column("subtier", sa.String(length=255), nullable=False),
        sa.Column("office", sa.String(length=255), nullable=False),
        sa.Column("posted_date", sa.DateTime(timezone=True)),
        sa.Column("response_deadline", sa.DateTime(timezone=True)),
        sa.Column("opportunity_type", sa.String(length=160), nullable=False),
        sa.Column("set_aside", sa.String(length=255)),
        sa.Column("set_aside_code", sa.String(length=80)),
        sa.Column("naics_code", sa.String(length=12)),
        sa.Column("classification_code", sa.String(length=20)),
        sa.Column("place_of_performance", sa.JSON(), nullable=False),
        sa.Column("description_url", sa.String(length=1000)),
        sa.Column("ui_link", sa.String(length=1000)),
        sa.Column("resource_links", sa.JSON(), nullable=False),
        sa.Column("point_of_contact", sa.JSON(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("status", capturestatus, nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "source", "notice_id", name="uq_contract_source_notice"),
    )
    op.create_index("ix_contract_opportunities_tenant_id", "contract_opportunities", ["tenant_id"])
    op.create_index("ix_contract_opportunities_source", "contract_opportunities", ["source"])
    op.create_index("ix_contract_opportunities_response_deadline", "contract_opportunities", ["response_deadline"])
    op.create_index("ix_contract_opportunities_naics_code", "contract_opportunities", ["naics_code"])
    op.create_index("ix_contract_opportunities_classification_code", "contract_opportunities", ["classification_code"])

    op.create_table(
        "contract_scores",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("contract_opportunity_id", sa.String(length=36), sa.ForeignKey("contract_opportunities.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("total_score", sa.Float(), nullable=False),
        sa.Column("naics_fit", sa.Float(), nullable=False),
        sa.Column("psc_fit", sa.Float(), nullable=False),
        sa.Column("past_performance_fit", sa.Float(), nullable=False),
        sa.Column("set_aside_fit", sa.Float(), nullable=False),
        sa.Column("deadline_fit", sa.Float(), nullable=False),
        sa.Column("competition_fit", sa.Float(), nullable=False),
        sa.Column("strategic_value", sa.Float(), nullable=False),
        sa.Column("recommended_action", contractaction, nullable=False),
        sa.Column("reasons", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_contract_scores_tenant_id", "contract_scores", ["tenant_id"])

    op.create_table(
        "past_performance_projects",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_name", sa.String(length=255), nullable=False),
        sa.Column("customer", sa.String(length=255), nullable=False),
        sa.Column("contract_number", sa.String(length=120)),
        sa.Column("naics_codes", sa.JSON(), nullable=False),
        sa.Column("classification_codes", sa.JSON(), nullable=False),
        sa.Column("value", sa.Integer()),
        sa.Column("start_date", sa.DateTime(timezone=True)),
        sa.Column("end_date", sa.DateTime(timezone=True)),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("outcomes", sa.JSON(), nullable=False),
        sa.Column("contact_reference", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_past_performance_projects_tenant_id", "past_performance_projects", ["tenant_id"])

    op.create_table(
        "teaming_partners",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("partner_type", sa.String(length=120), nullable=False),
        sa.Column("uei", sa.String(length=32)),
        sa.Column("capabilities", sa.JSON(), nullable=False),
        sa.Column("naics_codes", sa.JSON(), nullable=False),
        sa.Column("set_aside_statuses", sa.JSON(), nullable=False),
        sa.Column("contact_name", sa.String(length=255)),
        sa.Column("contact_email", sa.String(length=255)),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_teaming_partners_tenant_id", "teaming_partners", ["tenant_id"])

    op.create_table(
        "capture_plans",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("contract_opportunity_id", sa.String(length=36), sa.ForeignKey("contract_opportunities.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("status", capturestatus, nullable=False),
        sa.Column("bid_decision", sa.String(length=80), nullable=False),
        sa.Column("win_themes", sa.JSON(), nullable=False),
        sa.Column("customer_pain_points", sa.JSON(), nullable=False),
        sa.Column("competitor_notes", sa.Text(), nullable=False),
        sa.Column("partner_strategy", sa.Text(), nullable=False),
        sa.Column("compliance_matrix", sa.JSON(), nullable=False),
        sa.Column("color_team_reviews", sa.JSON(), nullable=False),
        sa.Column("tasks", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_capture_plans_tenant_id", "capture_plans", ["tenant_id"])


def downgrade() -> None:
    for table in ["capture_plans", "teaming_partners", "past_performance_projects", "contract_scores", "contract_opportunities"]:
        op.drop_table(table)
    contractaction.drop(op.get_bind(), checkfirst=True)
    capturestatus.drop(op.get_bind(), checkfirst=True)
