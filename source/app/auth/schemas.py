from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: constr(min_length=8)

class EmailRequest(BaseModel):
    email: EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: constr(min_length=8)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None


class Credentials(BaseModel):
    email: str
    password: str
    
class SSO_LOGIN_GOOGLE(BaseModel):
    google_id: str
    email: str
    active: bool = True

class Refresh(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr