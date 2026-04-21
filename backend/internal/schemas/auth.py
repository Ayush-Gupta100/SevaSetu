from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
	name: str = Field(min_length=2, max_length=255)
	email: EmailStr
	phone: Optional[str] = None
	password: str = Field(min_length=6, max_length=128)
	role: Literal["community", "volunteer", "ngo_member", "ngo_admin"]


class RegisterNgoRequest(BaseModel):
	admin_name: str = Field(min_length=2, max_length=255)
	admin_email: EmailStr
	admin_password: str = Field(min_length=6, max_length=128)
	ngo_name: str = Field(min_length=2, max_length=255)
	registration_number: str = Field(min_length=2, max_length=255)
	ngo_email: EmailStr
	address: Optional[str] = None


class LoginRequest(BaseModel):
	email: EmailStr
	password: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
	access_token: str
	token_type: str = "bearer"
	expires_in: int
	must_change_password: bool = False


class UserProfileResponse(BaseModel):
	id: int
	name: str
	email: EmailStr
	phone: Optional[str] = None
	role: str
	ngo_id: Optional[int] = None
	location_id: Optional[int] = None
	must_change_password: bool = False
	created_at: datetime


class ChangePasswordRequest(BaseModel):
	current_password: str = Field(min_length=6, max_length=128)
	new_password: str = Field(min_length=6, max_length=128)


class MessageResponse(BaseModel):
	message: str