from fastapi import APIRouter, Depends, Query

from handlers.problem_handler import (
	get_problem_by_id,
	get_problems,
	report_problem,
	upload_problem_proof,
	verify_problem,
)
from internal.auth_dependencies import get_current_user, require_roles
from internal.schemas.problem import (
	ProblemCreateRequest,
	ProblemProofCreateRequest,
	ProblemProofResponse,
	ProblemResponse,
	ProblemVerifyRequest,
	ProblemVerifyResponse,
)


problem_router = APIRouter()


@problem_router.post("", response_model=ProblemResponse)
def create_problem(payload: ProblemCreateRequest, current_user=Depends(get_current_user)):
	return report_problem(payload, current_user)


@problem_router.post("/{problem_id}/proofs", response_model=ProblemProofResponse)
def add_problem_proof(
	problem_id: int,
	payload: ProblemProofCreateRequest,
	current_user=Depends(get_current_user),
):
	return upload_problem_proof(problem_id, payload, current_user)


@problem_router.get("", response_model=list[ProblemResponse])
def list_problems(
	status: str | None = Query(default=None),
	category: str | None = Query(default=None),
	nearby: bool = Query(default=False),
	page: int = Query(default=1, ge=1),
	limit: int = Query(default=10, ge=1, le=100),
	current_user=Depends(get_current_user),
):
	return get_problems(status, category, nearby, page, limit, current_user)


@problem_router.get("/{problem_id}", response_model=ProblemResponse)
def get_problem(problem_id: int, current_user=Depends(get_current_user)):
	return get_problem_by_id(problem_id)


@problem_router.patch("/{problem_id}/verify", response_model=ProblemVerifyResponse)
def verify_problem_route(
	problem_id: int,
	payload: ProblemVerifyRequest,
	current_user=Depends(require_roles("ngo_member", "ngo_admin")),
):
	return verify_problem(problem_id, payload, current_user)