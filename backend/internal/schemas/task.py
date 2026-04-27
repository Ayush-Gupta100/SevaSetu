from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
	problem_id: int
	title: str = Field(min_length=3, max_length=255)
	description: Optional[str] = None
	deadline: Optional[date] = None


class TaskResponse(BaseModel):
	id: int
	problem_id: int
	title: str
	description: Optional[str] = None
	assigned_by: Optional[int] = None
	assigned_user_id: Optional[int] = None
	status: str
	deadline: Optional[datetime] = None
	created_at: datetime


class TaskAssignRequest(BaseModel):
	user_id: int
	role: Literal["volunteer", "worker"] = "volunteer"


class TaskAcceptResponse(BaseModel):
	message: str
	task_id: int


class TaskProofCreateRequest(BaseModel):
	file_url: str = Field(min_length=5)
	description: Optional[str] = None


class TaskProofResponse(BaseModel):
	id: int
	task_id: int
	file_url: str
	description: Optional[str] = None
	uploaded_by: int
	created_at: datetime