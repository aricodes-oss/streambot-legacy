import discord
from contextlib import asynccontextmanager
from .constants import AUTH_TOKEN

intents = discord.Intents.all()
intents.presences = True
intents.members = True
cache_flags = discord.MemberCacheFlags.all()

client: discord.Client = discord.Client(intents=intents, member_cache_flags=cache_flags)


@asynccontextmanager
async def managed_client():
    dc: discord.Client = discord.Client(intents=intents)
    await dc.login(AUTH_TOKEN)
    try:
        yield dc
    finally:
        await dc.close()
