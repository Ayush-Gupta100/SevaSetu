import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import func

from config.db import get_db
from internal.security import hash_password
from models.models import AiMatch, Ngo, Notification, Problem, Task, User


_IMPORT_STORE: dict[str, dict] = {}


def get_ai_matches(problem_id: int | None):
	with get_db() as db:
		if not problem_id:
			return db.query(AiMatch).order_by(AiMatch.match_score.desc()).all()
		
		problem = db.query(Problem).filter(Problem.id == problem_id).first()
		if not problem:
			raise HTTPException(status_code=404, detail="Problem not found")

		# 1. Fetch all volunteers
		volunteers = db.query(User).filter(User.role == "volunteer").all()
		
		matches = []
		for v in volunteers:
			# Mock Skill Match (Check if user has any skills matching problem category)
			skill_score = 0.5
			if v.user_skills and problem.category:
				skill_score = 1.0 if any(
					(us.skill and us.skill.name and us.skill.name.lower() in problem.category.lower())
					for us in v.user_skills
				) else 0.5
			
			# Mock Distance (In a real app, use Haversine with v.location and problem.location)
			# For now, generate a semi-random distance score
			distance_score = 0.8 # Placeholder
			
			# Urgency Score
			urgency_score = min(problem.priority_score / 10.0, 1.0)
			
			final_score = (skill_score * 0.4) + (distance_score * 0.3) + (urgency_score * 0.3)
			
			matches.append({
				"id": 0,
				"user_id": v.id,
				"problem_id": problem.id,
				"match_score": round(final_score, 2),
				"reason": f"Match based on skill ({skill_score}), proximity ({distance_score}), and urgency ({urgency_score})",
				"created_at": datetime.utcnow(),
			})
		
		# Sort by score
		matches.sort(key=lambda x: x["match_score"], reverse=True)
		return matches[:10]


def get_ai_insights():
	with get_db() as db:
		total_problems = db.query(Problem).count()
		verified_problems = db.query(Problem).filter(Problem.status == "verified").count()
		open_tasks = db.query(Task).filter(Task.status.in_(["open", "assigned", "in_progress"])).count()
		completed_tasks = db.query(Task).filter(Task.status == "completed").count()
		total_matches = db.query(AiMatch).count()
		avg_match_score = db.query(func.avg(AiMatch.match_score)).scalar()
		
		return {
			"total_problems": total_problems,
			"verified_problems": verified_problems,
			"open_tasks": open_tasks,
			"completed_tasks": completed_tasks,
			"total_matches": total_matches,
			"average_match_score": float(avg_match_score or 0.0),
		}


def get_notifications(current_user: User):
	with get_db() as db:
		return db.query(Notification).filter(Notification.user_id == current_user.id).order_by(
			Notification.created_at.desc()
		).all()


def mark_notification_read(notification_id: int, current_user: User):
	with get_db() as db:
		notification = db.query(Notification).filter(
			Notification.id == notification_id,
			Notification.user_id == current_user.id,
		).first()
		if not notification:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

		notification.status = "sent"
		db.add(notification)
		db.commit()
		return {"message": "Notification marked as read."}


def import_upload(file_name: str, rows: list[dict]):
	import_id = uuid.uuid4().hex[:12]
	_IMPORT_STORE[import_id] = {"file_name": file_name, "rows": rows, "confirmed": False}
	return {"import_id": import_id, "file_name": file_name, "rows_count": len(rows)}


def import_preview(import_id: str):
	entry = _IMPORT_STORE.get(import_id)
	if not entry:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import batch not found.")
	return {
		"import_id": import_id,
		"file_name": entry["file_name"],
		"rows_count": len(entry["rows"]),
		"preview": entry["rows"][:20],
	}


def import_confirm(import_id: str):
	entry = _IMPORT_STORE.get(import_id)
	if not entry:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import batch not found.")
	entry["confirmed"] = True
	return {"message": f"Import {import_id} confirmed with {len(entry['rows'])} rows."}


def get_public_stats():
	with get_db() as db:
		return {
			"total_ngos": db.query(Ngo).count(),
			"total_problems": db.query(Problem).count(),
			"total_tasks": db.query(Task).count(),
			"total_volunteers": db.query(User).filter(User.role == "volunteer").count(),
		}


def get_public_problems():
	with get_db() as db:
		return db.query(Problem).filter(Problem.status != "rejected").order_by(Problem.created_at.desc()).limit(100).all()


def public_join(name: str, email: str, phone: str | None, password: str):
	with get_db() as db:
		existing = db.query(User).filter(User.email == email).first()
		if existing:
			if existing.role == "volunteer":
				return {"message": "You are already registered as a volunteer."}

			if existing.role in {"ngo_admin", "ngo_member"}:
				if phone and not existing.phone:
					existing.phone = phone
					db.add(existing)
					db.commit()
				return {
					"message": "Your NGO account remains unchanged. You can participate through task assignments without switching roles."
				}

			existing.role = "volunteer"
			if phone and not existing.phone:
				existing.phone = phone
			db.add(existing)
			db.commit()
			return {"message": "Your account has been upgraded to volunteer."}

		user = User(
			name=name,
			email=email,
			phone=phone,
			password_hash=hash_password(password),
			role="volunteer",
		)
		db.add(user)
		db.commit()
		return {"message": "Volunteer registration successful."}


def volunteer_opt_in(current_user: User):
	with get_db() as db:
		user = db.query(User).filter(User.id == current_user.id).first()
		if not user:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

		if user.role == "volunteer":
			return {"message": "You are already registered as a volunteer."}

		if user.role in {"ngo_admin", "ngo_member"}:
			return {
				"message": "Your NGO role remains unchanged. You can contribute through assigned tasks."
			}

		user.role = "volunteer"
		db.add(user)
		db.commit()
		return {"message": "You are now registered as a volunteer."}