from time import monotonic

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models import AuditLog, User
from app.schemas import LoginIn, RegisterIn, TokenOut, UserOut
from app.services.accounts import VALID_SIGNUP_PLANS, create_tenant_with_owner, email_taken

router = APIRouter()
MAX_FAILED_LOGINS = 10
LOGIN_WINDOW_SECONDS = 15 * 60
_failed_logins: dict[str, list[float]] = {}


def _record_failed_login(email: str) -> None:
    now = monotonic()
    failures = [ts for ts in _failed_logins.get(email, []) if now - ts < LOGIN_WINDOW_SECONDS]
    failures.append(now)
    _failed_logins[email] = failures


def _is_login_limited(email: str) -> bool:
    now = monotonic()
    failures = [ts for ts in _failed_logins.get(email, []) if now - ts < LOGIN_WINDOW_SECONDS]
    _failed_logins[email] = failures
    return len(failures) >= MAX_FAILED_LOGINS


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    email = payload.email.lower()
    if _is_login_limited(email):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many failed login attempts")
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        _record_failed_login(email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This user account has been deactivated")
    if not user.tenant.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This organization's account is deactivated")
    _failed_logins.pop(email, None)
    token = create_access_token(user.id, user.tenant_id, user.role.value, user.is_super_admin)
    return TokenOut(access_token=token, tenant_id=user.tenant_id, role=user.role.value)


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: Session = Depends(get_db)) -> TokenOut:
    if payload.plan not in VALID_SIGNUP_PLANS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Choose a valid subscription plan")
    if email_taken(db, payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")
    tenant, owner = create_tenant_with_owner(
        db,
        organization_name=payload.organization_name,
        owner_name=payload.name,
        owner_email=payload.email,
        password=payload.password,
        plan=payload.plan,
    )
    db.add(
        AuditLog(
            tenant_id=tenant.id,
            actor_user_id=owner.id,
            action="tenant.registered",
            target_type="Tenant",
            target_id=tenant.id,
            metadata_json={"plan": payload.plan},
        )
    )
    db.commit()
    token = create_access_token(owner.id, tenant.id, owner.role.value, owner.is_super_admin)
    return TokenOut(access_token=token, tenant_id=tenant.id, role=owner.role.value)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)) -> User:
    return user
