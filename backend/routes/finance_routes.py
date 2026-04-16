from fastapi import APIRouter, Depends

from handlers.finance_handler import (
	create_donation,
	get_donations,
	get_ngo_ledger,
	get_ngo_wallet,
	handle_payment_webhook,
	initiate_payment,
)
from internal.auth_dependencies import get_current_user
from internal.schemas.finance import (
	DonationCreateRequest,
	DonationResponse,
	LedgerResponse,
	MessageResponse,
	PaymentInitiateRequest,
	PaymentResponse,
	PaymentWebhookRequest,
	WalletResponse,
)


finance_router = APIRouter()


@finance_router.post("/donations", response_model=DonationResponse)
def create_donation_route(payload: DonationCreateRequest, current_user=Depends(get_current_user)):
	return create_donation(payload, current_user)


@finance_router.post("/payments/initiate", response_model=PaymentResponse)
def initiate_payment_route(payload: PaymentInitiateRequest, current_user=Depends(get_current_user)):
	return initiate_payment(payload)


@finance_router.post("/payments/webhook", response_model=MessageResponse)
def payment_webhook_route(payload: PaymentWebhookRequest):
	return handle_payment_webhook(payload)


@finance_router.get("/donations", response_model=list[DonationResponse])
def get_donations_route(current_user=Depends(get_current_user)):
	return get_donations(current_user)


@finance_router.get("/ngos/{ngo_id}/wallet", response_model=WalletResponse)
def get_ngo_wallet_route(ngo_id: int, current_user=Depends(get_current_user)):
	return get_ngo_wallet(ngo_id)


@finance_router.get("/ngos/{ngo_id}/ledger", response_model=list[LedgerResponse])
def get_ngo_ledger_route(ngo_id: int, current_user=Depends(get_current_user)):
	return get_ngo_ledger(ngo_id)