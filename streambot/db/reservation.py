from .base import BaseModel

from peewee import CharField, IntegerField


class Reservation(BaseModel):
    guild_id = IntegerField()
    channel_id = IntegerField()
    game_id = CharField()
    strikes = IntegerField(default=0)
