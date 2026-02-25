from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, model_validator, constr

from source.app.auth.utils import get_password_hash
from source.app.users.enums import Order, Roles, Sort
from source.core.schemas import PageSchema, PaginationSchema, ResponseSchema


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    source: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        from_attributes = True

class UserRequest(BaseModel):
    # username: str
    password: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # role_id: int = 2



# class UserCreate(UserRequest):
#     active: bool = True
#     # role: Roles = Roles.USER
#     password_timestamp: float = Field(default_factory=datetime.utcnow().timestamp)

#     @model_validator(mode="after")
#     def validator(cls, values: "UserCreate") -> "UserCreate":
#         values.password = get_password_hash(values.password)
#         return values


class UserResponse(ResponseSchema):
    # username: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    active: bool
    access_token: Optional[str] = None
    phone: Optional[str] = None
    create_date: datetime
    update_date: datetime


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None


class UserUpdateRequestAdmin(UserUpdateRequest):
    active: Optional[bool] = None


class UserUpdate(UserUpdateRequestAdmin):
    password_timestamp: Optional[float] = None

    @model_validator(mode="after")
    def validator(cls, values: "UserUpdate") -> "UserUpdate":
        if password := values.password:
            values.password = get_password_hash(password)
            values.password_timestamp = datetime.utcnow().timestamp()
        return values


class UserPage(PageSchema):
    users: List[UserResponse]


class UserPagination(PaginationSchema):
    sort: Sort = Sort.ID
    order: Order = Order.ASC


class UserId(BaseModel):
    user_id: int


class Username(BaseModel):
    username: str
