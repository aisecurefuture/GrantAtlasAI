"""Registration, team management, and tenant lifecycle tests."""

from app.models import Role, Tenant, User
from tests.conftest import auth_headers, make_tenant, make_user


def _register(client, email="founder@neworg.org", plan="Professional", org="New Org Inc"):
    return client.post(
        "/auth/register",
        json={
            "organization_name": org,
            "name": "Founder",
            "email": email,
            "password": "a-long-password-123",
            "plan": plan,
        },
    )


# ---------------- Registration ----------------


def test_register_creates_tenant_owner_and_trial(client, db_session):
    response = _register(client)
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["access_token"]
    assert body["role"] == "Owner"

    tenant = db_session.get(Tenant, body["tenant_id"])
    assert tenant.plan == "Professional"
    assert tenant.subscription_status == "trialing"
    assert tenant.trial_end is not None
    assert tenant.is_active

    # Token works immediately
    me = client.get("/auth/me", headers=auth_headers(body["access_token"]))
    assert me.status_code == 200
    assert me.json()["email"] == "founder@neworg.org"

    # Profile stub exists so scoring works from day one
    profile = client.get("/organization/profile", headers=auth_headers(body["access_token"]))
    assert profile.status_code == 200
    assert profile.json()["organization_name"] == "New Org Inc"


def test_register_rejects_invalid_plan_and_duplicate_email(client):
    assert _register(client, plan="Platinum").status_code == 400
    assert _register(client).status_code == 201
    assert _register(client, org="Other Org").status_code == 409


def test_register_generates_unique_slugs(client, db_session):
    assert _register(client, email="a@dup.org", org="Same Name").status_code == 201
    assert _register(client, email="b@dup.org", org="Same Name").status_code == 201
    slugs = [t.slug for t in db_session.query(Tenant).filter(Tenant.name == "Same Name").all()]
    assert len(set(slugs)) == 2


# ---------------- Team management ----------------


def test_owner_can_add_and_manage_users(client, db_session):
    tenant = make_tenant(db_session, "team-a")
    _, token = make_user(db_session, tenant, "owner@team-a.org")

    created = client.post(
        "/organization/users",
        json={"email": "writer@team-a.org", "name": "Writer", "role": "Grant Writer"},
        headers=auth_headers(token),
    )
    assert created.status_code == 200, created.text
    body = created.json()
    assert body["temporary_password"]
    new_id = body["user"]["id"]

    # New user can log in with the temp password
    login = client.post("/auth/login", json={"email": "writer@team-a.org", "password": body["temporary_password"]})
    assert login.status_code == 200

    # Role change + deactivation
    updated = client.patch(f"/organization/users/{new_id}", json={"role": "Reviewer"}, headers=auth_headers(token))
    assert updated.status_code == 200 and updated.json()["role"] == "Reviewer"
    deactivated = client.patch(f"/organization/users/{new_id}", json={"is_active": False}, headers=auth_headers(token))
    assert deactivated.status_code == 200
    login_blocked = client.post("/auth/login", json={"email": "writer@team-a.org", "password": body["temporary_password"]})
    assert login_blocked.status_code == 403


def test_cannot_remove_last_active_owner(client, db_session):
    tenant = make_tenant(db_session, "team-b")
    owner, token = make_user(db_session, tenant, "owner@team-b.org")
    response = client.patch(f"/organization/users/{owner.id}", json={"role": "Viewer"}, headers=auth_headers(token))
    assert response.status_code == 400


def test_seat_limit_enforced(client, db_session):
    tenant = make_tenant(db_session, "team-c")
    tenant.plan = "Starter"
    tenant.usage_limits = {"users": 1, "saved_opportunities": 50, "proposal_workspaces": 5}
    db_session.commit()
    _, token = make_user(db_session, tenant, "owner@team-c.org")
    response = client.post(
        "/organization/users",
        json={"email": "extra@team-c.org", "name": "Extra", "role": "Viewer"},
        headers=auth_headers(token),
    )
    assert response.status_code == 402


def test_viewer_cannot_manage_team(client, db_session):
    tenant = make_tenant(db_session, "team-d")
    make_user(db_session, tenant, "owner@team-d.org")
    _, viewer_token = make_user(db_session, tenant, "viewer@team-d.org", role=Role.VIEWER)
    assert client.get("/organization/users", headers=auth_headers(viewer_token)).status_code == 403


# ---------------- Tenant lifecycle ----------------


def test_self_deactivation_blocks_all_access(client, db_session):
    tenant = make_tenant(db_session, "life-a")
    _, token = make_user(db_session, tenant, "owner@life-a.org", password="a-long-password-123")

    assert client.post("/organization/deactivate", headers=auth_headers(token)).status_code == 200
    # Existing token stops working
    assert client.get("/opportunities", headers=auth_headers(token)).status_code == 403
    # Fresh login is blocked
    login = client.post("/auth/login", json={"email": "owner@life-a.org", "password": "a-long-password-123"})
    assert login.status_code == 403


def test_self_delete_requires_name_confirmation_and_removes_data(client, db_session):
    tenant = make_tenant(db_session, "life-b")
    _, token = make_user(db_session, tenant, "owner@life-b.org")
    tenant_id = tenant.id

    wrong = client.post("/organization/delete", json={"confirm_organization_name": "nope"}, headers=auth_headers(token))
    assert wrong.status_code == 400

    ok = client.post("/organization/delete", json={"confirm_organization_name": tenant.name}, headers=auth_headers(token))
    assert ok.status_code == 200
    assert db_session.get(Tenant, tenant_id) is None
    assert db_session.query(User).filter(User.tenant_id == tenant_id).count() == 0


# ---------------- Super-admin tenant management ----------------


def _super_admin(client, db_session):
    tenant = make_tenant(db_session, "platform")
    admin = User(
        tenant_id=tenant.id,
        email="root@platform.org",
        name="Root",
        password_hash="x",
        role=Role.OWNER,
        is_super_admin=True,
    )
    db_session.add(admin)
    db_session.commit()
    from app.core.security import create_access_token

    return tenant, create_access_token(admin.id, admin.tenant_id, admin.role.value, True)


def test_admin_can_create_deactivate_and_delete_tenants(client, db_session):
    _, admin_token = _super_admin(client, db_session)

    created = client.post(
        "/admin/tenants",
        json={"organization_name": "Managed Org", "owner_name": "Olive", "owner_email": "olive@managed.org", "plan": "Growth"},
        headers=auth_headers(admin_token),
    )
    assert created.status_code == 200, created.text
    body = created.json()
    tenant_id = body["tenant_id"]
    assert body["temporary_password"]

    # Owner can log in, then admin deactivates for non-payment
    login = client.post("/auth/login", json={"email": "olive@managed.org", "password": body["temporary_password"]})
    assert login.status_code == 200
    assert client.post(f"/admin/tenants/{tenant_id}/deactivate", headers=auth_headers(admin_token)).status_code == 200
    login_blocked = client.post("/auth/login", json={"email": "olive@managed.org", "password": body["temporary_password"]})
    assert login_blocked.status_code == 403

    # Reactivate restores access
    assert client.post(f"/admin/tenants/{tenant_id}/activate", headers=auth_headers(admin_token)).status_code == 200
    assert client.post("/auth/login", json={"email": "olive@managed.org", "password": body["temporary_password"]}).status_code == 200

    # Delete removes the tenant entirely
    assert client.delete(f"/admin/tenants/{tenant_id}", headers=auth_headers(admin_token)).status_code == 200
    assert db_session.get(Tenant, tenant_id) is None


def test_admin_cannot_delete_own_platform_tenant(client, db_session):
    platform, admin_token = _super_admin(client, db_session)
    assert client.delete(f"/admin/tenants/{platform.id}", headers=auth_headers(admin_token)).status_code == 400
    assert client.post(f"/admin/tenants/{platform.id}/deactivate", headers=auth_headers(admin_token)).status_code == 400


# ---------------- Profile save re-scores the pipeline ----------------


def test_profile_save_scores_previously_unscored_opportunities(client, db_session):
    # Register a brand-new tenant (profile stub exists but mission is empty)
    body = _register(client, email="rescore@org.org", org="Rescore Org").json()
    token = body["access_token"]

    # Opportunity created before the profile is meaningfully filled in
    opp = client.post(
        "/opportunities",
        json={"title": "Cyber Education Grant", "description": "cybersecurity education for nonprofits"},
        headers=auth_headers(token),
    ).json()

    # Now fill in the profile — this must (re)score the existing pipeline
    saved = client.put(
        "/organization/profile",
        json={
            "organization_name": "Rescore Org",
            "mission": "Cybersecurity education and AI literacy for nonprofits",
            "focus_areas": ["cybersecurity education"],
        },
        headers=auth_headers(token),
    )
    assert saved.status_code == 200, saved.text

    detail = client.get(f"/opportunities/{opp['id']}", headers=auth_headers(token)).json()
    assert detail["score"] is not None
    assert detail["score"]["total_score"] > 0


# ---------------- Proposal editing ----------------


def test_proposal_update_persists_edits(client, db_session):
    tenant = make_tenant(db_session, "prop-a")
    _, token = make_user(db_session, tenant, "owner@prop-a.org")

    opp = client.post("/opportunities", json={"title": "Editable Grant"}, headers=auth_headers(token)).json()
    workspace = client.post(
        "/proposals",
        json={"opportunity_id": opp["id"], "title": "Draft 1", "outline": [{"heading": "Summary", "status": "Not started"}]},
        headers=auth_headers(token),
    ).json()

    updated = client.put(
        f"/proposals/{workspace['id']}",
        json={
            "title": "Draft 2",
            "outline": [{"heading": "Summary", "status": "Complete"}, {"heading": "Budget", "status": "Drafting"}],
            "compliance_matrix": [{"requirement": "Eligibility", "owner": "Founder", "status": "Mapped"}],
            "internal_notes": "Reviewed by board",
        },
        headers=auth_headers(token),
    )
    assert updated.status_code == 200, updated.text
    body = updated.json()
    assert body["title"] == "Draft 2"
    assert len(body["outline"]) == 2
    assert body["compliance_matrix"][0]["status"] == "Mapped"
    assert body["internal_notes"] == "Reviewed by board"

    # Viewer cannot edit
    _, viewer_token = make_user(db_session, tenant, "viewer@prop-a.org", role=Role.VIEWER)
    denied = client.put(f"/proposals/{workspace['id']}", json={"title": "Hax"}, headers=auth_headers(viewer_token))
    assert denied.status_code == 403
