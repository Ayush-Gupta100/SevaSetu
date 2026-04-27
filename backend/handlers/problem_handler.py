from decimal import Decimal

from fastapi import HTTPException, status

from config.db import get_db
from internal.geo_utils import haversine_km
from internal.auto_assignment import infer_problem_profile, try_auto_assign_task
from internal.notifications import create_notification
from internal.schemas.problem import ProblemCreateRequest, ProblemProofCreateRequest, ProblemVerifyRequest
from models.models import Location, Problem, ProblemProof, ProblemVerification, Task, TaskAssignment, User


_CATEGORY_PRIORITY_WEIGHT = {
	"emergency": 4.5,
	"health": 4.0,
	"infrastructure": 3.5,
	"water": 3.5,
	"sanitation": 3.0,
	"environment": 2.5,
	"education": 2.0,
	"general": 2.0,
}


def _calculate_priority(profile: dict, location: Location) -> float:
	category = str(profile.get("category") or "general").lower()
	confidence = float(profile.get("confidence") or 0.0)
	confidence_score = max(0.0, min(confidence * 4.0, 4.0))

	category_score = _CATEGORY_PRIORITY_WEIGHT.get(category, 2.5)

	location_text = f"{location.address or ''} {location.city or ''} {location.state or ''}".strip().lower()
	if "pan india" in location_text:
		location_score = 1.0
	elif location.city and location.state:
		location_score = 2.0
	else:
		location_score = 1.5

	priority = confidence_score + category_score + location_score
	return round(max(1.0, min(priority, 10.0)), 1)


def _problem_to_response(db, problem: Problem) -> dict:
	assignment = (
		db.query(TaskAssignment, User)
		.join(Task, Task.id == TaskAssignment.task_id)
		.join(User, User.id == TaskAssignment.user_id)
		.filter(Task.problem_id == problem.id)
		.order_by(TaskAssignment.assigned_at.desc())
		.first()
	)

	assigned_to_id = None
	assigned_to_name = None
	if assignment:
		assigned_to_id = assignment[1].id
		assigned_to_name = assignment[1].name

	return {
		"id": problem.id,
		"title": problem.title,
		"description": problem.description,
		"category": problem.category,
		"location_id": problem.location_id,
		"location_address": problem.location.address if problem.location else None,
		"reported_by": problem.reported_by,
		"status": problem.status,
		"priority_score": problem.priority_score,
		"ai_category": problem.ai_category,
		"ai_confidence": problem.ai_confidence,
		"assigned_to_id": assigned_to_id,
		"assigned_to_name": assigned_to_name,
		"created_at": problem.created_at,
	}


def report_problem(payload: ProblemCreateRequest, current_user: User):
	with get_db() as db:
		location = db.query(Location).filter(Location.id == payload.location_id).first()
		if not location:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found.")

		problem = Problem(
			title=payload.title,
			description=payload.description,
			category=payload.category,
			location_id=payload.location_id,
			reported_by=current_user.id,
			status="pending",
			priority_score=1.0,
			ai_category=payload.category,
			ai_confidence=0.0,
		)
		db.add(problem)
		db.commit()
		db.refresh(problem)

		profile = infer_problem_profile(problem)
		problem.ai_category = profile.get("category")
		problem.ai_confidence = round(float(profile.get("confidence", 0.0)) * 100.0, 1)
		problem.priority_score = _calculate_priority(profile, location)
		db.add(problem)
		db.commit()
		db.refresh(problem)

		task = Task(
			problem_id=problem.id,
			title=f"Resolve: {problem.title}",
			description=problem.description,
			assigned_by=current_user.id,
			status="open",
		)
		db.add(task)
		db.commit()
		db.refresh(task)

		# Attempt smart assignment immediately; if unavailable/unsuitable, task stays open (pending).
		try_auto_assign_task(db, task, assigned_by=current_user.id)
		db.refresh(problem)

		return _problem_to_response(db, problem)


def upload_problem_proof(problem_id: int, payload: ProblemProofCreateRequest, current_user: User):
	with get_db() as db:
		problem = db.query(Problem).filter(Problem.id == problem_id).first()
		if not problem:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found.")

		proof = ProblemProof(
			problem_id=problem.id,
			file_url=payload.file_url,
			file_type=payload.file_type,
			uploaded_by=current_user.id,
		)
		db.add(proof)
		db.commit()
		db.refresh(proof)
		return proof


def get_problems(
	status_filter: str | None,
	category: str | None,
	nearby: bool,
	page: int,
	limit: int,
	current_user: User,
):
	offset = (page - 1) * limit
	with get_db() as db:
		query = db.query(Problem)

		if status_filter:
			query = query.filter(Problem.status == status_filter)

		if category:
			query = query.filter(Problem.category == category)

		if nearby:
			if not current_user.location_id:
				return []

			user_location = db.query(Location).filter(Location.id == current_user.location_id).first()
			if not user_location:
				return []

			if user_location.latitude is not None and user_location.longitude is not None:
				user_lat = float(user_location.latitude if isinstance(user_location.latitude, Decimal) else user_location.latitude)
				user_lon = float(user_location.longitude if isinstance(user_location.longitude, Decimal) else user_location.longitude)
				all_locations = db.query(Location).filter(Location.latitude.isnot(None), Location.longitude.isnot(None)).all()
				nearby_location_ids = []
				for loc in all_locations:
					lat = float(loc.latitude if isinstance(loc.latitude, Decimal) else loc.latitude)
					lon = float(loc.longitude if isinstance(loc.longitude, Decimal) else loc.longitude)
					distance = haversine_km(user_lat, user_lon, lat, lon)
					if distance <= 15:
						nearby_location_ids.append(loc.id)

				if not nearby_location_ids:
					return []

				query = query.filter(Problem.location_id.in_(nearby_location_ids))
			else:
				query = query.filter(Problem.location_id == user_location.id)

		problems = query.order_by(Problem.created_at.desc()).offset(offset).limit(limit).all()
		return [_problem_to_response(db, problem) for problem in problems]


def get_problem_by_id(problem_id: int):
	with get_db() as db:
		problem = db.query(Problem).filter(Problem.id == problem_id).first()
		if not problem:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found.")
		return _problem_to_response(db, problem)


def verify_problem(problem_id: int, payload: ProblemVerifyRequest, current_user: User):
	with get_db() as db:
		problem = db.query(Problem).filter(Problem.id == problem_id).first()
		if not problem:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found.")

		problem_status = "verified" if payload.status == "approved" else "rejected"
		problem.status = problem_status

		verification = db.query(ProblemVerification).filter(ProblemVerification.problem_id == problem.id).first()
		if verification:
			verification.verified_by = current_user.id
			verification.status = payload.status
			verification.notes = payload.notes
		else:
			verification = ProblemVerification(
				problem_id=problem.id,
				verified_by=current_user.id,
				status=payload.status,
				notes=payload.notes,
			)
			db.add(verification)

		db.add(problem)
		create_notification(
			db,
			user_id=problem.reported_by,
			title="Problem Verification Update",
			message=(
				f"Your reported problem '{problem.title}' was {problem_status}."
				if problem_status == "verified"
				else f"Your reported problem '{problem.title}' was rejected."
			),
			notification_type="push",
			priority="medium",
		)
		db.commit()
		db.refresh(verification)

		return {
			"problem_id": problem.id,
			"problem_status": problem_status,
			"verification_status": verification.status,
			"verified_by": verification.verified_by,
			"notes": verification.notes,
			"created_at": verification.created_at,
		}