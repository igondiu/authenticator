import datetime

from app.database.schemas import UserIn, DeviceIn, Session, SessionResponse
from app.database import crud
from app.database import models
from app.database import schemas
from app.libs.jwt_management import verify_token_expired, generate_access_token


def create_session(db_connection, user: UserIn, device: DeviceIn):
    # First of all, check if user exists already in DB
    db_user = crud.get_user_by_email(db_connection, email=user.email)
    if db_user:
        # Check if device exists in the database
        db_device = crud.get_device(db_connection, device.vendor_uuid)
        if db_device:
            # User has previously connected using this device.
            # Find the existing session
            db_session = crud.get_session(db_connection, db_user.uuid, db_device.uuid)
            if db_session:
                # Verify if the token is still valid
                if not verify_token_expired(db_session.token, 120):
                    return SessionResponse(
                        uuid=db_session.uuid,
                        created_at=db_session.created_at,
                        token=db_session.token,
                        is_new_user=db_session.is_new_user,
                        is_new_device=db_session.is_new_device,
                        user=schemas.User(**db_user.__dict__),
                        device=schemas.Device(**db_device.__dict__),
                        status=db_session.status
                    ), 200
                else:
                    return create_db_session(db_connection, db_user, db_device)
        else:
            db_device = crud.create_device(db_connection, device)
            if not db_device:
                raise Exception(f"Failed to create user's device {device}")
            return create_db_session(db_connection, db_user, db_device)

    else:
        # Create the new user
        db_user = crud.create_user(db_connection, user)
        if not db_user:
            raise Exception("Something went wrong while creating the user in the database")

        # Create user's device
        db_device = crud.create_device(db_connection, device)
        if not db_device:
            raise Exception("Something went wrong while creating user's device in the database")

        return create_db_session(db_connection, db_user, db_device)


def update_session(db_connection, token: str, otp_code: str):
    # Find the session using token
    db_session = crud.get_session_by_token(db_connection, token)
    if not db_session:
        return

    db_session.status = "confirmed"
    db_connection.commit()
    return db_session


def create_db_session(db_connection, db_user, db_device):
    # Create the new session
    token_lifetime = 2 if db_device.type == 'othr' else 20 * 365 * 24
    session = Session(
        token=generate_access_token({"user_uuid": db_user.uuid}, hours=token_lifetime),
        created_at=datetime.datetime.utcnow(),
        is_new_user=True,
        is_new_device=True,
        status="pending",
        uuid="",
        user_uuid=db_user.uuid,
        device_uuid=db_device.uuid
    )
    db_session = crud.create_session(db_connection, session)
    if not db_session:
        raise Exception("Something went wrong while creating a new session in the database")

    session_resp = SessionResponse(
        uuid=db_session.uuid,
        created_at=db_session.created_at,
        token=db_session.token,
        is_new_user=db_session.is_new_user,
        is_new_device=db_session.is_new_device,
        user=schemas.User(**db_user.to_dict()),
        device=schemas.Device(**db_device.to_dict()),
        status=db_session.status
    )
    return session_resp, 201
