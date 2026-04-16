from typing import Optional

from pydantic import BaseModel, Field


class GeocodeRequest(BaseModel):
	address: Optional[str] = None
	city: Optional[str] = Field(default=None, max_length=120)
	state: Optional[str] = Field(default=None, max_length=120)
	country: Optional[str] = Field(default="India", max_length=120)
	pincode: Optional[str] = Field(default=None, max_length=20)


class GeocodeResponse(BaseModel):
	location_id: int
	latitude: float
	longitude: float
	address: Optional[str] = None
	city: Optional[str] = None
	state: Optional[str] = None
	country: Optional[str] = None
	pincode: Optional[str] = None


class ReverseGeocodeRequest(BaseModel):
	latitude: float = Field(ge=-90.0, le=90.0)
	longitude: float = Field(ge=-180.0, le=180.0)
	max_distance_km: float = Field(default=20.0, gt=0.0, le=200.0)


class ReverseGeocodeResponse(BaseModel):
	location_id: Optional[int] = None
	latitude: float
	longitude: float
	address: Optional[str] = None
	city: Optional[str] = None
	state: Optional[str] = None
	country: Optional[str] = None
	pincode: Optional[str] = None
	distance_km: Optional[float] = None
	found: bool