from asyncio import gather, get_event_loop

import discord

from streambot.logging import logger
from streambot.discord import managed_client
from streambot.db import Reservation, Stream

client: discord.Client = None


async def _clear_stale_streams(stream: Stream):
    guild = await client.fetch_guild(stream.reservation.guild_id)
    try:
        channel = await guild.fetch_channel(stream.reservation.channel_id)
    except Exception as e:
        logger.error(e)

    try:
        await channel.fetch_message(stream.message_id)
    except Exception:
        stream.delete_instance()


async def _run():
    global client

    async with managed_client() as dc:
        client = dc
        await gather(*[_clear_stale_streams(s) for s in Stream.select().prefetch(Reservation)])
        client = None


def task():
    loop = get_event_loop()
    loop.run_until_complete(_run())
