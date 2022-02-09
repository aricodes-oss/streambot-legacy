from asyncio import get_event_loop

import discord

from streambot.logging import logger
from streambot.celery import app
from streambot.discord import managed_client
from streambot.db import Reservation, Stream


async def _clear_stale_streams(stream: Stream, client: discord.Client):
    guild = await client.fetch_guild(stream.reservation.guild_id)
    try:
        channel = await guild.fetch_channel(stream.reservation.channel_id)
    except Exception as e:
        logger.error(e)

    try:
        await channel.fetch_message(stream.message_id)
    except Exception:
        stream.delete_instance()


async def _check(stream: Stream):
    async with managed_client() as dc:
        await _clear_stale_streams(stream, dc)


@app.task
def enqueue(stream: Stream):
    loop = get_event_loop()
    loop.run_until_complete(_check(stream))


# Since we're only running a single worker node, all of these tasks
# will be sharing time with all of the other ones and hopefully
# not using all of our ratelimit at once
def task():
    for stream in Stream.select().prefetch(Reservation):
        enqueue.delay(stream)
