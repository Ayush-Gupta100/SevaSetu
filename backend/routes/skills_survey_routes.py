from fastapi import APIRouter, Depends

from handlers.skills_survey_handler import add_user_skills, get_skill_categories, get_skills, get_user_skills, submit_survey
from internal.auth_dependencies import get_current_user
from internal.schemas.skills_survey import (
	AddUserSkillsRequest,
	MessageResponse,
	SkillCategoryResponse,
	SkillResponse,
	SurveyRequest,
	SurveyResponse,
	UserSkillResponse,
)


skills_survey_router = APIRouter()


@skills_survey_router.post("/users/skills", response_model=MessageResponse)
def add_user_skills_route(payload: AddUserSkillsRequest, current_user=Depends(get_current_user)):
	return add_user_skills(payload, current_user)


@skills_survey_router.get("/skills", response_model=list[SkillResponse])
def get_skills_route(current_user=Depends(get_current_user)):
	return get_skills()


@skills_survey_router.get("/users/skills/me", response_model=list[UserSkillResponse])
def get_user_skills_route(current_user=Depends(get_current_user)):
	return get_user_skills(current_user)


@skills_survey_router.get("/skills/categories", response_model=list[SkillCategoryResponse])
def get_skill_categories_route(current_user=Depends(get_current_user)):
	return get_skill_categories()


@skills_survey_router.post("/surveys", response_model=SurveyResponse)
def submit_survey_route(payload: SurveyRequest, current_user=Depends(get_current_user)):
	return submit_survey(payload, current_user)