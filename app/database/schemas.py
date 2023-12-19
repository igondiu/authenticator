from pydantic import BaseModel
from datetime import datetime


class UserIn(BaseModel):
    email: str


class User(UserIn):
    uuid: str

    class Config:
        orm_mode = True


class DeviceIn(BaseModel):
    type: str  # Can be 'mobi' or 'othr'
    vendor_uuid: str


class Device(DeviceIn):
    uuid: str

    class Config:
        orm_mode = True


class SessionBase(BaseModel):
    token: str
    is_new_user: bool
    is_new_device: bool
    status: str


class SessionCreate(SessionBase):
    pass


class Session(SessionBase):
    uuid: str
    created_at: datetime
    user_uuid: str
    device_uuid: str

    class Config:
        orm_mode = True


class SessionResponse(SessionBase):
    device: Device
    user: User
    uuid: str
    created_at: datetime
