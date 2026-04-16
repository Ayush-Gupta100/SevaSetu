from fastapi import APIRouter, Depends, Query

from handlers.ngo_handler import add_ngo_member, get_ngo_details, list_ngos, register_ngo, verify_ngo
from internal.auth_dependencies import get_current_user, require_roles
from internal.schemas.ngo import (
	AddNgoMemberRequest,
	MessageResponse,
	NgoCreateRequest,
	NgoResponse,
	NgoVerificationRequest,
)


ngo_router = APIRouter()


@ngo_router.post("", response_model=NgoResponse)
def create_ngo(payload: NgoCreateRequest, current_user=Depends(get_current_user)):
	return register_ngo(payload, current_user)


@ngo_router.get("", response_model=list[NgoResponse])
def get_ngos(
	page: int = Query(default=1, ge=1),
	limit: int = Query(default=10, ge=1, le=100),
	current_user=Depends(get_current_user),
):
	return list_ngos(page=page, limit=limit)


@ngo_router.get("/{ngo_id}", response_model=NgoResponse)
def get_ngo(ngo_id: int, current_user=Depends(get_current_user)):
	return get_ngo_details(ngo_id)


@ngo_router.patch("/{ngo_id}/verify", response_model=NgoResponse)
def verify_ngo_route(
	ngo_id: int,
	payload: NgoVerificationRequest,
	current_user=Depends(require_roles("ngo_admin")),
):
	return verify_ngo(ngo_id, payload)


@ngo_router.post("/{ngo_id}/members", response_model=MessageResponse)
def add_ngo_member_route(
	ngo_id: int,
	payload: AddNgoMemberRequest,
	current_user=Depends(require_roles("ngo_admin")),
):
	return add_ngo_member(ngo_id, payload, current_user)