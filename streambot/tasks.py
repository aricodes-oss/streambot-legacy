import asyncio

from .celery import app
from .twitch import get_streams
from .db import Reservation


@app.task
def update_game(game_id):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_streams(game_id, bypass_cache=True))


@app.task
def update_cached_streams():
    for reservation in Reservation.select():
        update_game.delay(reservation.game_id)
