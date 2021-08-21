from peewee import Model

from . import connection


class BaseModel(Model):
    class Meta:
        database = connection
