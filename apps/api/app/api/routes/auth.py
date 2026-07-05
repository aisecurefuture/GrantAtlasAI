from time import monotonic

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models import User
from app.schemas import LoginIn, TokenOut, UserOut

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
    _failed_logins.pop(email, None)
    token = create_access_token(user.id, user.tenant_id, user.role.value, user.is_super_admin)
    return TokenOut(access_token=token, tenant_id=user.tenant_id, role=user.role.value)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)) -> User:
    return user
