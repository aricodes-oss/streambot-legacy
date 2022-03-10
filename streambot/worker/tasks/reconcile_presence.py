import discord
from streambot.db import MemberReservation, MemberStream
from streambot.discord import client
from streambot.logging import logger


def _embed(member):
    activity = None

    for a in member.activities:
        if activity.type == discord.ActivityType.streaming:
            activity = a

    name = member.nick
    if name is None:
        name = member.name

    result = discord.Embed(
        title=name,
        description=activity.name,
        url=activity.url,
        color=0x0099FF,
    )

    return result


async def reconcile_presence(member):
    is_streaming = False
    for activity in member.activities:
        if activity.type == discord.ActivityType.streaming:
            is_streaming = True
            break

    existing_messages = MemberStream.select().where(MemberStream.member_id == member.id)

    # If the user is not streaming, we want to clear any mention of that
    if not is_streaming:
        for message in existing_messages:
            reservation = message.reservation

            guild = await client.fetch_guild(reservation.guild_id)
            channel = await client.fetch_channel(reservation.channel_id)
            dmessage = await channel.fetch_message(message.message_id)

            await dmessage.delete()

        return
    logger.info("Made it past the status check")

    reservation = MemberReservation.get_or_none(
        MemberReservation.guild_id == member.guild.id,
    )

    if reservation is None:
        logger.info("No reservation, quitting")
        return

    guild = await client.fetch_guild(reservation.guild_id)
    channel = await client.fetch_channel(reservation.channel_id)

    message = await channel.send(embed=_embed(member))

    try:
        MemberStream.create(
            reservation=reservation,
            member_id=member.id,
            message_id=message.id,
        )
    except Exception:
        await message.delete()
