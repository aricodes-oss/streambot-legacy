import environ

import uvloop
from . import celery  # noqa

env = environ.Env()
environ.Env.read_env()
uvloop.install()

__version__ = "0.1.0"
