from .base import BaseModel
from peewee import CharField, IntegerField, ForeignKeyField

from .reservation import Reservation


class Stream(BaseModel):
    reservation = ForeignKeyField(Reservation, backref="streams")
    username = CharField()
    message_id = IntegerField()
