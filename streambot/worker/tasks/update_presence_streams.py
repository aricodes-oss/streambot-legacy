import asyncio
import discord

from contextlib import suppress

from streambot.discord import managed_client
from streambot.db import MemberReservation, MemberStream
from streambot.logging import logger

from discord import Embed, Object

from typing import Optional

client: discord.Client = None


def _embed(member):
    activity = _streaming_activity(member)

    name = member.nick
    if name is None:
        name = member.name

    result = Embed(
        title=name,
        description=activity.name,
        url=activity.url,
        color=0x0099FF,
    )

    return result


def _streaming_activity(member) -> Optional[discord.Activity]:
    for activity in member.activities:
        if activity is None:
            continue

        if activity.type == discord.ActivityType.streaming:
            return activity

    return None


def _is_streaming(member) -> bool:
    return _streaming_activity(member) is not None


async def _update(reservation):
    guild = await client.fetch_guild(reservation.guild_id)
    try:
        channel = await client.fetch_channel(reservation.channel_id)
        reservation.strikes = 0
        reservation.save()
    except Exception as e:
        logger.warning(e)
        # Channel no longer exists maybe
        if reservation.strikes >= 150:
            reservation.delete_instance()
        else:
            reservation.strikes += 1
            reservation.save()
        return

    all_members = await guild.fetch_members(limit=None).flatten()
    for member in all_members:
        logger.info(member.activity)
    known_user_ids = {s.member_id for s in reservation.streams}
    live_members = [m for m in all_members if _is_streaming(m)]
    live_ids = [m.id for m in live_members]

    messages_to_delete = [
        Object(id=stream.message_id)
        for stream in reservation.streams
        if stream.member_id not in live_ids
    ]

    with suppress(Exception):
        if len(messages_to_delete) > 0:
            await channel.delete_messages(messages_to_delete)

    new_streaming_members = [m for m in live_members if m.id not in known_user_ids]

    for member in new_streaming_members:
        message = await channel.send(embed=_embed(member))

        try:
            MemberStream.create(
                reservation=reservation,
                member_id=member.id,
                message_id=message.id,
            )
        except Exception:
            await message.delete()


async def _run():
    global client

    async with managed_client() as dc:
        client = dc
        tasks = []

        for reservation in MemberReservation.select().prefetch(MemberStream):
            tasks.append(_update(reservation))

        await asyncio.gather(*tasks)

    client = None


def task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_run())
