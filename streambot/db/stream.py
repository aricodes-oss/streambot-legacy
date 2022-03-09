from .base import BaseModel
from peewee import CharField, IntegerField, ForeignKeyField

from .reservation import Reservation, MemberReservation


class Stream(BaseModel):
    reservation = ForeignKeyField(Reservation, backref="streams")
    username = CharField()
    message_id = IntegerField()


class MemberStream(BaseModel):
    reservation = ForeignKeyField(MemberReservation, backref="streams")
    member_id = IntegerField()
    message_id = IntegerField()
