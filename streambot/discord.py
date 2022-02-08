import discord
from contextlib import asynccontextmanager
from .constants import AUTH_TOKEN

client: discord.Client = discord.Client()


@asynccontextmanager
async def managed_client():
    dc: discord.Client = discord.Client()
    await dc.login(AUTH_TOKEN)

    try:
        yield dc
    finally:
        await dc.close()
