import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from aiogram.utils.markdown import quote_html

from tatneft_back.core.consts import settings

log = logging.getLogger(__name__)

def send_mail(to_email: str, subject: str, text: str):
    if settings.emulate_mail_sending is True:
        log.info(f'emulating mail sending to {to_email}\n{text}')
        return

    msg = MIMEMultipart()
    msg['From'] = settings.mailru_login
    msg['To'] = to_email
    msg['Subject'] = subject

    body = quote_html(text)
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP_SSL(settings.mailru_server, settings.mailru_port)
        server.login(settings.mailru_login, settings.mailru_password)
        server.sendmail(settings.mailru_login, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        log.exception(e)

