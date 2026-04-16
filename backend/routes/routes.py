from fastapi import APIRouter

from routes.auth_routes import auth_router
from routes.finance_routes import finance_router
from routes.location_routes import location_router
from routes.misc_routes import misc_router
from routes.ngo_routes import ngo_router
from routes.problem_routes import problem_router
from routes.resource_routes import resource_router
from routes.skills_survey_routes import skills_survey_router
from routes.task_routes import task_router


api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(ngo_router, prefix="/ngos", tags=["ngos"])
api_router.include_router(location_router, prefix="/locations", tags=["locations"])
api_router.include_router(problem_router, prefix="/problems", tags=["problems"])
api_router.include_router(task_router, prefix="/tasks", tags=["tasks"])
api_router.include_router(skills_survey_router, tags=["skills-survey"])
api_router.include_router(resource_router, tags=["resources"])
api_router.include_router(finance_router, tags=["finance"])
api_router.include_router(misc_router, tags=["misc"])
