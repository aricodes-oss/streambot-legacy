import environ
from . import celery  # noqa

env = environ.Env()
environ.Env.read_env()

__version__ = "0.1.0"
