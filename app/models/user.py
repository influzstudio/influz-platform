from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import hashlib, secrets


class AdminUser(Base):
    __tablename__ = "admin_users"

    id           = Column(Integer, primary_key=True)
    email        = Column(String, unique=True, nullable=False)
    name         = Column(String, default="")
    password_hash= Column(String, nullable=False)
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()


class ClientUser(Base):
    __tablename__ = "client_users"

    id           = Column(Integer, primary_key=True)
    client_id    = Column(Integer, ForeignKey("clients.id"), nullable=False)
    email        = Column(String, unique=True, nullable=False)
    name         = Column(String, default="")
    password_hash= Column(String, nullable=False)
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", back_populates="users")

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
