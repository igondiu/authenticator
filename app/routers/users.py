""" Module contains all the CRUD methods on user objects. """
from fastapi import Depends, HTTPException, APIRouter

from app.database import schemas, crud
from app.database.database import get_db
from sqlalchemy.orm import Session

users_router = APIRouter(
    tags=["Authenticator"],
    prefix="/v1"
)


@users_router.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@users_router.get("/users/{user_uuid}", response_model=schemas.User)
def read_user(user_uuid: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_uuid)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
