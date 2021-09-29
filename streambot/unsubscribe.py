from contextlib import suppress
from discord import Object

from . import twitch
from .db import Reservation, Stream


async def handle(message, game_name):
    guild_id = message.guild.id
    channel_id = message.channel.id
    available_games = await twitch.get_game(game_name)

    if len(available_games) != 1:
        await message.channel.send(
            f"I couldn't find a match for {game_name} - maybe you spelled it differently from"
            " Twitch?",
        )
        return

    try:
        game_id = available_games[0]["id"]
        res = Reservation.get(
            guild_id=guild_id,
            channel_id=channel_id,
            game_id=game_id,
        )
    except Exception:
        await message.channel.send(f"This channel is not subscribed to {game_name} streams.")
        return

    with suppress(Exception):
        message_ids = [
            Object(id=stream.message_id)
            for stream in Stream.select().where(Stream.reservation == res)
        ]
        await message.channel.delete_messages(message_ids)

    with suppress(Exception):
        for stream in res.streams:
            stream.delete_instance()
        res.delete_instance()

    await message.channel.send("Unsubscribed!")
