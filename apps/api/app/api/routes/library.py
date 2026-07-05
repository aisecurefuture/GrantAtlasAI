from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import current_user, require_role
from app.db.session import get_db
from app.models import LibraryItem, Role, User
from app.schemas import LibraryItemIn, LibraryItemOut

router = APIRouter()


@router.get("", response_model=list[LibraryItemOut])
def list_items(category: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[LibraryItem]:
    query = db.query(LibraryItem).filter(LibraryItem.tenant_id == user.tenant_id)
    if category:
        query = query.filter(LibraryItem.category == category)
    return query.order_by(LibraryItem.category.asc(), LibraryItem.title.asc()).all()


@router.post("", response_model=LibraryItemOut)
def create_item(
    payload: LibraryItemIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN, Role.GRANT_WRITER)),
    db: Session = Depends(get_db),
) -> LibraryItem:
    item = LibraryItem(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=LibraryItemOut)
def update_item(
    item_id: str,
    payload: LibraryItemIn,
    user: User = Depends(require_role(Role.OWNER, Role.ADMIN, Role.GRANT_WRITER)),
    db: Session = Depends(get_db),
) -> LibraryItem:
    item = db.query(LibraryItem).filter(LibraryItem.id == item_id, LibraryItem.tenant_id == user.tenant_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Library item not found")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

