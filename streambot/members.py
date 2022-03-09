from asyncio import sleep

from .db import MemberReservation
from .logging import logger


async def handle(message):
    confirmation_message = await message.channel.send("Sure! One moment.")
    guild_id = message.guild.id
    channel_id = message.channel.id

    try:
        MemberReservation.get(guild_id=guild_id, channel_id=channel_id)
        await message.channel.send("This channel is already subscribed to member streams!")

        return
    except Exception:
        pass

    logger.info(f"Creating member reservation for guild {guild_id}/channel {channel_id}")
    MemberReservation.create(guild_id=guild_id, channel_id=channel_id)

    subscribed_message = await message.channel.send(
        "Subscribed! These messages will be deleted in 5 seconds.",
    )

    await sleep(5)
    await confirmation_message.delete()
    await subscribed_message.delete()
    await message.delete()
