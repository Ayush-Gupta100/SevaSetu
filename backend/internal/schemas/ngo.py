from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class NgoCreateRequest(BaseModel):
	name: str = Field(min_length=2, max_length=255)
	registration_number: str = Field(min_length=2, max_length=255)
	email: EmailStr
	phone: Optional[str] = Field(default=None, max_length=32)
	address: Optional[str] = None
	city: Optional[str] = Field(default=None, max_length=120)
	state: Optional[str] = Field(default=None, max_length=120)


class NgoResponse(BaseModel):
	id: int
	name: str
	registration_number: str
	email: EmailStr
	phone: Optional[str] = None
	address: Optional[str] = None
	city: Optional[str] = None
	state: Optional[str] = None
	verified: bool
	trust_score: float
	created_at: datetime


class NgoVerificationRequest(BaseModel):
	verified: bool = True
	trust_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)


class AddNgoMemberRequest(BaseModel):
	user_id: int
	role: Literal["admin", "manager", "field_worker"]


class MessageResponse(BaseModel):
	message: str