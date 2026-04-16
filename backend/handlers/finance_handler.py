from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status

from config.db import get_db
from internal.schemas.finance import DonationCreateRequest, PaymentInitiateRequest, PaymentWebhookRequest
from models.models import Donation, LedgerEntry, Ngo, NgoWallet, PaymentTransaction, User


def create_donation(payload: DonationCreateRequest, current_user: User):
	with get_db() as db:
		ngo = db.query(Ngo).filter(Ngo.id == payload.ngo_id).first()
		if not ngo:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NGO not found.")

		donation = Donation(
			donor_id=current_user.id,
			ngo_id=payload.ngo_id,
			amount=payload.amount,
			currency=payload.currency,
			purpose=payload.purpose,
			status="pending",
		)
		db.add(donation)
		db.commit()
		db.refresh(donation)
		return donation


def initiate_payment(payload: PaymentInitiateRequest):
	with get_db() as db:
		donation = db.query(Donation).filter(Donation.id == payload.donation_id).first()
		if not donation:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donation not found.")

		payment = PaymentTransaction(
			donation_id=donation.id,
			provider=payload.provider,
			provider_transaction_id=payload.provider_transaction_id,
			amount=donation.amount,
			status="initiated",
			payment_method=payload.payment_method,
		)
		db.add(payment)
		db.commit()
		db.refresh(payment)
		return payment


def handle_payment_webhook(payload: PaymentWebhookRequest):
	with get_db() as db:
		donation = db.query(Donation).filter(Donation.id == payload.donation_id).first()
		if not donation:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donation not found.")

		payment = None
		if payload.payment_transaction_id:
			payment = db.query(PaymentTransaction).filter(PaymentTransaction.id == payload.payment_transaction_id).first()
		elif payload.provider_transaction_id:
			payment = db.query(PaymentTransaction).filter(
				PaymentTransaction.provider_transaction_id == payload.provider_transaction_id
			).first()

		if not payment:
			payment = db.query(PaymentTransaction).filter(PaymentTransaction.donation_id == donation.id).order_by(
				PaymentTransaction.id.desc()
			).first()

		if payment:
			payment.status = payload.status
			if payload.provider_transaction_id:
				payment.provider_transaction_id = payload.provider_transaction_id
			db.add(payment)

		if payload.status == "success":
			already_completed = donation.status == "completed"
			donation.status = "completed"
			donation.completed_at = datetime.utcnow()
			db.add(donation)

			if not already_completed:
				wallet = db.query(NgoWallet).filter(NgoWallet.ngo_id == donation.ngo_id).first()
				if not wallet:
					wallet = NgoWallet(ngo_id=donation.ngo_id, balance=Decimal("0.00"), updated_at=datetime.utcnow())
				wallet.balance = Decimal(wallet.balance) + Decimal(donation.amount)
				wallet.updated_at = datetime.utcnow()
				db.add(wallet)

				ledger = LedgerEntry(
					ngo_id=donation.ngo_id,
					type="credit",
					amount=donation.amount,
					reference_type="donation",
					reference_id=donation.id,
				)
				db.add(ledger)
		else:
			donation.status = "failed"
			db.add(donation)

		db.commit()
		return {"message": "Payment webhook processed."}


def get_donations(current_user: User):
	with get_db() as db:
		if current_user.role in ("ngo_member", "ngo_admin") and current_user.ngo_id:
			return db.query(Donation).filter(Donation.ngo_id == current_user.ngo_id).order_by(Donation.created_at.desc()).all()

		return db.query(Donation).filter(Donation.donor_id == current_user.id).order_by(Donation.created_at.desc()).all()


def get_ngo_wallet(ngo_id: int):
	with get_db() as db:
		wallet = db.query(NgoWallet).filter(NgoWallet.ngo_id == ngo_id).first()
		if not wallet:
			wallet = NgoWallet(ngo_id=ngo_id, balance=Decimal("0.00"), updated_at=datetime.utcnow())
			db.add(wallet)
			db.commit()
			db.refresh(wallet)
		return wallet


def get_ngo_ledger(ngo_id: int):
	with get_db() as db:
		return db.query(LedgerEntry).filter(LedgerEntry.ngo_id == ngo_id).order_by(LedgerEntry.created_at.desc()).all()