from asyncio import create_task, run

from . import twitch

from .discord import client
from .db import Reservation, Stream

from discord import Embed, Object


def _embed(stream):
    result = Embed(
        title=stream["user_name"],
        description=stream["title"],
        url=f"https://twitch.tv/{stream['user_name']}",
        color=0x0099FF,
    )

    thumbnail_url = stream["thumbnail_url"].replace("{width}", "72").replace("{height}", "72")
    result.set_thumbnail(url=thumbnail_url)

    return result


async def _update(reservation):
    guild = client.get_guild(reservation.guild_id)
    channel = guild.get_channel(reservation.channel_id)

    live_streams = await twitch.get_streams(reservation.game_id)

    live_usernames = {s["user_login"] for s in live_streams}
    known_usernames = {s.username for s in reservation.streams}

    try:
        # Remove old streams
        messages_to_delete = [
            Object(id=stream.message_id)
            for stream in reservation.streams
            if stream.username not in live_usernames
        ]
        if len(messages_to_delete) > 0:
            await channel.delete_messages(messages_to_delete)

        Stream.delete().where(Stream.message_id << [m.id for m in messages_to_delete])
    except Exception:
        await channel.send(
            "Unable to delete existing streams! Please give me permissions to manage this"
            " channel to suppress this message.",
        )

    # Add new ones
    new_streams = [
        stream for stream in live_streams if stream["user_login"] not in known_usernames
    ]

    for stream in new_streams:
        message = await channel.send(embed=_embed(stream))
        Stream.create(
            reservation=reservation,
            username=stream["user_login"],
            message_id=message.id,
        )


async def work():
    for reservation in Reservation.select().prefetch(Stream):
        await _update(reservation)
