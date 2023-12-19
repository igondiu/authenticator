import logging

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi import Header
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session as DbConnection

from app.database.database import get_db
from app.database.schemas import UserIn, DeviceIn, SessionResponse
from app.libs.jwt_management import verify_token_expired

from app.kernels import manage_sessions

router = APIRouter(
    tags=["Authenticator"],
    prefix="/v1"
)


@router.post("/sessions", response_model=SessionResponse)
def create_session(user: UserIn, device: DeviceIn, db: DbConnection = Depends(get_db)):
    # Check received input parameters
    if not user.email or not device.type:
        raise HTTPException(status_code=400, detail="Bad input parameters")

    if device.type == 'mobi' and not device.vendor_uuid:
        raise HTTPException(status_code=400, detail="Bad input parameter <vendor_uuid>")

    try:
        result, response_code = manage_sessions.create_session(db, user, device)
        logging.debug("Session successfully created")
        return result

    except Exception as e:
        logging.exception(f"An error has occurred while creating a session: \n{e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/sessions", response_model=SessionResponse)
def validate_session(otp_code: str, Authorization: str = Header(None), db: DbConnection = Depends(get_db)):
    if Authorization is None:
        raise HTTPException(status_code=400, detail="Token JWT invalide ou expiré")
    bearer_token = Authorization[Authorization.find(" ")+1:]
    if not verify_token_expired(bearer_token, 200):
        raise HTTPException(status_code=400, detail="Token JWT invalide ou expiré")

    try:
        result = manage_sessions.update_session(db, bearer_token, otp_code)
        return result

    except Exception as e:
        logging.exception(f"An error occurred while validating the session of user with token : {bearer_token}\n{e}")
        raise HTTPException(status_code=500, detail="Internal server error")
