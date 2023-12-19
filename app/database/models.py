from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import database


class User(database.Base):
    __tablename__ = "users"

    uuid = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)

    sessions = relationship("Session", back_populates="user")

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "email": self.email
        }


class Session(database.Base):
    __tablename__ = "sessions"

    uuid = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime)
    token = Column(String)
    is_new_user = Column(Boolean, default=True)
    is_new_device = Column(Boolean, default=True)
    status = Column(String, default="pending")
    device_uuid = Column(String, ForeignKey("devices.uuid"))
    user_uuid = Column(String, ForeignKey("users.uuid"))

    user = relationship("User", back_populates="sessions")
    device = relationship("Device", back_populates="sessions")


class Device(database.Base):
    __tablename__ = "devices"

    uuid = Column(String, primary_key=True, index=True)
    type = Column(String)
    vendor_uuid = Column(String)

    sessions = relationship("Session", back_populates="device")

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "type": self.type,
            "vendor_uuid": self.vendor_uuid
        }


class Code(database.Base):
    __tablename__ = "validation_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String)
    token = Column(String)


database.Base.metadata.create_all(bind=database.engine)
