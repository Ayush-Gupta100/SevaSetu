from fastapi import APIRouter, Depends

from handlers.resource_handler import add_inventory, add_requirement, allocate_resource, get_inventory, get_resource_types
from internal.auth_dependencies import get_current_user
from internal.schemas.resource import (
	AddInventoryRequest,
	AddRequirementRequest,
	AllocateResourceRequest,
	AllocationResponse,
	InventoryResponse,
	RequirementResponse,
	ResourceTypeResponse,
)


resource_router = APIRouter()


@resource_router.get("/resource-types", response_model=list[ResourceTypeResponse])
def get_resource_types_route(current_user=Depends(get_current_user)):
	return get_resource_types()


@resource_router.post("/resources/inventory", response_model=InventoryResponse)
def add_inventory_route(payload: AddInventoryRequest, current_user=Depends(get_current_user)):
	return add_inventory(payload, current_user)


@resource_router.get("/resources/inventory", response_model=list[InventoryResponse])
def get_inventory_route(current_user=Depends(get_current_user)):
	return get_inventory(current_user)


@resource_router.post("/tasks/{task_id}/requirements", response_model=RequirementResponse)
def add_requirement_route(task_id: int, payload: AddRequirementRequest, current_user=Depends(get_current_user)):
	return add_requirement(task_id, payload)


@resource_router.post("/resources/allocate", response_model=AllocationResponse)
def allocate_resource_route(payload: AllocateResourceRequest, current_user=Depends(get_current_user)):
	return allocate_resource(payload, current_user)