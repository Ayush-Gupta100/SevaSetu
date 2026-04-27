from fastapi import HTTPException, status

from config.db import get_db
from internal.schemas.resource import AddInventoryRequest, AddRequirementRequest, AllocateResourceRequest
from models.models import (
	Location,
	ResourceAllocation,
	ResourceInventory,
	ResourceRequirement,
	ResourceType,
	Task,
	User,
)


def _resolve_default_location_id(db, current_user: User) -> int | None:
	if current_user.location_id:
		return current_user.location_id

	if current_user.ngo_id:
		ngo_user = (
			db.query(User)
			.filter(User.ngo_id == current_user.ngo_id, User.location_id.isnot(None))
			.order_by(User.id.asc())
			.first()
		)
		if ngo_user:
			return ngo_user.location_id

	return None


def _seed_resource_types() -> None:
	defaults = [
		{"name": "Funds", "category": "financial", "unit": "INR", "description": "Monetary support"},
		{"name": "Water Tanker", "category": "material", "unit": "unit", "description": "Water supply vehicle"},
		{"name": "Volunteer", "category": "human", "unit": "person", "description": "Human support"},
	]
	with get_db() as db:
		count = db.query(ResourceType).count()
		if count == 0:
			for item in defaults:
				db.add(ResourceType(**item))
			db.commit()


def get_resource_types():
	_seed_resource_types()
	with get_db() as db:
		return db.query(ResourceType).order_by(ResourceType.name.asc()).all()


def add_inventory(payload: AddInventoryRequest, current_user: User):
	with get_db() as db:
		resource_type = db.query(ResourceType).filter(ResourceType.id == payload.resource_type_id).first()
		if not resource_type:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource type not found.")

		owner_type = "ngo" if current_user.ngo_id else "user"
		owner_id = current_user.ngo_id if current_user.ngo_id else current_user.id

		location_id = payload.location_id or _resolve_default_location_id(db, current_user)
		if not location_id:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Resource location is required. Please provide a location.",
			)

		location = db.query(Location).filter(Location.id == location_id).first()
		if not location:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found.")

		inventory = ResourceInventory(
			resource_type_id=payload.resource_type_id,
			owner_type=owner_type,
			owner_id=owner_id,
			quantity_total=payload.quantity_total,
			quantity_available=payload.quantity_total,
			location_id=location_id,
		)
		db.add(inventory)
		db.commit()
		db.refresh(inventory)
		return {
			"id": inventory.id,
			"resource_type_id": inventory.resource_type_id,
			"owner_type": inventory.owner_type,
			"owner_id": inventory.owner_id,
			"quantity_total": inventory.quantity_total,
			"quantity_available": inventory.quantity_available,
			"location_id": inventory.location_id,
			"location_address": location.address,
			"created_at": inventory.created_at,
		}


def get_inventory(current_user: User):
	with get_db() as db:
		query = db.query(ResourceInventory)
		if current_user.ngo_id:
			rows = query.filter(
				ResourceInventory.owner_type == "ngo",
				ResourceInventory.owner_id == current_user.ngo_id,
			).all()
		else:
			rows = query.filter(
				ResourceInventory.owner_type == "user",
				ResourceInventory.owner_id == current_user.id,
			).all()

		location_ids = [row.location_id for row in rows if row.location_id]
		location_index = {}
		if location_ids:
			for loc in db.query(Location).filter(Location.id.in_(location_ids)).all():
				location_index[loc.id] = loc.address

		return [
			{
				"id": row.id,
				"resource_type_id": row.resource_type_id,
				"owner_type": row.owner_type,
				"owner_id": row.owner_id,
				"quantity_total": row.quantity_total,
				"quantity_available": row.quantity_available,
				"location_id": row.location_id,
				"location_address": location_index.get(row.location_id),
				"created_at": row.created_at,
			}
			for row in rows
		]


def add_requirement(task_id: int, payload: AddRequirementRequest):
	with get_db() as db:
		task = db.query(Task).filter(Task.id == task_id).first()
		if not task:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

		resource_type = db.query(ResourceType).filter(ResourceType.id == payload.resource_type_id).first()
		if not resource_type:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource type not found.")

		requirement = ResourceRequirement(
			task_id=task.id,
			resource_type_id=payload.resource_type_id,
			quantity_required=payload.quantity_required,
			quantity_allocated=0.0,
			priority_level=payload.priority_level,
		)
		db.add(requirement)
		db.commit()
		db.refresh(requirement)
		return requirement


def allocate_resource(payload: AllocateResourceRequest, current_user: User):
	with get_db() as db:
		requirement = db.query(ResourceRequirement).filter(ResourceRequirement.id == payload.requirement_id).first()
		if not requirement:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found.")

		inventory = db.query(ResourceInventory).filter(ResourceInventory.id == payload.resource_inventory_id).first()
		if not inventory:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource inventory not found.")

		if inventory.resource_type_id != requirement.resource_type_id:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Inventory resource type does not match requirement.",
			)

		if inventory.quantity_available < payload.quantity:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient inventory available.")

		allocation = ResourceAllocation(
			requirement_id=requirement.id,
			resource_inventory_id=inventory.id,
			allocated_quantity=payload.quantity,
			allocated_by=current_user.id,
		)

		inventory.quantity_available -= payload.quantity
		requirement.quantity_allocated += payload.quantity

		db.add(allocation)
		db.add(inventory)
		db.add(requirement)
		db.commit()
		db.refresh(allocation)
		return allocation