from fastapi import APIRouter, Depends, Query

from handlers.task_handler import accept_task, assign_task, complete_task, create_task, get_tasks, upload_task_proof
from internal.auth_dependencies import get_current_user, require_roles
from internal.schemas.ngo import MessageResponse
from internal.schemas.task import (
	TaskAcceptResponse,
	TaskAssignRequest,
	TaskCreateRequest,
	TaskProofCreateRequest,
	TaskProofResponse,
	TaskResponse,
)


task_router = APIRouter()


@task_router.post("", response_model=TaskResponse)
def create_task_route(
	payload: TaskCreateRequest,
	current_user=Depends(require_roles("ngo_member", "ngo_admin")),
):
	return create_task(payload, current_user)


@task_router.get("", response_model=list[TaskResponse])
def list_tasks_route(
	status: str | None = Query(default=None),
	nearby: bool = Query(default=False),
	page: int = Query(default=1, ge=1),
	limit: int = Query(default=10, ge=1, le=100),
	current_user=Depends(get_current_user),
):
	return get_tasks(status, nearby, page, limit, current_user)


@task_router.post("/{task_id}/assign", response_model=TaskAcceptResponse)
def assign_task_route(
	task_id: int,
	payload: TaskAssignRequest,
	current_user=Depends(require_roles("ngo_member", "ngo_admin")),
):
	return assign_task(task_id, payload, current_user)


@task_router.patch("/{task_id}/accept", response_model=TaskAcceptResponse)
def accept_task_route(task_id: int, current_user=Depends(require_roles("volunteer"))):
	return accept_task(task_id, current_user)


@task_router.post("/{task_id}/proofs", response_model=TaskProofResponse)
def upload_task_proof_route(
	task_id: int,
	payload: TaskProofCreateRequest,
	current_user=Depends(get_current_user),
):
	return upload_task_proof(task_id, payload, current_user)


@task_router.patch("/{task_id}/complete", response_model=TaskAcceptResponse)
def complete_task_route(
	task_id: int,
	current_user=Depends(require_roles("ngo_member", "ngo_admin")),
):
	return complete_task(task_id, current_user)