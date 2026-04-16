from fastapi import APIRouter, Depends, Query

from handlers.misc_handler import (
	get_ai_insights,
	get_ai_matches,
	get_notifications,
	get_public_problems,
	get_public_stats,
	import_confirm,
	import_preview,
	import_upload,
	mark_notification_read,
	public_join,
)
from internal.auth_dependencies import get_current_user
from internal.schemas.misc import (
	AiInsightResponse,
	AiMatchResponse,
	ImportPreviewResponse,
	ImportUploadRequest,
	ImportUploadResponse,
	MessageResponse,
	NotificationResponse,
	PublicJoinRequest,
	PublicProblemResponse,
	PublicStatsResponse,
)


misc_router = APIRouter()


@misc_router.get("/ai/matches", response_model=list[AiMatchResponse])
def get_ai_matches_route(problem_id: int | None = Query(default=None), current_user=Depends(get_current_user)):
	return get_ai_matches(problem_id)


@misc_router.get("/ai/insights", response_model=AiInsightResponse)
def get_ai_insights_route(current_user=Depends(get_current_user)):
	return get_ai_insights()


@misc_router.get("/notifications", response_model=list[NotificationResponse])
def get_notifications_route(current_user=Depends(get_current_user)):
	return get_notifications(current_user)


@misc_router.patch("/notifications/{notification_id}/read", response_model=MessageResponse)
def mark_notification_read_route(notification_id: int, current_user=Depends(get_current_user)):
	return mark_notification_read(notification_id, current_user)


@misc_router.post("/import/upload", response_model=ImportUploadResponse)
def import_upload_route(payload: ImportUploadRequest, current_user=Depends(get_current_user)):
	return import_upload(payload.file_name, payload.rows)


@misc_router.get("/import/{import_id}/preview", response_model=ImportPreviewResponse)
def import_preview_route(import_id: str, current_user=Depends(get_current_user)):
	return import_preview(import_id)


@misc_router.post("/import/{import_id}/confirm", response_model=MessageResponse)
def import_confirm_route(import_id: str, current_user=Depends(get_current_user)):
	return import_confirm(import_id)


@misc_router.get("/public/stats", response_model=PublicStatsResponse)
def public_stats_route():
	return get_public_stats()


@misc_router.get("/public/problems", response_model=list[PublicProblemResponse])
def public_problems_route():
	return get_public_problems()


@misc_router.post("/public/join", response_model=MessageResponse)
def public_join_route(payload: PublicJoinRequest):
	return public_join(payload.name, payload.email, payload.phone, payload.password)