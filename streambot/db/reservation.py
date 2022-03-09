from .base import BaseModel

from peewee import CharField, IntegerField, BooleanField


class BaseReservation(BaseModel):
    guild_id = IntegerField()
    channel_id = IntegerField()
    strikes = IntegerField(default=0)


class Reservation(BaseReservation):
    game_id = CharField()
    speedrun_only = BooleanField(default=False)


class MemberReservation(BaseReservation):
    pass
