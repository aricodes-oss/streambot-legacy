from .base import BaseModel

from peewee import CharField, IntegerField, BooleanField


class Reservation(BaseModel):
    guild_id = IntegerField()
    channel_id = IntegerField()
    game_id = CharField()
    strikes = IntegerField(default=0)
    speedrun_only = BooleanField(default=False)
