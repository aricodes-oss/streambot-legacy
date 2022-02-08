from contextlib import suppress
import asyncio
import discord

from streambot import twitch

from streambot.logging import logger
from streambot.constants import SPEEDRUN_TAG_ID
from streambot.discord import managed_client
from streambot.db import Stream, Reservation

from discord import Embed, Object

client: discord.Client = None


def _embed(stream):
    result = Embed(
        title=stream["user_name"],
        description=stream["title"],
        url=f"https://twitch.tv/{stream['user_login']}",
        color=0x0099FF,
    )

    thumbnail_url = stream["thumbnail_url"].replace("{width}", "72").replace("{height}", "72")
    result.set_thumbnail(url=thumbnail_url)

    return result


async def _update(reservation):
    guild = await client.fetch_guild(reservation.guild_id)
    try:
        channel = await guild.fetch_channel(reservation.channel_id)
    except Exception as e:
        logger.warning(e)
        # Channel no longer exists maybe
        if reservation.strikes >= 5:
            reservation.delete_instance()
        else:
            reservation.strikes += 1
            reservation.save()
        return

    live_streams = await twitch.get_streams(reservation.game_id, require_cache=True)
    if live_streams is None:  # Cache miss
        logger.debug(f"No streams for {reservation.game_id}, skipping")
        return

    if reservation.speedrun_only:
        live_streams = [
            s
            for s in live_streams
            if s["tag_ids"] is not None and SPEEDRUN_TAG_ID in s["tag_ids"]
        ]

    live_usernames = {s["user_login"] for s in live_streams}
    known_usernames = {s.username for s in reservation.streams}

    with suppress(Exception):
        # Remove old streams
        messages_to_delete = [
            Object(id=stream.message_id)
            for stream in reservation.streams
            if stream.username not in live_usernames
        ]
        if len(messages_to_delete) > 0:
            await channel.delete_messages(messages_to_delete)

    try:
        for stream in reservation.streams:
            if stream.username not in live_usernames:
                stream.delete_instance()
    except Exception as e:
        logger.error(e)

    # Add new ones
    new_streams = [
        stream for stream in live_streams if stream["user_login"] not in known_usernames
    ]

    for stream in new_streams:
        # See previous note about potentially needing mid-refresh
        if stream["user_login"] in known_usernames:
            continue

        # We can always add more streams later
        if client.is_ws_ratelimited():
            return

        message = await channel.send(embed=_embed(stream))

        try:
            Stream.create(
                reservation=reservation,
                username=stream["user_login"],
                message_id=message.id,
            )
        except Exception:
            await message.delete()


async def _run():
    global client

    async with managed_client() as dc:
        client = dc
        tasks = []
        for reservation in Reservation.select().prefetch(Stream):
            tasks.append(_update(reservation))

        await asyncio.gather(*tasks)
    client = None


def task():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_run())
