from pydantic import BaseModel
from typing import List, Optional

class PermissionBase(BaseModel):
    name: str
    description: Optional[str]

class PermissionCreate(PermissionBase):
    pass

class PermissionRead(PermissionBase):
    id: int
    class Config:
        orm_mode = True

class RoleBase(BaseModel):
    name: str
    description: Optional[str]

class RoleCreate(RoleBase):
    permission_ids: List[int] = []

class RoleRead(RoleBase):
    id: int
    permissions: List[PermissionRead] = []
    class Config:
        orm_mode = True

class UserSettingsBase(BaseModel):
    email_notifications: bool
    timezone: str
    language: str

class UserSettingsRead(UserSettingsBase):
    id: int
    class Config:
        orm_mode = True

class UserSettingsUpdate(BaseModel):
    email_notifications: Optional[bool]
    timezone: Optional[str]
    language: Optional[str]
