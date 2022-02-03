from asyncio import gather

from streambot.discord import client
from streambot.db import Reservation, Stream


async def clear_channel(reservation: Reservation):
    guild = client.get_guild(reservation.guild_id)
    try:
        channel = guild.get_channel(reservation.channel_id)
    except Exception:
        return

    known_message_ids = {s.message_id for s in Stream.select()}

    async for message in channel.history(limit=200):
        # Only delete our own messages
        if message.author != client.user:
            continue

        if message.id not in known_message_ids:
            await message.delete()


async def run():
    await gather(*[clear_channel(r) for r in Reservation.select().prefetch(Stream)])
