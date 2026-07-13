from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import CapturePlan, CaptureStatus, ContractOpportunity, LibraryItem, Opportunity, OrganizationProfile, PastPerformanceProject, Role, TeamingPartner, Tenant, User
from app.services.billing import subscription_limit_for_plan


FOCUS_AREAS = [
    "AI safety education",
    "Cybersecurity education",
    "AI literacy",
    "Workforce development",
    "Open-source public benefit tools",
    "Community AI safety",
    "Small business cybersecurity",
    "Nonprofit cybersecurity",
    "Student mentorship",
    "Veteran technology training",
    "Teacher AI literacy",
    "Responsible AI adoption",
]


def run() -> None:
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.slug == "gratitech").first()
        if not tenant:
            tenant = Tenant(
                name="Gratitech Research & Charitable Endeavor Corp.",
                slug="gratitech",
                plan="Free Trial",
                subscription_status="trialing",
                trial_end=datetime.now(timezone.utc) + timedelta(days=14),
                usage_limits=subscription_limit_for_plan("Free Trial"),
            )
            db.add(tenant)
            db.flush()

        if not db.query(User).filter(User.tenant_id == tenant.id, User.email == settings.bootstrap_admin_email.lower()).first():
            db.add(
                User(
                    tenant_id=tenant.id,
                    email=settings.bootstrap_admin_email.lower(),
                    name="Gratitech Owner",
                    password_hash=hash_password(settings.bootstrap_admin_password),
                    role=Role.OWNER,
                    is_super_admin=True,
                )
            )

        if not db.query(OrganizationProfile).filter(OrganizationProfile.tenant_id == tenant.id).first():
            db.add(
                OrganizationProfile(
                    tenant_id=tenant.id,
                    organization_name=tenant.name,
                    nonprofit_status="501(c)(3) planned/active validation required",
                    mission="Advance public-benefit AI literacy, cybersecurity education, and responsible technology adoption.",
                    vision="Communities, educators, nonprofits, veterans, and small businesses can use emerging technology safely and confidently.",
                    programs=[
                        {"name": "Community AI Safety", "summary": "Workshops and open tools for responsible AI adoption."},
                        {"name": "Cybersecurity Education", "summary": "Practical cyber hygiene training for nonprofits and small businesses."},
                        {"name": "Workforce Mentorship", "summary": "Student and veteran pathways into trustworthy technology careers."},
                    ],
                    focus_areas=FOCUS_AREAS,
                    geographic_service_area="United States, with remote-first training and community partnerships.",
                    target_populations=["nonprofits", "teachers", "students", "veterans", "small businesses"],
                    past_performance="Open-source tooling, educational program design, AI safety research, and cybersecurity enablement.",
                )
            )

        if not db.query(Opportunity).filter(Opportunity.tenant_id == tenant.id).first():
            db.add(
                Opportunity(
                    tenant_id=tenant.id,
                    title="Community Technology Education Capacity Grant",
                    agency="Manual Seed Funder",
                    source="Manual",
                    source_url=None,  # manual entries have no external listing
                    opportunity_number="SEED-TECH-001",
                    posted_date=datetime.now(timezone.utc),
                    close_date=datetime.now(timezone.utc) + timedelta(days=35),
                    award_floor=50000,
                    award_ceiling=250000,
                    expected_awards=8,
                    eligibility="Eligible applicants include nonprofit organizations and education institutions.",
                    description="Supports nonprofit cybersecurity education, AI literacy, student mentorship, and workforce development.",
                    categories=["Education", "Cybersecurity", "AI literacy"],
                    keywords=["nonprofit", "cybersecurity", "AI literacy", "workforce"],
                )
            )

        if not db.query(PastPerformanceProject).filter(PastPerformanceProject.tenant_id == tenant.id).first():
            db.add(
                PastPerformanceProject(
                    tenant_id=tenant.id,
                    project_name="Responsible Technology Training Pilot",
                    customer="Community education coalition",
                    contract_number="PAST-EDU-001",
                    naics_codes=["611430", "541519"],
                    classification_codes=["U008", "D399"],
                    value=125000,
                    start_date=datetime.now(timezone.utc) - timedelta(days=420),
                    end_date=datetime.now(timezone.utc) - timedelta(days=90),
                    summary="Designed and delivered AI literacy and cybersecurity training for educators, nonprofits, and small businesses.",
                    outcomes=["Trained 250 participants", "Published reusable open-source safety materials", "Improved cyber hygiene practices"],
                )
            )

        if not db.query(TeamingPartner).filter(TeamingPartner.tenant_id == tenant.id).first():
            db.add(
                TeamingPartner(
                    tenant_id=tenant.id,
                    name="Veteran Cyber Workforce Alliance",
                    partner_type="Teaming partner",
                    capabilities=["veteran training", "cybersecurity instructors", "workforce placement"],
                    naics_codes=["611430", "541519"],
                    set_aside_statuses=["Service-Disabled Veteran-Owned Small Business", "Small Business"],
                    contact_name="Partner Lead",
                    contact_email="partners@example.org",
                    notes="Potential partner for workforce and cybersecurity training solicitations.",
                )
            )

        contract = db.query(ContractOpportunity).filter(ContractOpportunity.tenant_id == tenant.id).first()
        if not contract:
            contract = ContractOpportunity(
                tenant_id=tenant.id,
                title="Cybersecurity and AI Literacy Training Support",
                source="Manual",
                notice_id="SEED-SAM-001",
                solicitation_number="FAKE-TRAINING-001",
                department="Department of Education",
                subtier="Office of Career, Technical, and Adult Education",
                office="Program Support Office",
                posted_date=datetime.now(timezone.utc),
                response_deadline=datetime.now(timezone.utc) + timedelta(days=28),
                opportunity_type="Sources Sought",
                set_aside="Small Business",
                set_aside_code="SBA",
                naics_code="611430",
                classification_code="U008",
                place_of_performance={"country": "United States"},
                ui_link="https://sam.gov/",
                resource_links=[],
                point_of_contact=[{"email": "contracting@example.gov"}],
                raw_payload={"seed": True},
            )
            db.add(contract)
            db.flush()

        if not db.query(CapturePlan).filter(CapturePlan.tenant_id == tenant.id, CapturePlan.contract_opportunity_id == contract.id).first():
            db.add(
                CapturePlan(
                    tenant_id=tenant.id,
                    contract_opportunity_id=contract.id,
                    status=CaptureStatus.QUALIFYING,
                    bid_decision="Undecided",
                    win_themes=["Responsible AI literacy", "Cybersecurity education", "Veteran workforce pathway"],
                    customer_pain_points=["Need practical training", "Need safe AI adoption guardrails", "Need measurable workforce outcomes"],
                    partner_strategy="Validate small-business eligibility and consider teaming with Veteran Cyber Workforce Alliance.",
                    compliance_matrix=[
                        {"requirement": "Training capability", "owner": "Grant Writer", "status": "Mapped"},
                        {"requirement": "Past performance", "owner": "Owner", "status": "Draft"},
                    ],
                    color_team_reviews=[
                        {"name": "Pink Team", "due": "T-14 days", "status": "Planned"},
                        {"name": "Red Team", "due": "T-5 days", "status": "Planned"},
                    ],
                    tasks=[
                        {"title": "Confirm set-aside eligibility", "status": "To do"},
                        {"title": "Draft capability statement", "status": "Drafting"},
                    ],
                )
            )

        existing_titles = {item.title for item in db.query(LibraryItem).filter(LibraryItem.tenant_id == tenant.id).all()}
        for title, category, body in [
            ("Mission Statement", "Mission statement", "Advance public-benefit AI literacy, cybersecurity education, and responsible technology adoption."),
            ("Organizational History", "Organizational history", "Gratitech develops education programs and open-source public benefit tools for safer technology adoption."),
            ("Cybersecurity Capability Statement", "Capability statement", "Training, assessment, and enablement for nonprofit and small business cybersecurity resilience."),
            ("AI Literacy Program", "Program descriptions", "Practical workshops that help teachers, students, and nonprofit teams use AI responsibly."),
            ("Evaluation Plan", "Evaluation plan", "Measure learning gains, adoption outcomes, participant satisfaction, and follow-on community impact."),
            ("Sustainability Plan", "Sustainability plan", "Blend earned training revenue, philanthropic grants, partnerships, and reusable open-source assets."),
        ]:
            if title not in existing_titles:
                db.add(LibraryItem(tenant_id=tenant.id, title=title, category=category, body=body, tags=FOCUS_AREAS[:4]))

        db.flush()

        # Score any seeded records that don't have scores yet, so demo data
        # shows the explainable fit scoring out of the box.
        from app.models import ContractScore, OpportunityScore
        from app.services.ingestion import store_contract_score, store_opportunity_score

        for opportunity in db.query(Opportunity).filter(Opportunity.tenant_id == tenant.id).all():
            if not db.query(OpportunityScore).filter(OpportunityScore.opportunity_id == opportunity.id).first():
                store_opportunity_score(db, tenant.id, opportunity)
        for contract_row in db.query(ContractOpportunity).filter(ContractOpportunity.tenant_id == tenant.id).all():
            if not db.query(ContractScore).filter(ContractScore.contract_opportunity_id == contract_row.id).first():
                store_contract_score(db, tenant.id, contract_row)

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()
