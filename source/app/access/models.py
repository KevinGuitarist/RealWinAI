# source/app/access/models.py

from sqlalchemy import Column, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from source.core.models import Model

# association tables
user_roles = Table(
    "user_roles", Model.metadata,
    Column("user_id", ForeignKey("User.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True),
)

role_permissions = Table(
    "role_permissions", Model.metadata,
    Column("role_id", ForeignKey("role.id"), primary_key=True),
    Column("permission_id", ForeignKey("permission.id"), primary_key=True),
)

class Role(Model):
    __tablename__ = "role"
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)

    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
    )
    users = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
        lazy="selectin",   # <- async-safe eager loader

    )

class Permission(Model):
    __tablename__ = "permission"
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)

    roles = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
    )

class UserSettings(Model):
    __tablename__ = "user_settings"
    user_id = Column(ForeignKey("User.id"), unique=True, index=True)
    email_notifications = Column(Boolean, default=False)
    timezone = Column(String, default="UTC")
    language = Column(String, default="en")

    user = relationship("User", back_populates="settings")
