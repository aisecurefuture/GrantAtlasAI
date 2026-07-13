from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import LibraryItem, Opportunity, OrganizationProfile, ProposalWorkspace, Tenant, User
from app.schemas import OnboardingStatusOut, OnboardingStepOut

router = APIRouter()


@router.get("/status", response_model=OnboardingStatusOut)
def onboarding_status(user: User = Depends(current_user), db: Session = Depends(get_db)) -> OnboardingStatusOut:
    tenant = db.get(Tenant, user.tenant_id)
    profile = db.query(OrganizationProfile).filter(OrganizationProfile.tenant_id == user.tenant_id).first()
    opp_count = db.query(Opportunity).filter(Opportunity.tenant_id == user.tenant_id).count()
    lib_count = db.query(LibraryItem).filter(LibraryItem.tenant_id == user.tenant_id).count()
    prop_count = db.query(ProposalWorkspace).filter(ProposalWorkspace.tenant_id == user.tenant_id).count()
    team_count = db.query(User).filter(User.tenant_id == user.tenant_id).count()

    profile_done = bool(profile and profile.mission and profile.focus_areas and profile.past_performance)

    steps = [
        OnboardingStepOut(
            key="profile",
            title="Complete your organization profile",
            description="Your mission, focus areas, and past performance power every fit score and AI draft.",
            done=profile_done,
            cta_label="Edit profile",
            cta_href="/organization",
        ),
        OnboardingStepOut(
            key="opportunities",
            title="Import your first opportunities",
            description="Pull live grants from Grants.gov, automatically scored against your profile.",
            done=opp_count > 0,
            cta_label="Import grants",
            cta_href="/dashboard",
        ),
        OnboardingStepOut(
            key="library",
            title="Add reusable content",
            description="Save your boilerplate so the AI can draft proposals in your own approved language.",
            done=lib_count > 0,
            cta_label="Open content library",
            cta_href="/library",
        ),
        OnboardingStepOut(
            key="proposal",
            title="Create your first proposal",
            description="Turn a strong-fit opportunity into a working proposal with AI-drafted sections.",
            done=prop_count > 0,
            cta_label="Go to pipeline",
            cta_href="/dashboard",
        ),
        OnboardingStepOut(
            key="team",
            title="Invite your team",
            description="Add grant writers and reviewers so you can collaborate on proposals.",
            done=team_count > 1,
            cta_label="Manage team",
            cta_href="/organization",
        ),
    ]

    completed = sum(1 for step in steps if step.done)
    return OnboardingStatusOut(
        steps=steps,
        completed=completed,
        total=len(steps),
        all_complete=completed == len(steps),
        dismissed=bool(tenant and tenant.onboarding_dismissed),
        organization_name=profile.organization_name if profile else (tenant.name if tenant else "your workspace"),
    )


@router.post("/dismiss", response_model=OnboardingStatusOut)
def dismiss_onboarding(user: User = Depends(current_user), db: Session = Depends(get_db)) -> OnboardingStatusOut:
    tenant = db.get(Tenant, user.tenant_id)
    if tenant:
        tenant.onboarding_dismissed = True
        db.commit()
    return onboarding_status(user=user, db=db)
