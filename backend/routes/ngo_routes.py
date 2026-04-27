from fastapi import APIRouter, Depends, Query

from handlers.ngo_handler import (
	add_ngo_member,
	add_ngo_member_by_email,
	confirm_ngo_member_import,
	get_ngo_details,
	list_ngo_members,
	list_ngos,
	preview_ngo_member_import,
	register_ngo,
	upload_ngo_member_import,
	update_ngo_hq_location,
	verify_ngo,
)
from internal.auth_dependencies import get_current_user, require_roles
from internal.schemas.ngo import (
	AddNgoMemberRequest,
	AddNgoMemberByEmailRequest,
	AddNgoMemberByEmailResponse,
	NgoMemberImportConfirmResponse,
	NgoMemberImportPreviewResponse,
	NgoMemberImportUploadRequest,
	NgoMemberImportUploadResponse,
	MessageResponse,
	NgoCreateRequest,
	NgoHqLocationRequest,
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


@ngo_router.patch("/{ngo_id}/hq-location", response_model=MessageResponse)
def update_ngo_hq_location_route(
	ngo_id: int,
	payload: NgoHqLocationRequest,
	current_user=Depends(require_roles("ngo_admin", "ngo_member")),
):
	return update_ngo_hq_location(ngo_id, payload, current_user)


@ngo_router.post("/{ngo_id}/members", response_model=MessageResponse)
def add_ngo_member_route(
	ngo_id: int,
	payload: AddNgoMemberRequest,
	current_user=Depends(require_roles("ngo_admin")),
):
	return add_ngo_member(ngo_id, payload, current_user)


@ngo_router.post("/{ngo_id}/members/by-email", response_model=AddNgoMemberByEmailResponse)
def add_ngo_member_by_email_route(
	ngo_id: int,
	payload: AddNgoMemberByEmailRequest,
	current_user=Depends(require_roles("ngo_admin")),
):
	return add_ngo_member_by_email(ngo_id, payload, current_user)


@ngo_router.get("/{ngo_id}/members")
def get_ngo_members_route(
	ngo_id: int,
	current_user=Depends(require_roles("ngo_admin", "ngo_member")),
):
	return list_ngo_members(ngo_id, current_user)


@ngo_router.post("/{ngo_id}/members/import/upload", response_model=NgoMemberImportUploadResponse)
def upload_ngo_member_import_route(
	ngo_id: int,
	payload: NgoMemberImportUploadRequest,
	current_user=Depends(require_roles("ngo_admin")),
):
	return upload_ngo_member_import(ngo_id, payload.file_name, payload.rows, current_user)


@ngo_router.get("/{ngo_id}/members/import/{import_id}/preview", response_model=NgoMemberImportPreviewResponse)
def preview_ngo_member_import_route(
	ngo_id: int,
	import_id: str,
	current_user=Depends(require_roles("ngo_admin")),
):
	return preview_ngo_member_import(ngo_id, import_id, current_user)


@ngo_router.post("/{ngo_id}/members/import/{import_id}/confirm", response_model=NgoMemberImportConfirmResponse)
def confirm_ngo_member_import_route(
	ngo_id: int,
	import_id: str,
	current_user=Depends(require_roles("ngo_admin")),
):
	return confirm_ngo_member_import(ngo_id, import_id, current_user)