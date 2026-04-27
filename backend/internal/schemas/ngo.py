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


class NgoHqLocationRequest(BaseModel):
	address: str = Field(min_length=3, max_length=255)
	city: Optional[str] = Field(default=None, max_length=120)
	state: Optional[str] = Field(default=None, max_length=120)
	country: Optional[str] = Field(default="India", max_length=120)
	pincode: Optional[str] = Field(default=None, max_length=20)


class AddNgoMemberRequest(BaseModel):
	user_id: int
	role: Literal["admin", "manager", "field_worker"]


class NgoMemberSkillItem(BaseModel):
	skill_name: str = Field(min_length=2, max_length=255)
	category: Optional[str] = Field(default=None, max_length=120)
	proficiency_level: Optional[str] = Field(default=None, max_length=80)


class AddNgoMemberByEmailRequest(BaseModel):
	email: EmailStr
	name: Optional[str] = Field(default=None, min_length=2, max_length=255)
	phone: Optional[str] = Field(default=None, max_length=32)
	role: Literal["admin", "manager", "field_worker"]
	skills: list[NgoMemberSkillItem] = Field(default_factory=list)
	create_if_missing: bool = True


class AddNgoMemberByEmailResponse(BaseModel):
	message: str
	user_id: int
	created_new_user: bool = False
	temporary_password: Optional[str] = None


class MessageResponse(BaseModel):
	message: str


class NgoMemberImportUploadRequest(BaseModel):
	file_name: str = Field(min_length=1, max_length=255)
	rows: list[dict] = Field(default_factory=list)


class NgoMemberImportUploadResponse(BaseModel):
	import_id: str
	file_name: str
	total_rows: int
	valid_rows: int
	invalid_rows: int


class NgoMemberImportInvalidRow(BaseModel):
	row_number: int
	reason: str
	raw: dict


class NgoMemberImportPreviewResponse(BaseModel):
	import_id: str
	file_name: str
	total_rows: int
	valid_rows: int
	invalid_rows: int
	accepted_fields: list[str]
	required_fields: list[str]
	preview: list[dict]
	invalid_entries: list[NgoMemberImportInvalidRow]


class NgoMemberImportConfirmResponse(BaseModel):
	message: str
	import_id: str
	processed_rows: int
	created_members: int
	already_members: int
	failed_rows: int
	temporary_passwords: list[dict]
	failures: list[dict]