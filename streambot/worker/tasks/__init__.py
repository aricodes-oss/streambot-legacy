import asyncio

from streambot.celery import app
from streambot.twitch import get_streams
from streambot.db import Reservation

from . import (
    update_active_streams,
    clear_unknown_messages,
    clear_stale_streams,
    update_presence_streams,
)

_imported = [
    update_active_streams,
    clear_unknown_messages,
    clear_stale_streams,
    update_presence_streams,
]

for f in _imported:
    app.task(f.task)


@app.task
def update_game(game_id):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_streams(game_id, bypass_cache=True))


@app.task
def update_cached_streams():
    for reservation in Reservation.select():
        update_game.delay(reservation.game_id)
