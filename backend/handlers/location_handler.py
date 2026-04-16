from decimal import Decimal

from fastapi import HTTPException, status

from config.db import get_db
from internal.geo_utils import haversine_km, pseudo_geocode
from internal.schemas.location import GeocodeRequest, ReverseGeocodeRequest
from models.models import Location


def geocode_address(payload: GeocodeRequest):
	parts = [payload.address, payload.city, payload.state, payload.country, payload.pincode]
	text = ", ".join([part.strip() for part in parts if part and part.strip()])
	if not text:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Provide at least one address field for geocoding.",
		)

	lat, lon = pseudo_geocode(text)

	with get_db() as db:
		existing = db.query(Location).filter(
			Location.address == payload.address,
			Location.city == payload.city,
			Location.state == payload.state,
			Location.country == payload.country,
			Location.pincode == payload.pincode,
		).first()

		if existing:
			return {
				"location_id": existing.id,
				"latitude": float(existing.latitude),
				"longitude": float(existing.longitude),
				"address": existing.address,
				"city": existing.city,
				"state": existing.state,
				"country": existing.country,
				"pincode": existing.pincode,
			}

		location = Location(
			latitude=lat,
			longitude=lon,
			address=payload.address,
			city=payload.city,
			state=payload.state,
			country=payload.country,
			pincode=payload.pincode,
		)
		db.add(location)
		db.commit()
		db.refresh(location)

		return {
			"location_id": location.id,
			"latitude": float(location.latitude),
			"longitude": float(location.longitude),
			"address": location.address,
			"city": location.city,
			"state": location.state,
			"country": location.country,
			"pincode": location.pincode,
		}


def reverse_geocode(payload: ReverseGeocodeRequest):
	with get_db() as db:
		locations = db.query(Location).filter(Location.latitude.isnot(None), Location.longitude.isnot(None)).all()

		closest = None
		closest_distance = None
		for loc in locations:
			lat = float(loc.latitude if isinstance(loc.latitude, Decimal) else loc.latitude)
			lon = float(loc.longitude if isinstance(loc.longitude, Decimal) else loc.longitude)
			distance = haversine_km(payload.latitude, payload.longitude, lat, lon)
			if closest_distance is None or distance < closest_distance:
				closest_distance = distance
				closest = loc

		if closest and closest_distance is not None and closest_distance <= payload.max_distance_km:
			return {
				"location_id": closest.id,
				"latitude": float(closest.latitude),
				"longitude": float(closest.longitude),
				"address": closest.address,
				"city": closest.city,
				"state": closest.state,
				"country": closest.country,
				"pincode": closest.pincode,
				"distance_km": round(closest_distance, 2),
				"found": True,
			}

		return {
			"location_id": None,
			"latitude": payload.latitude,
			"longitude": payload.longitude,
			"address": None,
			"city": None,
			"state": None,
			"country": None,
			"pincode": None,
			"distance_km": None,
			"found": False,
		}