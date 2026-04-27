import os

from config.db import get_db
from internal.auto_assignment import infer_problem_profile, try_auto_assign_task
from internal.geo_utils import pseudo_geocode
from internal.security import hash_password
from models.models import (
	AiMatch,
	Location,
	Problem,
	ProblemProof,
	ProblemVerification,
	ResourceAllocation,
	ResourceRequirement,
	Task,
	TaskAssignment,
	TaskExpense,
	TaskProof,
	User,
)


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


SEED_PROBLEMS = [
	{
		"title": "Water pipeline burst in Sector 9",
		"description": "Main water pipeline has burst and streets are flooding near Sector 9 market.",
		"category": "infrastructure",
		"address": "Sector 9 Market Road",
		"city": "Noida",
		"state": "Uttar Pradesh",
	},
	{
		"title": "Contaminated drinking water complaint",
		"description": "Multiple families reported contaminated tap water with odor and discoloration.",
		"category": "health",
		"address": "Shivaji Nagar Community Block",
		"city": "Pune",
		"state": "Maharashtra",
	},
	{
		"title": "School sanitation facility failure",
		"description": "School washrooms are non-functional and unsafe for children.",
		"category": "sanitation",
		"address": "Govt School Lane",
		"city": "Jaipur",
		"state": "Rajasthan",
	},
	{
		"title": "Drainage overflow after rain",
		"description": "Drainage channels are blocked and overflow has impacted residential lanes.",
		"category": "environment",
		"address": "Lakeview Colony Phase 2",
		"city": "Bhopal",
		"state": "Madhya Pradesh",
	},
	{
		"title": "General volunteer mobilization required",
		"description": "Cross-state volunteer support is needed for nationwide logistics coordination.",
		"category": "general",
		"address": "Pan India",
		"city": "Pan India",
		"state": "India",
	},
]


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


def _ensure_system_reporter(db):
	reporter = db.query(User).filter(User.email == "system.coordinator@local").first()
	if reporter:
		return reporter

	reporter = (
		db.query(User)
		.filter(User.role.in_(["ngo_admin", "ngo_member", "community", "volunteer"]))
		.order_by(User.id.asc())
		.first()
	)
	if reporter:
		return reporter

	reporter = User(
		name="System Coordinator",
		email="system.coordinator@local",
		password_hash=hash_password("ChangeMe@123"),
		role="ngo_admin",
	)
	db.add(reporter)
	db.commit()
	db.refresh(reporter)
	return reporter


def _clear_existing_problems_and_tasks(db):
	problem_ids = [row[0] for row in db.query(Problem.id).all()]
	if not problem_ids:
		return

	task_ids = [row[0] for row in db.query(Task.id).filter(Task.problem_id.in_(problem_ids)).all()]

	if task_ids:
		requirement_ids = [
			row[0]
			for row in db.query(ResourceRequirement.id).filter(ResourceRequirement.task_id.in_(task_ids)).all()
		]
		if requirement_ids:
			db.query(ResourceAllocation).filter(ResourceAllocation.requirement_id.in_(requirement_ids)).delete(
				synchronize_session=False
			)
			db.query(ResourceRequirement).filter(ResourceRequirement.id.in_(requirement_ids)).delete(
				synchronize_session=False
			)

		db.query(TaskProof).filter(TaskProof.task_id.in_(task_ids)).delete(synchronize_session=False)
		db.query(TaskAssignment).filter(TaskAssignment.task_id.in_(task_ids)).delete(synchronize_session=False)
		db.query(TaskExpense).filter(TaskExpense.task_id.in_(task_ids)).delete(synchronize_session=False)
		db.query(Task).filter(Task.id.in_(task_ids)).delete(synchronize_session=False)

	db.query(AiMatch).filter(AiMatch.problem_id.in_(problem_ids)).delete(synchronize_session=False)
	db.query(ProblemProof).filter(ProblemProof.problem_id.in_(problem_ids)).delete(synchronize_session=False)
	db.query(ProblemVerification).filter(ProblemVerification.problem_id.in_(problem_ids)).delete(
		synchronize_session=False
	)
	db.query(Problem).filter(Problem.id.in_(problem_ids)).delete(synchronize_session=False)
	db.commit()


def _get_or_create_location(db, address: str, city: str, state: str) -> Location:
	existing = (
		db.query(Location)
		.filter(Location.address == address, Location.city == city, Location.state == state)
		.first()
	)
	if existing:
		return existing

	lat, lon = pseudo_geocode(f"{address}, {city}, {state}, India")
	location = Location(
		address=address,
		city=city,
		state=state,
		country="India",
		latitude=lat,
		longitude=lon,
	)
	db.add(location)
	db.flush()
	return location


def seed_and_assign_problems_on_startup() -> dict:
	if os.getenv("RESET_PROBLEMS_ON_STARTUP", "true").strip().lower() not in {"1", "true", "yes", "on"}:
		return {"reset": False, "created": 0, "assigned": 0}

	with get_db() as db:
		reporter = _ensure_system_reporter(db)
		_clear_existing_problems_and_tasks(db)

		created = 0
		assigned = 0
		for item in SEED_PROBLEMS:
			location = _get_or_create_location(db, item["address"], item["city"], item["state"])

			problem = Problem(
				title=item["title"],
				description=item["description"],
				category=item["category"],
				location_id=location.id,
				reported_by=reporter.id,
				status="pending",
				priority_score=1.0,
			)
			db.add(problem)
			db.flush()

			profile = infer_problem_profile(problem)
			problem.ai_category = profile.get("category")
			problem.ai_confidence = round(float(profile.get("confidence", 0.0)) * 100.0, 1)
			problem.priority_score = _calculate_priority(profile, location)
			db.add(problem)
			db.flush()

			task = Task(
				problem_id=problem.id,
				title=f"Resolve: {problem.title}",
				description=problem.description,
				assigned_by=reporter.id,
				status="open",
			)
			db.add(task)
			db.flush()

			result = try_auto_assign_task(db, task, assigned_by=reporter.id)
			if result.get("assigned"):
				assigned += 1

			created += 1

		db.commit()
		return {"reset": True, "created": created, "assigned": assigned}
