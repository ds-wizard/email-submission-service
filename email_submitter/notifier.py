import json

from .config import SubmitterConfig
from .mailer import Mailer, Attachment


def send_notification(content_type: str, encoding: str, data: bytes,
                      recipient: str, intro_message: str, cfg: SubmitterConfig):
    Mailer.init(cfg)
    mailer = Mailer.get()
    if content_type == 'application/json':
        doc = json.loads(data.decode(encoding))
        project_name = doc.get('questionnaireName', '?')
        base_url = doc.get('config', {}).get('clientUrl', '?')
        project_uuid = doc.get('questionnaireUuid', '?')
        message = f'{intro_message}\n\n' \
                  f'Project "{project_name}" ' \
                  f'(link: {base_url}/projects/{project_uuid})'
        mailer.send(
            recipient=recipient,
            message=message,
            attachments=[],
        )
    else:
        mailer.send(
            recipient=recipient,
            message=intro_message,
            attachments=[
                Attachment(
                    content_type=content_type,
                    encoding=encoding,
                    data=data,
                )
            ],
        )
