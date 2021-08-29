from streambot.db import Reservation, Stream
from streambot.discord import client

from discord import Object

from contextlib import suppress


async def main():
    for reservation in Reservation.select().prefetch(Stream):
        with suppress(Exception):
            guild = client.get_guild(reservation.guild_id)
            channel = guild.get_channel(reservation.channel_id)

            messages_to_delete = [
                Object(id=stream.message_id) for stream in reservation.streams
            ]

            if len(messages_to_delete) > 0:
                await channel.delete_messages(messages_to_delete)

            print(f"Deleted {len(messages_to_delete)} messages")

        for stream in reservation.streams:
            stream.delete_instance()
        print("Deleted all stream instances")
