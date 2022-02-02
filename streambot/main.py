from discord.ext import tasks
from .logging import logger

from . import env, subscribe, unsubscribe, worker
from .discord import client


def _t(w):
    return w.replace("!", "!d") if env.bool("DEBUG", default=False) else w


SUBSCRIBE = _t("!subscribe")
UNSUBSCRIBE = _t("!unsubscribe")
SPEEDRUN = _t("!speedrun")

TRIGGERS = [SUBSCRIBE, UNSUBSCRIBE, SPEEDRUN]


@tasks.loop(seconds=30, reconnect=True)
async def work():
    try:
        await worker.work()
    except Exception as e:
        logger.error(e)


@client.event
async def on_ready():
    logger.info(f"Logged in as {client.user}")
    logger.info("Ret-2-Go!")

    if not work.is_running():
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

    await {
        SUBSCRIBE: subscribe.handle,
        SPEEDRUN: subscribe.handle,
        UNSUBSCRIBE: unsubscribe.handle,
    }[command](message, game_name, speedrun_only=command == SPEEDRUN)


def main():
    logger.info("Connecting...")
    client.run(env("DISCORD_BOT_TOKEN"))
