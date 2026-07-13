import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import OrganizationProfile, Role, Tenant, User


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_sqlite_fk(dbapi_connection, _record):  # noqa: ANN001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def make_tenant(db, slug: str) -> Tenant:
    tenant = Tenant(name=f"Tenant {slug}", slug=slug)
    db.add(tenant)
    db.flush()
    db.add(
        OrganizationProfile(
            tenant_id=tenant.id,
            organization_name=f"Org {slug}",
            mission="AI literacy and cybersecurity education",
            focus_areas=["cybersecurity education", "AI literacy"],
        )
    )
    db.commit()
    return tenant


def make_user(db, tenant: Tenant, email: str, role: Role = Role.OWNER, password: str = "test-password-123") -> tuple[User, str]:
    user = User(
        tenant_id=tenant.id,
        email=email,
        name=email.split("@")[0],
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    token = create_access_token(user.id, user.tenant_id, user.role.value, user.is_super_admin)
    return user, token


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
