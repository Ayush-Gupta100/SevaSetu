import hashlib
import math


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
	# Great-circle distance between two points on Earth.
	radius_km = 6371.0
	phi1 = math.radians(lat1)
	phi2 = math.radians(lat2)
	delta_phi = math.radians(lat2 - lat1)
	delta_lambda = math.radians(lon2 - lon1)

	a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	return radius_km * c


def pseudo_geocode(text: str) -> tuple[float, float]:
	# Deterministic fallback coordinates, bounded to India-centric ranges.
	digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
	lat_seed = int(digest[:8], 16)
	lon_seed = int(digest[8:16], 16)
	lat = 8.0 + (lat_seed / 0xFFFFFFFF) * (37.0 - 8.0)
	lon = 68.0 + (lon_seed / 0xFFFFFFFF) * (97.0 - 68.0)
	return round(lat, 6), round(lon, 6)