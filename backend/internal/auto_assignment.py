import json
import logging
import os
import re
from urllib import error, request

from sqlalchemy.orm import Session

from internal.notifications import create_notification
from models.models import Problem, Skill, Task, TaskAssignment, User, UserSkill


_GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
_DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"


logger = logging.getLogger(__name__)


_FALLBACK_SKILL_RULES = {
	"water": ["plumbing", "water distribution", "field operations"],
	"pipe": ["plumbing", "repair", "field operations"],
	"road": ["civil work", "transport coordination", "field operations"],
	"ambulance": ["emergency response", "logistics", "first aid"],
	"medical": ["first aid", "medical support", "inventory"],
	"health": ["first aid", "medical support", "community outreach"],
	"food": ["supply chain", "distribution", "inventory"],
	"electric": ["electrical", "repair", "safety"],
	"flood": ["disaster response", "rescue", "logistics"],
	"fire": ["emergency response", "safety", "rescue"],
	"sanitation": ["hygiene", "waste management", "community outreach"],
}


def _extract_json_block(text: str) -> dict | None:
	if not text:
		return None

	match = re.search(r"\{.*\}", text, flags=re.DOTALL)
	if not match:
		return None

	try:
		return json.loads(match.group(0))
	except json.JSONDecodeError:
		return None


def _infer_with_groq(problem: Problem) -> dict | None:
	api_key = os.getenv("GROQ_API_KEY", "").strip()
	if not api_key:
		logger.debug("Skipping Groq inference because GROQ_API_KEY is not set.")
		return None

	model = os.getenv("GROQ_MODEL", _DEFAULT_GROQ_MODEL).strip() or _DEFAULT_GROQ_MODEL
	prompt = (
		"You are classifying NGO community issues for volunteer assignment. "
		"Return JSON only with keys: category (string), confidence (0 to 1), required_skills (array of short strings).\n"
		f"Title: {problem.title}\n"
		f"Description: {problem.description}\n"
		f"User Category Hint: {problem.category or ''}"
	)

	payload = {
		"model": model,
		"messages": [
			{"role": "system", "content": "Respond with valid JSON only."},
			{"role": "user", "content": prompt},
		],
		"temperature": 0.2,
	}

	data = json.dumps(payload).encode("utf-8")
	req = request.Request(
		_GROQ_API_URL,
		data=data,
		headers={
			"Authorization": f"Bearer {api_key}",
			"Content-Type": "application/json",
			"Accept": "application/json",
			"User-Agent": "curl/8.7.1",
		},
		method="POST",
	)

	try:
		with request.urlopen(req, timeout=8) as resp:
			raw = resp.read().decode("utf-8")
	except (error.URLError, TimeoutError) as exc:
		logger.warning("Groq inference request failed: %s", exc)
		return None

	try:
		parsed = json.loads(raw)
		content = parsed["choices"][0]["message"]["content"]
	except (KeyError, IndexError, TypeError, json.JSONDecodeError):
		return None

	result = _extract_json_block(content)
	if not result:
		return None

	required_skills = result.get("required_skills") or []
	if not isinstance(required_skills, list):
		required_skills = []

	cleaned_skills = []
	for skill in required_skills:
		if isinstance(skill, str) and skill.strip():
			cleaned_skills.append(skill.strip().lower())

	confidence_raw = result.get("confidence", 0.0)
	try:
		confidence = float(confidence_raw)
	except (TypeError, ValueError):
		confidence = 0.0

	category = str(result.get("category") or problem.category or "general").strip().lower()
	if not category:
		category = "general"

	return {
		"category": category,
		"confidence": max(0.0, min(confidence, 1.0)),
		"required_skills": cleaned_skills,
		"inference_source": "groq",
		"inference_model": model,
	}


def _infer_fallback(problem: Problem) -> dict:
	text = f"{problem.title} {problem.description} {problem.category or ''}".lower()
	skills = []
	for key, mapped_skills in _FALLBACK_SKILL_RULES.items():
		if key in text:
			skills.extend(mapped_skills)

	# Preserve order and remove duplicates.
	unique_skills = list(dict.fromkeys([skill.strip().lower() for skill in skills if skill.strip()]))
	category = (problem.category or "general").strip().lower() or "general"

	return {
		"category": category,
		"confidence": 0.4,
		"required_skills": unique_skills,
		"inference_source": "fallback",
		"inference_model": "rule-based",
	}


def infer_problem_profile(problem: Problem) -> dict:
	return _infer_with_groq(problem) or _infer_fallback(problem)


def _active_busy_user_ids(db: Session) -> set[int]:
	rows = (
		db.query(TaskAssignment.user_id)
		.join(Task, Task.id == TaskAssignment.task_id)
		.filter(Task.status.in_(["assigned", "in_progress"]))
		.distinct()
		.all()
	)
	return {row[0] for row in rows}


def _user_skill_index(db: Session, user_ids: list[int]) -> dict[int, set[str]]:
	if not user_ids:
		return {}

	rows = (
		db.query(UserSkill.user_id, Skill.name)
		.join(Skill, Skill.id == UserSkill.skill_id)
		.filter(UserSkill.user_id.in_(user_ids))
		.all()
	)

	index: dict[int, set[str]] = {user_id: set() for user_id in user_ids}
	for user_id, skill_name in rows:
		if skill_name:
			index[user_id].add(skill_name.strip().lower())
	return index


def _score_user(required_skills: list[str], user_skills: set[str], category: str) -> int:
	if not user_skills:
		return 0

	score = 0
	for req in required_skills:
		if req in user_skills:
			score += 3
		elif any(req in user_skill or user_skill in req for user_skill in user_skills):
			score += 2

	if category and any(category in user_skill for user_skill in user_skills):
		score += 1

	return score


def try_auto_assign_task(db: Session, task: Task, assigned_by: int | None = None) -> dict:
	existing_assignment = db.query(TaskAssignment).filter(TaskAssignment.task_id == task.id).first()
	if existing_assignment or task.status != "open":
		return {"assigned": False, "reason": "Task is not pending assignment."}

	problem = db.query(Problem).filter(Problem.id == task.problem_id).first()
	if not problem:
		return {"assigned": False, "reason": "Problem not found for task."}

	profile = infer_problem_profile(problem)
	logger.info(
		"Problem inference completed for problem_id=%s using source=%s model=%s",
		problem.id,
		profile.get("inference_source", "unknown"),
		profile.get("inference_model", "unknown"),
	)
	problem.ai_category = profile["category"]
	problem.ai_confidence = profile["confidence"] * 100
	db.add(problem)

	required_skills: list[str] = profile.get("required_skills", [])
	busy_ids = _active_busy_user_ids(db)

	volunteers = db.query(User).filter(User.role == "volunteer").all()
	available = [user for user in volunteers if user.id not in busy_ids]
	if not available:
		db.commit()
		return {"assigned": False, "reason": "No available volunteers right now."}

	skill_index = _user_skill_index(db, [user.id for user in available])
	best_user = None
	best_score = 0
	for user in available:
		score = _score_user(required_skills, skill_index.get(user.id, set()), profile["category"])
		if score > best_score:
			best_score = score
			best_user = user

	if not best_user or best_score <= 0:
		# Fallback: if no skill-matched volunteer found but volunteers are available,
		# assign to any available volunteer to prevent tasks from being perpetually open.
		if available:
			best_user = available[0]
			logger.info(
				"No skill-match found for task_id=%s; falling back to first available volunteer user_id=%s.",
				task.id,
				best_user.id,
			)
		else:
			db.commit()
			return {
				"assigned": False,
				"reason": "No available volunteers right now.",
			}

	assignment = TaskAssignment(
		task_id=task.id,
		user_id=best_user.id,
		role="volunteer",
		status="assigned",
	)
	task.status = "assigned"
	task.assigned_by = assigned_by or task.assigned_by

	db.add(assignment)
	db.add(task)
	create_notification(
		db,
		user_id=best_user.id,
		title="New Task Assigned",
		message=f"You have been auto-assigned task #{task.id}: {task.title}",
		notification_type="push",
		priority="high",
	)
	db.commit()

	return {
		"assigned": True,
		"task_id": task.id,
		"user_id": best_user.id,
		"required_skills": required_skills,
	}