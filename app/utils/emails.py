from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

conf = ConnectionConfig(
    MAIL_USERNAME="username",
    MAIL_PASSWORD="password",  # type: ignore
    MAIL_FROM="test@email.com",
    MAIL_PORT=465,
    MAIL_SERVER="mail server",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_email(to: str, subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[to],  # type: ignore
        body=body,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message)
