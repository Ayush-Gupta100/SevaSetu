from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status

from config.db import get_db
from internal.geo_utils import haversine_km
from internal.schemas.task import TaskAssignRequest, TaskCreateRequest, TaskProofCreateRequest
from models.models import Location, Problem, Task, TaskAssignment, TaskProof, User


def create_task(payload: TaskCreateRequest, current_user: User):
	with get_db() as db:
		problem = db.query(Problem).filter(Problem.id == payload.problem_id).first()
		if not problem:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found.")

		deadline_value = None
		if payload.deadline:
			deadline_value = datetime.combine(payload.deadline, datetime.min.time())

		task = Task(
			problem_id=payload.problem_id,
			title=payload.title,
			description=payload.description,
			assigned_by=current_user.id,
			status="open",
			deadline=deadline_value,
		)
		db.add(task)
		db.commit()
		db.refresh(task)
		return task


def get_tasks(
	status_filter: str | None,
	nearby: bool,
	mine: bool,
	page: int,
	limit: int,
	current_user: User,
):
	offset = (page - 1) * limit
	with get_db() as db:
		query = db.query(Task)

		if status_filter:
			query = query.filter(Task.status == status_filter)

		if mine:
			query = query.join(TaskAssignment, TaskAssignment.task_id == Task.id).filter(
				TaskAssignment.user_id == current_user.id
			)

		if nearby:
			if not current_user.location_id:
				return []

			user_location = db.query(Location).filter(Location.id == current_user.location_id).first()
			if not user_location:
				return []

			if user_location.latitude is not None and user_location.longitude is not None:
				user_lat = float(user_location.latitude if isinstance(user_location.latitude, Decimal) else user_location.latitude)
				user_lon = float(user_location.longitude if isinstance(user_location.longitude, Decimal) else user_location.longitude)

				nearby_problem_ids = []
				problems = db.query(Problem).all()
				for problem in problems:
					loc = db.query(Location).filter(Location.id == problem.location_id).first()
					if not loc or loc.latitude is None or loc.longitude is None:
						continue
					lat = float(loc.latitude if isinstance(loc.latitude, Decimal) else loc.latitude)
					lon = float(loc.longitude if isinstance(loc.longitude, Decimal) else loc.longitude)
					if haversine_km(user_lat, user_lon, lat, lon) <= 15:
						nearby_problem_ids.append(problem.id)

				if not nearby_problem_ids:
					return []

				query = query.filter(Task.problem_id.in_(nearby_problem_ids))

		return query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()


def assign_task(task_id: int, payload: TaskAssignRequest, current_user: User):
	with get_db() as db:
		task = db.query(Task).filter(Task.id == task_id).first()
		if not task:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

		user = db.query(User).filter(User.id == payload.user_id).first()
		if not user:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

		existing = db.query(TaskAssignment).filter(
			TaskAssignment.task_id == task.id,
			TaskAssignment.user_id == user.id,
		).first()
		if existing:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already assigned.")

		assignment = TaskAssignment(task_id=task.id, user_id=user.id, role=payload.role, status="assigned")
		task.status = "assigned"
		task.assigned_by = current_user.id

		db.add(assignment)
		db.add(task)
		db.commit()
		return {"message": "Task assigned successfully.", "task_id": task.id}


def accept_task(task_id: int, current_user: User):
	with get_db() as db:
		task = db.query(Task).filter(Task.id == task_id).first()
		if not task:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

		assignment = db.query(TaskAssignment).filter(
			TaskAssignment.task_id == task.id,
			TaskAssignment.user_id == current_user.id,
		).first()
		if not assignment:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Task is not assigned to you.")

		assignment.status = "accepted"
		task.status = "in_progress"
		db.add(assignment)
		db.add(task)
		db.commit()
		return {"message": "Task accepted.", "task_id": task.id}


def upload_task_proof(task_id: int, payload: TaskProofCreateRequest, current_user: User):
	with get_db() as db:
		task = db.query(Task).filter(Task.id == task_id).first()
		if not task:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

		proof = TaskProof(
			task_id=task.id,
			file_url=payload.file_url,
			description=payload.description,
			uploaded_by=current_user.id,
		)
		db.add(proof)
		db.commit()
		db.refresh(proof)
		return proof


def complete_task(task_id: int, current_user: User):
	with get_db() as db:
		task = db.query(Task).filter(Task.id == task_id).first()
		if not task:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

		if task.status not in ("in_progress", "assigned"):
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Task can only be completed from assigned/in_progress state.",
			)

		assignments = db.query(TaskAssignment).filter(TaskAssignment.task_id == task.id).all()
		for assignment in assignments:
			if assignment.status in ("accepted", "assigned"):
				assignment.status = "completed"
				db.add(assignment)

		task.status = "completed"
		db.add(task)
		db.commit()
		return {"message": "Task completed successfully.", "task_id": task.id}