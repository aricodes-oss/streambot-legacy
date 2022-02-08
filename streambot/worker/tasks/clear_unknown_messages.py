from asyncio import gather, get_event_loop

import discord

from streambot.logging import logger
from streambot.discord import managed_client
from streambot.db import Reservation, Stream

client: discord.Client = None


async def _clear_channel(reservation: Reservation):
    guild = await client.fetch_guild(reservation.guild_id)
    try:
        channel = await guild.fetch_channel(reservation.channel_id)
    except Exception as e:
        logger.error(e)
        return

    known_message_ids = {s.message_id for s in Stream.select()}

    async for message in channel.history(limit=200):
        # Only delete our own messages
        if message.author != client.user:
            continue

        if message.id not in known_message_ids:
            logger.debug(f"Deleting {message.id}")
            await message.delete()


async def _run():
    global client

    async with managed_client() as dc:
        client = dc
        await gather(*[_clear_channel(r) for r in Reservation.select().prefetch(Stream)])
        client = None


def task():
    loop = get_event_loop()
    loop.run_until_complete(_run())
