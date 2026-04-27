from sqlalchemy.orm import Session

from internal.mailing import send_mail
from models.models import Notification, User


def create_notification(
	db: Session,
	user_id: int,
	title: str,
	message: str,
	notification_type: str = "push",
	priority: str = "medium",
) -> Notification:
	user = db.query(User).filter(User.id == user_id).first()
	status = "pending"

	if user and user.email:
		mail_sent = send_mail(user.email, message)
		if not mail_sent:
			status = "failed"
	else:
		status = "failed"

	notification = Notification(
		user_id=user_id,
		type=notification_type,
		priority=priority,
		title=title,
		message=message,
		status=status,
	)
	db.add(notification)
	return notification
