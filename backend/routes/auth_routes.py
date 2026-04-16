from fastapi import APIRouter, Depends

from handlers.auth_handler import get_profile, login_user, logout_user, register_user
from internal.auth_dependencies import get_bearer_token, get_current_user
from internal.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserProfileResponse


auth_router = APIRouter()


@auth_router.post("/register", response_model=UserProfileResponse)
def register(payload: RegisterRequest):
	return register_user(payload)


@auth_router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
	return login_user(payload)


@auth_router.get("/me", response_model=UserProfileResponse)
def me(current_user=Depends(get_current_user)):
	return get_profile(current_user)


@auth_router.post("/logout")
def logout(current_user=Depends(get_current_user), token: str = Depends(get_bearer_token)):
	return logout_user(current_user, token)