import uuid

from fastapi import HTTPException, status
from sqlalchemy import func

from config.db import get_db
from internal.security import hash_password
from models.models import AiMatch, Ngo, Notification, Problem, Task, User


_IMPORT_STORE: dict[str, dict] = {}


def get_ai_matches(problem_id: int | None):
	with get_db() as db:
		query = db.query(AiMatch)
		if problem_id is not None:
			query = query.filter(AiMatch.problem_id == problem_id)
		return query.order_by(AiMatch.created_at.desc()).all()


def get_ai_insights():
	with get_db() as db:
		total_problems = db.query(Problem).count()
		verified_problems = db.query(Problem).filter(Problem.status == "verified").count()
		open_tasks = db.query(Task).filter(Task.status.in_(["open", "assigned", "in_progress"])).count()
		completed_tasks = db.query(Task).filter(Task.status == "completed").count()
		total_matches = db.query(AiMatch).count()
		avg_match_score = db.query(func.avg(AiMatch.match_score)).scalar() or 0.0
		return {
			"total_problems": total_problems,
			"verified_problems": verified_problems,
			"open_tasks": open_tasks,
			"completed_tasks": completed_tasks,
			"total_matches": total_matches,
			"average_match_score": round(float(avg_match_score), 3),
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
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

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