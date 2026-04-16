from datetime import datetime
from threading import Lock
from typing import Dict, Optional


_lock = Lock()
_blacklisted_tokens: Dict[str, Dict] = {}


def blacklist_token(token: str, payload: Optional[Dict] = None) -> None:
	with _lock:
		_blacklisted_tokens[token] = {
			"payload": payload or {},
			"blacklisted_at": datetime.utcnow().isoformat(),
		}


def is_token_blacklisted(token: str) -> bool:
	with _lock:
		return token in _blacklisted_tokens