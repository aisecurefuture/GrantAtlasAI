from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models import User
from app.schemas import LoginIn, TokenOut, UserOut

router = APIRouter()


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token(user.id, user.tenant_id, user.role.value, user.is_super_admin)
    return TokenOut(access_token=token, tenant_id=user.tenant_id, role=user.role.value)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)) -> User:
    return user

