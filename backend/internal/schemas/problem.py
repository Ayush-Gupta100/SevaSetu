from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ProblemCreateRequest(BaseModel):
	title: str = Field(min_length=3, max_length=255)
	description: str = Field(min_length=5)
	category: Optional[str] = Field(default=None, max_length=120)
	location_id: int


class ProblemResponse(BaseModel):
	id: int
	title: str
	description: str
	category: Optional[str] = None
	location_id: int
	location_address: Optional[str] = None
	reported_by: int
	status: str
	priority_score: float
	ai_category: Optional[str] = None
	ai_confidence: Optional[float] = None
	assigned_to_id: Optional[int] = None
	assigned_to_name: Optional[str] = None
	created_at: datetime


class ProblemProofCreateRequest(BaseModel):
	file_url: str = Field(min_length=5)
	file_type: Optional[str] = Field(default=None, max_length=120)


class ProblemProofResponse(BaseModel):
	id: int
	problem_id: int
	file_url: str
	file_type: Optional[str] = None
	uploaded_by: int
	created_at: datetime


class ProblemVerifyRequest(BaseModel):
	status: Literal["approved", "rejected"]
	notes: Optional[str] = None


class ProblemVerifyResponse(BaseModel):
	problem_id: int
	problem_status: Literal["verified", "rejected"]
	verification_status: Literal["approved", "rejected"]
	verified_by: int
	notes: Optional[str] = None
	created_at: datetime