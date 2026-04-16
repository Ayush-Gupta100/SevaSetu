from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


class AiMatchResponse(BaseModel):
	id: int
	problem_id: int
	user_id: int
	match_score: float
	reason: Optional[str] = None
	created_at: datetime


class AiInsightResponse(BaseModel):
	total_problems: int
	verified_problems: int
	open_tasks: int
	completed_tasks: int
	total_matches: int
	average_match_score: float


class NotificationResponse(BaseModel):
	id: int
	user_id: int
	type: str
	priority: str
	title: str
	message: str
	status: str
	created_at: datetime
	sent_at: Optional[datetime] = None


class MessageResponse(BaseModel):
	message: str


class ImportUploadRequest(BaseModel):
	file_name: str
	rows: list[dict[str, Any]] = Field(default_factory=list)


class ImportUploadResponse(BaseModel):
	import_id: str
	file_name: str
	rows_count: int


class ImportPreviewResponse(BaseModel):
	import_id: str
	file_name: str
	rows_count: int
	preview: list[dict[str, Any]]


class PublicStatsResponse(BaseModel):
	total_ngos: int
	total_problems: int
	total_tasks: int
	total_volunteers: int


class PublicProblemResponse(BaseModel):
	id: int
	title: str
	description: str
	category: Optional[str] = None
	status: str
	created_at: datetime


class PublicJoinRequest(BaseModel):
	name: str = Field(min_length=2, max_length=255)
	email: EmailStr
	phone: Optional[str] = Field(default=None, max_length=32)
	password: str = Field(min_length=6, max_length=128)