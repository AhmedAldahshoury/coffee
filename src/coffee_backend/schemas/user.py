from pydantic import BaseModel, EmailStr

from coffee_backend.schemas.common import TimestampedSchema


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(TimestampedSchema):
    email: EmailStr
    name: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
