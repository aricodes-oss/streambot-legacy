from asyncio import gather

from streambot.discord import client
from streambot.db import Reservation, Stream


async def clear_stale_streams(stream: Stream):
    guild = client.get_guild(stream.reservation.guild_id)
    try:
        channel = guild.get_channel(stream.reservation.channel_id)
    except Exception:
        return

    try:
        await channel.fetch_message(stream.message_id)
    except Exception:
        stream.delete_instance()


async def run():
    await gather(*[clear_stale_streams(s) for s in Stream.select().prefetch(Reservation)])
