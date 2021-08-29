import asyncio

from streambot import env
from streambot.db import Reservation, Stream
from streambot.discord import client

from discord import Object


async def _work():
    await client.login(env("DISCORD_BOT_TOKEN"))
    for reservation in Reservation.select().prefetch(Stream):
        try:
            guild = client.get_guild(reservation.guild_id)
            channel = guild.get_channel(reservation.channel_id)

            messages_to_delete = [
                Object(id=stream.message_id) for stream in reservation.streams
            ]

            if len(messages_to_delete) > 0:
                await channel.delete_messages(messages_to_delete)

            print(f"Deleted {len(messages_to_delete)} messages")
        except Exception as e:
            print(e)

        for stream in reservation.streams:
            stream.delete_instance()
        print("Deleted all stream instances")


def main():
    asyncio.run(_work())
