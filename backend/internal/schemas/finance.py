from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class DonationCreateRequest(BaseModel):
	ngo_id: int
	amount: Decimal = Field(gt=0)
	currency: str = "INR"
	purpose: Optional[str] = None


class DonationResponse(BaseModel):
	id: int
	donor_id: Optional[int] = None
	ngo_id: int
	amount: Decimal
	currency: str
	purpose: Optional[str] = None
	status: str
	created_at: datetime


class PaymentInitiateRequest(BaseModel):
	donation_id: int
	provider: Literal["razorpay", "stripe", "upi"]
	payment_method: Literal["card", "upi", "netbanking"]
	provider_transaction_id: Optional[str] = None


class PaymentWebhookRequest(BaseModel):
	donation_id: int
	payment_transaction_id: Optional[int] = None
	provider_transaction_id: Optional[str] = None
	status: Literal["success", "failed"]


class PaymentResponse(BaseModel):
	id: int
	donation_id: int
	provider: str
	provider_transaction_id: Optional[str] = None
	amount: Decimal
	status: str
	payment_method: str
	created_at: datetime


class WalletResponse(BaseModel):
	ngo_id: int
	balance: Decimal
	updated_at: datetime


class LedgerResponse(BaseModel):
	id: int
	ngo_id: int
	type: str
	amount: Decimal
	reference_type: str
	reference_id: int
	created_at: datetime


class MessageResponse(BaseModel):
	message: str