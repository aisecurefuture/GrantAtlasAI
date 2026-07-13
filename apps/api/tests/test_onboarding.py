"""Onboarding status is computed from real tenant data and is dismissible."""

from tests.conftest import auth_headers, make_tenant, make_user


def test_fresh_tenant_has_incomplete_onboarding(client, db_session):
    tenant = make_tenant(db_session, "onb-a")
    _, token = make_user(db_session, tenant, "owner@onb-a.org")

    status = client.get("/onboarding/status", headers=auth_headers(token)).json()
    assert status["total"] == 5
    assert status["dismissed"] is False
    assert status["all_complete"] is False
    keys = {s["key"]: s["done"] for s in status["steps"]}
    # make_tenant seeds a profile with mission + focus_areas but no past_performance
    assert keys["profile"] is False
    assert keys["opportunities"] is False
    assert keys["library"] is False


def test_steps_flip_to_done_as_work_happens(client, db_session):
    tenant = make_tenant(db_session, "onb-b")
    _, token = make_user(db_session, tenant, "owner@onb-b.org")

    # Complete the profile (adds past_performance) and add a library item
    client.put(
        "/organization/profile",
        json={
            "organization_name": "Onb B",
            "mission": "Cybersecurity education",
            "focus_areas": ["cybersecurity education"],
            "past_performance": "Delivered training to 500 educators.",
        },
        headers=auth_headers(token),
    )
    client.post("/library", json={"title": "Mission", "category": "Boilerplate", "body": "..."}, headers=auth_headers(token))

    status = client.get("/onboarding/status", headers=auth_headers(token)).json()
    keys = {s["key"]: s["done"] for s in status["steps"]}
    assert keys["profile"] is True
    assert keys["library"] is True
    assert status["completed"] >= 2


def test_dismiss_persists(client, db_session):
    tenant = make_tenant(db_session, "onb-c")
    _, token = make_user(db_session, tenant, "owner@onb-c.org")

    dismissed = client.post("/onboarding/dismiss", headers=auth_headers(token)).json()
    assert dismissed["dismissed"] is True
    assert client.get("/onboarding/status", headers=auth_headers(token)).json()["dismissed"] is True


def test_onboarding_requires_auth(client):
    assert client.get("/onboarding/status").status_code == 401
