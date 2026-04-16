from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ResourceTypeResponse(BaseModel):
	id: int
	name: str
	category: str
	unit: Optional[str] = None
	description: Optional[str] = None


class AddInventoryRequest(BaseModel):
	resource_type_id: int
	quantity_total: float = Field(gt=0)
	location_id: Optional[int] = None


class InventoryResponse(BaseModel):
	id: int
	resource_type_id: int
	owner_type: str
	owner_id: int
	quantity_total: float
	quantity_available: float
	location_id: Optional[int] = None
	created_at: datetime


class AddRequirementRequest(BaseModel):
	resource_type_id: int
	quantity_required: float = Field(gt=0)
	priority_level: Literal["low", "medium", "high"] = "medium"


class RequirementResponse(BaseModel):
	id: int
	task_id: int
	resource_type_id: int
	quantity_required: float
	quantity_allocated: float
	priority_level: str
	created_at: datetime


class AllocateResourceRequest(BaseModel):
	requirement_id: int
	resource_inventory_id: int
	quantity: float = Field(gt=0)


class AllocationResponse(BaseModel):
	id: int
	requirement_id: int
	resource_inventory_id: int
	allocated_quantity: float
	allocated_by: int
	created_at: datetime