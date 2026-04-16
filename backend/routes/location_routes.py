from fastapi import APIRouter, Depends

from handlers.location_handler import geocode_address, reverse_geocode
from internal.auth_dependencies import get_current_user
from internal.schemas.location import (
	GeocodeRequest,
	GeocodeResponse,
	ReverseGeocodeRequest,
	ReverseGeocodeResponse,
)


location_router = APIRouter()


@location_router.post("/geocode", response_model=GeocodeResponse)
def geocode(payload: GeocodeRequest, current_user=Depends(get_current_user)):
	return geocode_address(payload)


@location_router.post("/reverse", response_model=ReverseGeocodeResponse)
def reverse(payload: ReverseGeocodeRequest, current_user=Depends(get_current_user)):
	return reverse_geocode(payload)