from datetime import datetime

from sqlalchemy import (
	Column,
	DateTime,
	DECIMAL,
	Boolean,
	Enum,
	Float,
	ForeignKey,
	Integer,
	JSON,
	String,
	Text,
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


def utcnow():
	return datetime.utcnow()


class TimestampMixin:
	created_at = Column(DateTime, nullable=False, default=utcnow)


class Ngo(Base, TimestampMixin):
	__tablename__ = "ngos"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(255), nullable=False)
	registration_number = Column(String(255), unique=True, nullable=False)
	email = Column(String(255), unique=True, nullable=False)
	phone = Column(String(32), nullable=True)
	address = Column(Text, nullable=True)
	city = Column(String(120), nullable=True)
	state = Column(String(120), nullable=True)
	verified = Column(Boolean, nullable=False, default=False)
	trust_score = Column(Float, nullable=False, default=0.0)

	users = relationship("User", back_populates="ngo")
	members = relationship("NgoMember", back_populates="ngo")
	wallet = relationship("NgoWallet", back_populates="ngo", uselist=False)
	donations = relationship("Donation", back_populates="ngo")
	ledger_entries = relationship("LedgerEntry", back_populates="ngo")
	financial_ledger_entries = relationship("FinancialLedger", back_populates="ngo")
	task_expenses = relationship("TaskExpense", back_populates="ngo")
	errors = relationship("ErrorAnalytics", back_populates="ngo")


class Location(Base, TimestampMixin):
	__tablename__ = "locations"

	id = Column(Integer, primary_key=True, autoincrement=True)
	latitude = Column(DECIMAL(9, 6), nullable=True)
	longitude = Column(DECIMAL(9, 6), nullable=True)
	address = Column(Text, nullable=True)
	city = Column(String(120), nullable=True)
	state = Column(String(120), nullable=True)
	country = Column(String(120), nullable=True)
	pincode = Column(String(20), nullable=True)

	users = relationship("User", back_populates="location")
	problems = relationship("Problem", back_populates="location")
	resource_inventory = relationship("ResourceInventory", back_populates="location")


class User(Base, TimestampMixin):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(255), nullable=False)
	email = Column(String(255), unique=True, nullable=False)
	phone = Column(String(32), nullable=True)
	password_hash = Column(String(255), nullable=False)
	role = Column(
		Enum("community", "volunteer", "ngo_member", "ngo_admin", name="user_role"),
		nullable=False,
	)
	ngo_id = Column(Integer, ForeignKey("ngos.id"), nullable=True)
	location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)

	ngo = relationship("Ngo", back_populates="users")
	location = relationship("Location", back_populates="users")
	ngo_memberships = relationship("NgoMember", back_populates="user")
	reported_problems = relationship("Problem", back_populates="reporter")
	uploaded_problem_proofs = relationship("ProblemProof", back_populates="uploaded_by_user")
	verifications = relationship("ProblemVerification", back_populates="verifier")
	assigned_tasks = relationship("Task", back_populates="assignee")
	task_assignments = relationship("TaskAssignment", back_populates="user")
	task_proofs = relationship("TaskProof", back_populates="uploaded_by_user")
	user_skills = relationship("UserSkill", back_populates="user")
	surveys = relationship("Survey", back_populates="user")
	resource_allocations = relationship("ResourceAllocation", back_populates="allocated_by_user")
	ai_matches = relationship("AiMatch", back_populates="user")
	notifications = relationship("Notification", back_populates="user")
	donations = relationship("Donation", back_populates="donor")


class NgoMember(Base):
	__tablename__ = "ngo_members"

	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	ngo_id = Column(Integer, ForeignKey("ngos.id"), nullable=False)
	role = Column(
		Enum("admin", "manager", "field_worker", name="ngo_member_role"),
		nullable=False,
	)
	joined_at = Column(DateTime, nullable=False, default=utcnow)

	user = relationship("User", back_populates="ngo_memberships")
	ngo = relationship("Ngo", back_populates="members")


class Problem(Base, TimestampMixin):
	__tablename__ = "problems"

	id = Column(Integer, primary_key=True, autoincrement=True)
	title = Column(String(255), nullable=False)
	description = Column(Text, nullable=False)
	category = Column(String(120), nullable=True)
	location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
	reported_by = Column(Integer, ForeignKey("users.id"), nullable=False)
	status = Column(
		Enum("pending", "verified", "in_progress", "resolved", "rejected", name="problem_status"),
		nullable=False,
		default="pending",
	)
	priority_score = Column(Float, nullable=False, default=0.0)
	ai_category = Column(String(120), nullable=True)
	ai_confidence = Column(Float, nullable=True)

	location = relationship("Location", back_populates="problems")
	reporter = relationship("User", back_populates="reported_problems")
	proofs = relationship("ProblemProof", back_populates="problem")
	verification = relationship("ProblemVerification", back_populates="problem", uselist=False)
	tasks = relationship("Task", back_populates="problem")
	ai_matches = relationship("AiMatch", back_populates="problem")


class ProblemProof(Base, TimestampMixin):
	__tablename__ = "problem_proofs"

	id = Column(Integer, primary_key=True, autoincrement=True)
	problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
	file_url = Column(Text, nullable=False)
	file_type = Column(String(120), nullable=True)
	file_size = Column(Integer, nullable=True)
	s3_bucket = Column(String(120), nullable=True)
	s3_key = Column(String(255), nullable=True)
	uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)

	problem = relationship("Problem", back_populates="proofs")
	uploaded_by_user = relationship("User", back_populates="uploaded_problem_proofs")


class ProblemVerification(Base, TimestampMixin):
	__tablename__ = "problem_verification"

	id = Column(Integer, primary_key=True, autoincrement=True)
	problem_id = Column(Integer, ForeignKey("problems.id"), unique=True, nullable=False)
	verified_by = Column(Integer, ForeignKey("users.id"), nullable=False)
	status = Column(Enum("approved", "rejected", name="verification_status"), nullable=False)
	notes = Column(Text, nullable=True)

	problem = relationship("Problem", back_populates="verification")
	verifier = relationship("User", back_populates="verifications")


class Task(Base, TimestampMixin):
	__tablename__ = "tasks"

	id = Column(Integer, primary_key=True, autoincrement=True)
	problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
	title = Column(String(255), nullable=False)
	description = Column(Text, nullable=True)
	assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)
	status = Column(
		Enum("open", "assigned", "in_progress", "completed", name="task_status"),
		nullable=False,
		default="open",
	)
	deadline = Column(DateTime, nullable=True)

	problem = relationship("Problem", back_populates="tasks")
	assignee = relationship("User", back_populates="assigned_tasks")
	assignments = relationship("TaskAssignment", back_populates="task")
	proofs = relationship("TaskProof", back_populates="task")
	resource_requirements = relationship("ResourceRequirement", back_populates="task")
	expenses = relationship("TaskExpense", back_populates="task")


class TaskAssignment(Base):
	__tablename__ = "task_assignments"

	id = Column(Integer, primary_key=True, autoincrement=True)
	task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	role = Column(Enum("volunteer", "worker", name="task_assignment_role"), nullable=False)
	status = Column(
		Enum("assigned", "accepted", "completed", name="task_assignment_status"),
		nullable=False,
		default="assigned",
	)
	assigned_at = Column(DateTime, nullable=False, default=utcnow)

	task = relationship("Task", back_populates="assignments")
	user = relationship("User", back_populates="task_assignments")


class TaskProof(Base, TimestampMixin):
	__tablename__ = "task_proofs"

	id = Column(Integer, primary_key=True, autoincrement=True)
	task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
	file_url = Column(Text, nullable=False)
	description = Column(Text, nullable=True)
	uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)

	task = relationship("Task", back_populates="proofs")
	uploaded_by_user = relationship("User", back_populates="task_proofs")


class Skill(Base):
	__tablename__ = "skills"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(255), nullable=False, unique=True)
	category = Column(String(120), nullable=True)

	user_skills = relationship("UserSkill", back_populates="skill")


class UserSkill(Base):
	__tablename__ = "user_skills"

	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
	proficiency_level = Column(String(80), nullable=True)

	user = relationship("User", back_populates="user_skills")
	skill = relationship("Skill", back_populates="user_skills")


class Survey(Base, TimestampMixin):
	__tablename__ = "surveys"

	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	availability = Column(Text, nullable=True)
	interests = Column(Text, nullable=True)

	user = relationship("User", back_populates="surveys")



class ResourceType(Base):
	__tablename__ = "resource_types"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(255), nullable=False, unique=True)
	category = Column(Enum("financial", "material", "human", name="resource_type_category"), nullable=False)
	unit = Column(String(80), nullable=True)
	description = Column(Text, nullable=True)

	inventory = relationship("ResourceInventory", back_populates="resource_type")
	requirements = relationship("ResourceRequirement", back_populates="resource_type")


class ResourceInventory(Base, TimestampMixin):
	__tablename__ = "resource_inventory"

	id = Column(Integer, primary_key=True, autoincrement=True)
	resource_type_id = Column(Integer, ForeignKey("resource_types.id"), nullable=False)
	owner_type = Column(Enum("ngo", "user", name="resource_inventory_owner_type"), nullable=False)
	owner_id = Column(Integer, nullable=False)
	quantity_total = Column(Float, nullable=False, default=0.0)
	quantity_available = Column(Float, nullable=False, default=0.0)
	location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)

	resource_type = relationship("ResourceType", back_populates="inventory")
	location = relationship("Location", back_populates="resource_inventory")
	allocations = relationship("ResourceAllocation", back_populates="resource_inventory")


class ResourceRequirement(Base, TimestampMixin):
	__tablename__ = "resource_requirements"

	id = Column(Integer, primary_key=True, autoincrement=True)
	task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
	resource_type_id = Column(Integer, ForeignKey("resource_types.id"), nullable=False)
	quantity_required = Column(Float, nullable=False, default=0.0)
	quantity_allocated = Column(Float, nullable=False, default=0.0)
	priority_level = Column(Enum("low", "medium", "high", name="resource_requirement_priority"), nullable=False, default="medium")

	task = relationship("Task", back_populates="resource_requirements")
	resource_type = relationship("ResourceType", back_populates="requirements")
	allocations = relationship("ResourceAllocation", back_populates="requirement")


class ResourceAllocation(Base, TimestampMixin):
	__tablename__ = "resource_allocations"

	id = Column(Integer, primary_key=True, autoincrement=True)
	requirement_id = Column(Integer, ForeignKey("resource_requirements.id"), nullable=False)
	resource_inventory_id = Column(Integer, ForeignKey("resource_inventory.id"), nullable=False)
	allocated_quantity = Column(Float, nullable=False, default=0.0)
	allocated_by = Column(Integer, ForeignKey("users.id"), nullable=False)

	requirement = relationship("ResourceRequirement", back_populates="allocations")
	resource_inventory = relationship("ResourceInventory", back_populates="allocations")
	allocated_by_user = relationship("User", back_populates="resource_allocations")


class Donation(Base, TimestampMixin):
	__tablename__ = "donations"

	id = Column(Integer, primary_key=True, autoincrement=True)
	donor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
	ngo_id = Column(Integer, ForeignKey("ngos.id"), nullable=False)
	amount = Column(Float, nullable=False)
	currency = Column(String(10), nullable=False, default="INR")
	status = Column(Enum("pending", "completed", "failed", name="donation_status"), default="pending")
	completed_at = Column(DateTime, nullable=True)

	ngo = relationship("Ngo", back_populates="donations")
	donor = relationship("User", back_populates="donations")
	payment_transactions = relationship("PaymentTransaction", back_populates="donation")


class FinancialLedger(Base, TimestampMixin):
	__tablename__ = "financial_ledger"

	id = Column(Integer, primary_key=True, autoincrement=True)
	ngo_id = Column(Integer, ForeignKey("ngos.id"), nullable=False)
	donation_id = Column(Integer, ForeignKey("donations.id"), nullable=True)
	transaction_type = Column(Enum("credit", "debit", name="ledger_tx_type"), nullable=False)
	amount = Column(Float, nullable=False)
	description = Column(Text, nullable=True)
	balance_after = Column(Float, nullable=False)

	ngo = relationship("Ngo", back_populates="financial_ledger_entries")
	donation = relationship("Donation")


class PaymentTransaction(Base, TimestampMixin):
	__tablename__ = "payment_transactions"

	id = Column(Integer, primary_key=True, autoincrement=True)
	donation_id = Column(Integer, ForeignKey("donations.id"), nullable=False)
	provider = Column(Enum("razorpay", "stripe", "upi", name="payment_provider"), nullable=False)
	provider_transaction_id = Column(String(255), nullable=True)
	amount = Column(DECIMAL(10, 2), nullable=False)
	status = Column(Enum("initiated", "success", "failed", name="payment_status"), nullable=False, default="initiated")
	payment_method = Column(Enum("card", "upi", "netbanking", name="payment_method"), nullable=False)

	donation = relationship("Donation", back_populates="payment_transactions")


class NgoWallet(Base):
	__tablename__ = "ngo_wallets"

	id = Column(Integer, primary_key=True, autoincrement=True)
	ngo_id = Column(Integer, ForeignKey("ngos.id"), nullable=False, unique=True)
	balance = Column(DECIMAL(12, 2), nullable=False, default=0)
	updated_at = Column(DateTime, nullable=False, default=utcnow)

	ngo = relationship("Ngo", back_populates="wallet")


class LedgerEntry(Base, TimestampMixin):
	__tablename__ = "ledger_entries"

	id = Column(Integer, primary_key=True, autoincrement=True)
	ngo_id = Column(Integer, ForeignKey("ngos.id"), nullable=False)
	type = Column(Enum("credit", "debit", name="ledger_entry_type"), nullable=False)
	amount = Column(DECIMAL(10, 2), nullable=False)
	reference_type = Column(Enum("donation", "task_expense", name="ledger_reference_type"), nullable=False)
	reference_id = Column(Integer, nullable=False)

	ngo = relationship("Ngo", back_populates="ledger_entries")


class TaskExpense(Base, TimestampMixin):
	__tablename__ = "task_expenses"

	id = Column(Integer, primary_key=True, autoincrement=True)
	task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
	ngo_id = Column(Integer, ForeignKey("ngos.id"), nullable=False)
	amount = Column(DECIMAL(10, 2), nullable=False)
	description = Column(Text, nullable=True)

	task = relationship("Task", back_populates="expenses")
	ngo = relationship("Ngo", back_populates="task_expenses")


class AiMatch(Base, TimestampMixin):
	__tablename__ = "ai_matches"

	id = Column(Integer, primary_key=True, autoincrement=True)
	problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	match_score = Column(Float, nullable=False, default=0.0)
	reason = Column(Text, nullable=True)

	problem = relationship("Problem", back_populates="ai_matches")
	user = relationship("User", back_populates="ai_matches")


class ErrorAnalytics(Base):
	__tablename__ = "error_analytics"

	id = Column(Integer, primary_key=True, autoincrement=True)
	error_code = Column(String(120), nullable=False)
	module = Column(Enum("import", "ocr", "matching", "task", "notification", name="error_module"), nullable=False)
	count = Column(Integer, nullable=False, default=0)
	last_occurred = Column(DateTime, nullable=True)
	ngo_id = Column(Integer, ForeignKey("ngos.id"), nullable=True)
	context = Column(JSON, nullable=True)

	ngo = relationship("Ngo", back_populates="errors")


class Notification(Base, TimestampMixin):
	__tablename__ = "notifications"

	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	type = Column(Enum("sms", "whatsapp", "push", name="notification_type"), nullable=False)
	priority = Column(Enum("low", "medium", "high", name="notification_priority"), nullable=False, default="medium")
	title = Column(String(255), nullable=False)
	message = Column(Text, nullable=False)
	status = Column(Enum("pending", "sent", "failed", name="notification_status"), nullable=False, default="pending")
	sent_at = Column(DateTime, nullable=True)

	user = relationship("User", back_populates="notifications")
