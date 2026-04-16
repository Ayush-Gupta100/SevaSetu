from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserSkillItem(BaseModel):
	skill_name: str = Field(min_length=2, max_length=255)
	category: Optional[str] = Field(default=None, max_length=120)
	proficiency_level: Optional[str] = Field(default=None, max_length=80)


class AddUserSkillsRequest(BaseModel):
	skills: list[UserSkillItem]


class SkillResponse(BaseModel):
	id: int
	name: str
	category: Optional[str] = None


class SurveyRequest(BaseModel):
	availability: Optional[str] = None
	interests: Optional[str] = None


class SurveyResponse(BaseModel):
	id: int
	user_id: int
	availability: Optional[str] = None
	interests: Optional[str] = None
	created_at: datetime


class MessageResponse(BaseModel):
	message: str