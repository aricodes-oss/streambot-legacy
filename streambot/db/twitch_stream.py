from .base import BaseModel
from peewee import CharField, BooleanField


class TwitchStream(BaseModel):
    username = CharField()
    game_id = CharField()
    description = CharField()
    thumbnail_url = CharField()
    is_speedrun = BooleanField(default=False)
