import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Sender credentials
EMAIL = "your_email@gmail.com"
APP_PASSWORD = "your_app_password"

def send_email(to_email, subject, message):
    try:
        # Setup server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, APP_PASSWORD)

        # Create message
        msg = MIMEMultipart()
        msg["From"] = EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        # Send email
        server.sendmail(EMAIL, to_email, msg.as_string())
        server.quit()

        print("✅ Email sent successfully!")

    except Exception as e:
        print("❌ Error:", e)

# ---- INPUT SECTION ----
to_email = input("Enter recipient email: ")
subject = input("Enter subject: ")
message = input("Enter message: ")

send_email(to_email, subject, message)