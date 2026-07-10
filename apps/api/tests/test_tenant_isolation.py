"""Tenant isolation and authorization tests against the live FastAPI app."""

from tests.conftest import auth_headers, make_tenant, make_user


def _create_opportunity(client, token: str, title: str) -> str:
    response = client.post(
        "/opportunities",
        json={"title": title, "agency": "Test Agency", "description": "cybersecurity education program"},
        headers=auth_headers(token),
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]


def test_requests_without_token_are_rejected(client):
    assert client.get("/opportunities").status_code == 401
    assert client.get("/organization/profile").status_code == 401
    assert client.get("/billing/summary").status_code == 401


def test_tenants_cannot_see_each_others_opportunities(client, db_session):
    tenant_a = make_tenant(db_session, "alpha")
    tenant_b = make_tenant(db_session, "beta")
    _, token_a = make_user(db_session, tenant_a, "owner@alpha.org")
    _, token_b = make_user(db_session, tenant_b, "owner@beta.org")

    opp_id = _create_opportunity(client, token_a, "Alpha Only Grant")

    titles_b = [item["title"] for item in client.get("/opportunities", headers=auth_headers(token_b)).json()]
    assert "Alpha Only Grant" not in titles_b

    # Direct-ID access across tenants must 404, not leak
    assert client.get(f"/opportunities/{opp_id}", headers=auth_headers(token_b)).status_code == 404
    assert client.get(f"/opportunities/{opp_id}", headers=auth_headers(token_a)).status_code == 200


def test_viewer_cannot_create_opportunities(client, db_session):
    tenant = make_tenant(db_session, "gamma")
    from app.models import Role

    _, viewer_token = make_user(db_session, tenant, "viewer@gamma.org", role=Role.VIEWER)
    response = client.post(
        "/opportunities",
        json={"title": "Should Fail"},
        headers=auth_headers(viewer_token),
    )
    assert response.status_code == 403


def test_non_super_admin_cannot_access_admin_endpoints(client, db_session):
    tenant = make_tenant(db_session, "delta")
    _, owner_token = make_user(db_session, tenant, "owner@delta.org")
    assert client.get("/admin/tenants", headers=auth_headers(owner_token)).status_code == 403
    assert client.get("/admin/usage", headers=auth_headers(owner_token)).status_code == 403


def test_login_returns_token_and_rejects_bad_password(client, db_session):
    tenant = make_tenant(db_session, "epsilon")
    make_user(db_session, tenant, "owner@epsilon.org", password="correct-horse-battery")

    ok = client.post("/auth/login", json={"email": "owner@epsilon.org", "password": "correct-horse-battery"})
    assert ok.status_code == 200
    body = ok.json()
    assert body["access_token"]
    assert body["tenant_id"] == tenant.id

    bad = client.post("/auth/login", json={"email": "owner@epsilon.org", "password": "wrong"})
    assert bad.status_code == 401


def test_scoring_happens_on_create_and_lists_include_fit(client, db_session):
    tenant = make_tenant(db_session, "zeta")
    _, token = make_user(db_session, tenant, "owner@zeta.org")
    _create_opportunity(client, token, "Cybersecurity Education Grant")

    items = client.get("/opportunities", headers=auth_headers(token)).json()
    assert len(items) == 1
    assert items[0]["fit_score"] is not None
    assert items[0]["recommended_action"] in {"Apply", "Partner", "Monitor", "Skip"}
