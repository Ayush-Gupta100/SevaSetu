from decimal import Decimal

from fastapi import HTTPException, status

from config.db import get_db
from internal.geo_utils import haversine_km
from internal.schemas.problem import ProblemCreateRequest, ProblemProofCreateRequest, ProblemVerifyRequest
from models.models import Location, Problem, ProblemProof, ProblemVerification, User


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
			priority_score=0.0,
			ai_category=payload.category,
			ai_confidence=0.5,
		)
		db.add(problem)
		db.commit()
		db.refresh(problem)
		return problem


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

		return query.order_by(Problem.created_at.desc()).offset(offset).limit(limit).all()


def get_problem_by_id(problem_id: int):
	with get_db() as db:
		problem = db.query(Problem).filter(Problem.id == problem_id).first()
		if not problem:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found.")
		return problem


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