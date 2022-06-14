import fastapi
import fastapi.responses
import os
import pathlib
import traceback

from .config import cfg_parser
from .consts import NICE_NAME, VERSION, BUILD_INFO,\
    ENV_CONFIG, DEFAULT_CONFIG, DEFAULT_ENCODING
from .logger import LOG, init_default_logging, init_config_logging
from .notifier import send_notification

from typing import Tuple

app = fastapi.FastAPI(
    title=NICE_NAME,
    version=VERSION,
)
cfg = cfg_parser.config


def _valid_token(request: fastapi.Request) -> bool:
    if not cfg.security.enabled:
        LOG.debug('Security disabled, authorized directly')
        return True
    auth = request.headers.get('Authorization', '')  # type: str
    if not auth.startswith('Bearer '):
        LOG.debug('Invalid token (missing or without "Bearer " prefix')
        return False
    token = auth.split(' ', maxsplit=1)[1]
    return token in cfg.security.tokens


def _extract_content_type(header: str) -> Tuple[str, str]:
    type_headers = header.lower().split(';')
    input_format = type_headers[0]
    if len(type_headers) == 0:
        return input_format, DEFAULT_ENCODING
    encoding_header = type_headers[0].strip()
    if encoding_header.startswith('charset='):
        return input_format, encoding_header[9:]
    return input_format, DEFAULT_ENCODING


@app.get(path='/')
async def get_info():
    return fastapi.responses.JSONResponse(
        content=BUILD_INFO,
    )


@app.post(path='/submit')
async def submit(request: fastapi.Request):
    # (1) Verify authorization
    if not _valid_token(request=request):
        return fastapi.responses.PlainTextResponse(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            content='Unauthorized submission request.\n\n'
                    'The submission service is not configured properly.\n'
        )
    # (2) Get data
    content_type, encoding = _extract_content_type(
        header=request.headers.get('Content-Type', ''),
    )
    recipient = request.headers.get('X-Msg-Recipient', '')
    intro_message = request.headers.get('X-Msg-Intro', '')
    location = request.headers.get('X-Location', None)
    data = await request.body()
    # (3) Return response
    if recipient == '':
        return fastapi.responses.PlainTextResponse(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            content='Invalid notification recipient\n\n'
                    'The submission service is mis-configured!\n'
        )
    headers = {}
    if location is not None:
        headers['Location'] = location
    try:
        send_notification(
            content_type=content_type,
            encoding=encoding,
            data=data,
            recipient=recipient,
            intro_message=intro_message,
            cfg=cfg,
        )
        return fastapi.responses.JSONResponse(
            headers=headers,
            status_code=fastapi.status.HTTP_201_CREATED,
            content={
                'message': 'Notification sent successfully!',
            }
        )
    except Exception as e:
        print(traceback.format_exc())
        return fastapi.responses.PlainTextResponse(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=f'Could not send the notification ({type(e).__name__}).\n\n'
                    f'{str(e)}.\n'
        )


@app.on_event("startup")
async def app_init():
    global cfg
    init_default_logging()
    config_file = os.getenv(ENV_CONFIG, DEFAULT_CONFIG)
    try:
        with pathlib.Path(config_file).open() as fp:
            cfg = cfg_parser.parse_file(fp=fp)
        init_config_logging(config=cfg)
    except Exception as e:
        print(traceback.format_exc())
        LOG.warn(f'Failed to load config: {config_file}')
        LOG.warn(str(e))
    LOG.info(f'Loaded config: {config_file}')
