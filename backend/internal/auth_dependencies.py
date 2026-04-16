from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from config.db import get_db
from internal.security import decode_access_token
from internal.token_blacklist import is_token_blacklisted
from models.models import User


bearer_scheme = HTTPBearer(auto_error=True)


def get_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
	return credentials.credentials


def get_current_user(token: str = Depends(get_bearer_token)):
	if is_token_blacklisted(token):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token has been revoked.",
		)

	try:
		payload = decode_access_token(token)
		user_id = payload.get("sub")
		if not user_id:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid token payload.",
			)
	except InvalidTokenError as exc:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid or expired token.",
		) from exc

	with get_db() as db:
		user = db.query(User).filter(User.id == int(user_id)).first()
		if not user:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="User not found.",
			)
		return user


def require_roles(*allowed_roles: str) -> Callable:
	def role_dependency(current_user: User = Depends(get_current_user)) -> User:
		if current_user.role not in allowed_roles:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="You are not allowed to perform this action.",
			)
		return current_user

	return role_dependency