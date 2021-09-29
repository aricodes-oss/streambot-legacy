from contextlib import suppress

from discord.ext import tasks

from . import env, subscribe, unsubscribe, worker
from .discord import client


SUBSCRIBE = "!ssubscribe"
UNSUBSCRIBE = "!unsubscribe"

TRIGGERS = [SUBSCRIBE, UNSUBSCRIBE]


@tasks.loop(seconds=5)
async def work():
    with suppress(Exception):
        await worker.work()


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    print("Ret-2-Go!")

    work.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    command = None

    for trigger in TRIGGERS:
        if message.content.lower().startswith(trigger):
            command = trigger
            break

    if command is None:
        return

    # Vet permissions
    if not message.author.guild_permissions.administrator:
        await message.channel.send("You lack the permissions to do this")

    # Get the name of the game they want
    game_name = message.content[len(command) + 1 :]
    if len(game_name) < 1:
        await message.channel.send("Please specify a game name!")
        return

    await {SUBSCRIBE: subscribe.handle, UNSUBSCRIBE: unsubscribe.handle}[command](
        message,
        game_name,
    )


def main():
    print("Connecting...")
    client.run(env("DISCORD_BOT_TOKEN"))
