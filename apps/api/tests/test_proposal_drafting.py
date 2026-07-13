"""AI proposal-section drafting endpoint (model call mocked — no network in CI)."""

import app.api.routes.proposals as proposals_route
from app.models import Role
from tests.conftest import auth_headers, make_tenant, make_user


def _setup_proposal(client, db_session, slug: str, role: Role = Role.OWNER):
    tenant = make_tenant(db_session, slug)
    _, token = make_user(db_session, tenant, f"owner@{slug}.org", role=role)
    opp = client.post(
        "/opportunities",
        json={"title": "Cyber Education Grant", "description": "cybersecurity education for nonprofits"},
        headers=auth_headers(token),
    ).json()
    proposal = client.post(
        "/proposals",
        json={"opportunity_id": opp["id"], "title": "Cyber Ed Proposal", "outline": [{"heading": "Statement of Need"}]},
        headers=auth_headers(token),
    ).json()
    return token, proposal


def _mock_ai(monkeypatch, text: str = "Drafted need statement grounded in the mission. [INSERT: participants served in 2025]."):
    monkeypatch.setattr(proposals_route, "ai_enabled", lambda: True)
    captured = {}

    def fake_generate(**kwargs):
        captured.update(kwargs)
        return text

    monkeypatch.setattr(proposals_route, "generate_proposal_section", fake_generate)
    return captured


def test_draft_section_upserts_narrative(client, db_session, monkeypatch):
    captured = _mock_ai(monkeypatch)
    token, proposal = _setup_proposal(client, db_session, "draft-a")

    resp = client.post(
        f"/proposals/{proposal['id']}/draft-section",
        json={"heading": "Statement of Need"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200, resp.text
    sections = resp.json()["narrative_sections"]
    assert len(sections) == 1
    assert sections[0]["heading"] == "Statement of Need"
    assert "[INSERT:" in sections[0]["content"]
    # The drafter was grounded in the org profile + opportunity
    assert "mission" in captured["profile"]
    assert captured["opportunity"]["title"] == "Cyber Education Grant"


def test_draft_section_replaces_existing_heading(client, db_session, monkeypatch):
    _mock_ai(monkeypatch, text="First draft.")
    token, proposal = _setup_proposal(client, db_session, "draft-b")
    client.post(f"/proposals/{proposal['id']}/draft-section", json={"heading": "Statement of Need"}, headers=auth_headers(token))

    _mock_ai(monkeypatch, text="Second, better draft.")
    resp = client.post(f"/proposals/{proposal['id']}/draft-section", json={"heading": "Statement of Need"}, headers=auth_headers(token))
    sections = resp.json()["narrative_sections"]
    assert len(sections) == 1  # replaced, not appended
    assert sections[0]["content"] == "Second, better draft."


def test_draft_section_returns_503_when_ai_disabled(client, db_session, monkeypatch):
    monkeypatch.setattr(proposals_route, "ai_enabled", lambda: False)
    token, proposal = _setup_proposal(client, db_session, "draft-c")
    resp = client.post(f"/proposals/{proposal['id']}/draft-section", json={"heading": "Need"}, headers=auth_headers(token))
    assert resp.status_code == 503


def test_draft_section_role_gated(client, db_session, monkeypatch):
    _mock_ai(monkeypatch)
    # Build a proposal as owner, then a viewer in the same tenant tries to draft
    tenant = make_tenant(db_session, "draft-d")
    _, owner_token = make_user(db_session, tenant, "owner@draft-d.org", role=Role.OWNER)
    _, viewer_token = make_user(db_session, tenant, "viewer@draft-d.org", role=Role.VIEWER)
    opp = client.post("/opportunities", json={"title": "Grant"}, headers=auth_headers(owner_token)).json()
    proposal = client.post(
        "/proposals",
        json={"opportunity_id": opp["id"], "title": "P", "outline": [{"heading": "Need"}]},
        headers=auth_headers(owner_token),
    ).json()
    resp = client.post(f"/proposals/{proposal['id']}/draft-section", json={"heading": "Need"}, headers=auth_headers(viewer_token))
    assert resp.status_code == 403


def test_draft_section_tenant_isolation(client, db_session, monkeypatch):
    _mock_ai(monkeypatch)
    token_a, proposal = _setup_proposal(client, db_session, "draft-e")
    tenant_b = make_tenant(db_session, "draft-f")
    _, token_b = make_user(db_session, tenant_b, "owner@draft-f.org")
    resp = client.post(
        f"/proposals/{proposal['id']}/draft-section",
        json={"heading": "Statement of Need"},
        headers=auth_headers(token_b),
    )
    assert resp.status_code == 404
