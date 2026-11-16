"""
App configuration, contains no secrets - everything comes from the environment.

* Production (``MYSQL_HOST`` is set, see Docker/compose.yaml): MySQL and SMTP,
  every required variable must be set, otherwise the app refuses to start.
* Local development (``MYSQL_HOST`` not set): SQLite file in backend/instance/,
  no mail is sent. Values can be overridden in backend/.env (gitignored).
"""
import os
from urllib.parse import quote

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

PRODUCTION = bool(os.environ.get('MYSQL_HOST'))


def _env(name, dev_default=None):
    value = os.environ.get(name)
    if value:
        return value
    if PRODUCTION or dev_default is None:
        raise RuntimeError('environment variable {} is missing'.format(name))
    return dev_default


def _env_bool(name, default):
    return os.environ.get(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


class Config(object):
    SECRET_KEY = _env('SECRET_KEY', dev_default='geheim')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_ECHO = True
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'lars@tele-schocken.de')

    if PRODUCTION:
        # build the URI from single values and URL encode user/password (special characters)
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
            quote(_env('MYSQL_USER'), safe=''),
            quote(_env('MYSQL_PASSWORD'), safe=''),
            os.environ['MYSQL_HOST'],
            os.environ.get('MYSQL_PORT', '3306'),
            _env('MYSQL_DATABASE'))
        # reconnect after MySQL closed idle connections (wait_timeout)
        SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True, 'pool_recycle': 280}

        MAIL_SERVER = _env('MAIL_SERVER')
        MAIL_PORT = int(os.environ.get('MAIL_PORT', '465'))
        MAIL_USERNAME = _env('MAIL_USERNAME')
        MAIL_PASSWORD = _env('MAIL_PASSWORD')
        MAIL_USE_TLS = _env_bool('MAIL_USE_TLS', False)
        MAIL_USE_SSL = _env_bool('MAIL_USE_SSL', True)

        SESSION_COOKIE_SECURE = True
        SESSION_COOKIE_HTTPONLY = True
        # "None" is needed if the feedback form (CSRF) has to work inside an iframe on another site
        SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir, 'instance', 'teleschocken.sqlite')
        MAIL_SERVER = 'localhost'
        MAIL_PORT = 25
        MAIL_USE_TLS = False
        MAIL_USE_SSL = False
        # mails are only logged via signals, never sent
        MAIL_SUPPRESS_SEND = True
