import yaml

from typing import List

from .consts import DEFAULT_LOG_LEVEL, DEFAULT_LOG_FORMAT


class MissingConfigurationError(Exception):

    def __init__(self, missing: List[str]):
        self.missing = missing


class SecurityConfig:

    def __init__(self, enabled: bool, tokens: List[str]):
        self.enabled = enabled
        self.tokens = frozenset(tokens)


class LoggingConfig:

    def __init__(self, level, message_format: str):
        self.level = level
        self.format = message_format


class MailConfig:

    def __init__(self, name: str, email: str, host: str, port: int,
                 security: str, auth: bool, username: str, password: str):
        self.name = name
        self.email = email
        self.host = host
        self.port = port
        self.security = security.lower()
        self.auth = auth
        self.username = username
        self.password = password


class SubmitterConfig:

    def __init__(self, mail: MailConfig, security: SecurityConfig,
                 logging: LoggingConfig):
        self.mail = mail
        self.security = security
        self.logging = logging


class SubmitterConfigParser:

    DEFAULTS = {
        'mail': {
            'name': 'DSW Notifier',
            'email': '',
            'host': '',
            'port': 25,
            'security': 'plain',
            'authEnabled': True,
            'username': '',
            'password': '',
        },
        'security': {
            'enabled': False,
            'tokens': [],
        },
        'logging': {
            'level': DEFAULT_LOG_LEVEL,
            'format': DEFAULT_LOG_FORMAT,
        },
    }

    REQUIRED = [
        ['mail', 'email'],
        ['mail', 'host'],
        ['mail', 'port'],
        ['mail', 'security'],
        ['mail', 'authEnabled'],
    ]

    def __init__(self):
        self.cfg = dict()

    def has(self, *path):
        x = self.cfg
        for p in path:
            if not hasattr(x, 'keys') or p not in x.keys():
                return False
            x = x[p]
        return True

    def _get_default(self, *path):
        x = self.DEFAULTS
        for p in path:
            x = x[p]
        return x

    def get_or_default(self, *path):
        x = self.cfg
        for p in path:
            if not hasattr(x, 'keys') or p not in x.keys():
                return self._get_default(*path)
            x = x[p]
        return x

    def validate(self):
        missing = []
        for path in self.REQUIRED:
            if not self.has(*path):
                missing.append('.'.join(path))
        if len(missing) > 0:
            raise MissingConfigurationError(missing)

    @property
    def _mail(self):
        return MailConfig(
            name=self.get_or_default('mail', 'name'),
            email=self.get_or_default('mail', 'email'),
            host=self.get_or_default('mail', 'host'),
            port=self.get_or_default('mail', 'port'),
            security=self.get_or_default('mail', 'security'),
            auth=self.get_or_default('mail', 'authEnabled'),
            username=self.get_or_default('mail', 'username'),
            password=self.get_or_default('mail', 'password'),
        )

    @property
    def _security(self):
        return SecurityConfig(
            enabled=self.get_or_default('security', 'enabled'),
            tokens=self.get_or_default('security', 'tokens'),
        )

    @property
    def _logging(self):
        return LoggingConfig(
            level=self.get_or_default('logging', 'level'),
            message_format=self.get_or_default('logging', 'format'),
        )

    def parse_file(self, fp) -> SubmitterConfig:
        try:
            self.cfg = yaml.full_load(fp)
            self.validate()
            return self.config
        except KeyError as e:
            print(self.cfg)
            raise RuntimeError(f'Missing configuration: {e}')

    @property
    def config(self) -> SubmitterConfig:
        return SubmitterConfig(
            mail=self._mail,
            security=self._security,
            logging=self._logging,
        )


cfg_parser = SubmitterConfigParser()
