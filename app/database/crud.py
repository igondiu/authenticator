import datetime
import uuid
from sqlalchemy.orm import Session as DbConnection

from app.database import models
from app.database import schemas


def get_session(db: DbConnection, user_uuid: str, device_uuid: str):
    return db.query(models.Session).filter(models.Session.user_uuid == user_uuid,
                                           models.Session.device_uuid == device_uuid
                                           ).order_by(models.Session.created_at.desc()).first()


def get_session_by_token(db: DbConnection, token: str):
    return db.query(models.Session).filter(models.Session.token == token).first()


def create_session(db: DbConnection, session: schemas.Session):
    db_session = models.Session(uuid="ses-"+uuid.uuid4().__str__(),
                                created_at=session.created_at,
                                token=session.token,
                                device_uuid=session.device_uuid,
                                is_new_user=session.is_new_user,
                                is_new_device=session.is_new_device,
                                status=session.status,
                                user_uuid=session.user_uuid
                                )
    db.add(db_session)
    db.commit()
    return db_session


def delete_session(db: DbConnection, user_id: int):
    pass


def patch_session(db: DbConnection, token: str):
    existing_session = db.query(models.Session).filter(token=token).fetchone()
    session = models.Session(existing_session)
    session.status = "confirmed"
    db.refresh(session)
    db.commit()
    return session


def get_user(db: DbConnection, user_uuid: str):
    return db.query(models.User).filter(models.User.uuid == user_uuid).first()


def get_user_by_email(db: DbConnection, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: DbConnection, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: DbConnection, user: schemas.UserIn):
    db_user = models.User(email=user.email, uuid="usr-"+uuid.uuid4().__str__())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_device(db: DbConnection, vendor_uuid: str):
    return db.query(models.Device).filter(models.Device.vendor_uuid == vendor_uuid).first()


def create_device(db: DbConnection, device: schemas.DeviceIn):
    db_device = models.Device(uuid="dev-"+uuid.uuid4().__str__(), type=device.type, vendor_uuid=device.vendor_uuid)
    db.add(db_device)
    db.commit()
    return db_device
