import mimetypes
import smtplib
import ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import SubmitterConfig
from .consts import DEFAULT_ENCODING
from .logger import LOG


class Attachment:

    def __init__(self, content_type: str, encoding: str, data: bytes):
        self.content_type = content_type
        self.encoding = encoding
        self.data = data


class Mailer:
    _instance = None

    def __init__(self):
        self.cfg = None

    @classmethod
    def init(cls, config: SubmitterConfig):
        cls.get().cfg = config

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = Mailer()
        return cls._instance

    def _msg_text(self, message: str):
        return f"Hello,\n" \
               f"there is a notification from DSW:\n\n" \
               f"{message}\n\n" \
               f"____________________________________________________\n" \
               f"Have a nice day!\n" \
               f"{self.cfg.mail.name}\n"

    def _convert_plain_part(self, message: str) -> MIMEText:
        return MIMEText(self._msg_text(message), 'plain', DEFAULT_ENCODING)

    def _convert_attachment(self, attachment: Attachment) -> MIMEBase:
        mtype, msubtype = attachment.content_type.split('/', maxsplit=1)
        part = MIMEBase(mtype, msubtype)
        part.set_payload(attachment.data)
        encoders.encode_base64(part)
        extension = mimetypes.guess_extension(attachment.content_type) or '.txt'
        filename = f'document{extension}'
        part.add_header('Content-Disposition', f'attachment; filename={filename}')
        return part

    def send(self, recipient: str, message: str, attachments: list[Attachment]):
        LOG.info(f'Sending notification (recipient={recipient})')
        LOG.info(f'Mail server: {self.cfg.mail.host}:{self.cfg.mail.port}'
                 f' ({self.cfg.mail.security})')
        LOG.info(f'Sender: {self.cfg.mail.name} <{self.cfg.mail.email}>')

        msg = MIMEMultipart('mixed')
        msg['From'] = self.cfg.mail.email
        msg['To'] = recipient
        msg['Subject'] = f'[{self.cfg.mail.name}] Notification'
        msg.attach(self._convert_plain_part(message))
        for attachment in attachments:
            msg.attach(self._convert_attachment(attachment))
        result = self._send(recipient, msg)
        LOG.debug(f'Email result: {result}')

    def _send(self, recipient, message):
        if self.cfg.mail.security == 'ssl':
            return self._send_smtp_ssl(
                recipients=[recipient],
                message=message,
            )
        return self._send_smtp(
            recipients=[recipient],
            message=message,
            use_tls=self.cfg.mail.security == 'starttls',
        )

    def _send_smtp_ssl(self, recipients, message):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
                host=self.cfg.mail.host,
                port=self.cfg.mail.port,
                context=context,
                timeout=10,
        ) as server:
            if self.cfg.mail.auth:
                server.login(
                    user=self.cfg.mail.username,
                    password=self.cfg.mail.password,
                )
            return server.send_message(
                msg=message,
                from_addr=self.cfg.mail.email,
                to_addrs=recipients,
            )

    def _send_smtp(self, recipients, message, use_tls: bool):
        context = ssl.create_default_context()
        with smtplib.SMTP(
                host=self.cfg.mail.host,
                port=self.cfg.mail.port,
                timeout=10,
        ) as server:
            if use_tls:
                server.starttls(context=context)
            if self.cfg.mail.auth:
                server.login(
                    user=self.cfg.mail.username,
                    password=self.cfg.mail.password,
                )
            return server.send_message(
                msg=message,
                from_addr=self.cfg.mail.email,
                to_addrs=recipients,
            )
