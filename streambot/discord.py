import discord
from contextlib import asynccontextmanager
from .constants import AUTH_TOKEN

intents = discord.Intents.default()
intents.presences = True
intents.members = True

client: discord.Client = discord.Client(intents=intents)


@asynccontextmanager
async def managed_client():
    dc: discord.Client = discord.Client(intents=intents)
    await dc.login(AUTH_TOKEN)

    try:
        yield dc
    finally:
        await dc.close()
