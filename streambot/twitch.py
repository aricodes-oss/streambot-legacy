from . import env
from .cache import cached
from .logging import logger

import aiohttp


@cached(ttl=30)
async def _get_token():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": env("TWITCH_CLIENT_ID"),
                "client_secret": env("TWITCH_CLIENT_SECRET"),
                "grant_type": "client_credentials",
            },
        ) as res:
            return (await res.json())["access_token"]


async def _headers():
    return {
        "Authorization": f"Bearer {await _get_token()}",
        "Client-Id": env("TWITCH_CLIENT_ID"),
    }


@cached(ttl=120)
async def get_game(name):
    params = {"name": name}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.twitch.tv/helix/games",
            params=params,
            headers=await _headers(),
        ) as res:
            json = await res.json()

            if json is None:
                return []

            return json.get("data")


# Let multiple discords share the same stream pool
# to avoid API rate limiting
@cached(ttl=30)
async def get_streams(game_id, cursor=None):
    params = {"game_id": game_id, "first": "100"}

    if cursor is not None:
        params["after"] = cursor

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.twitch.tv/helix/streams",
            params=params,
            headers=await _headers(),
        ) as res:
            json = await res.json()

            data = json.get("data")
            new_cursor = json.get("pagination").get("cursor")

            if new_cursor is not None:
                logger.debug(f"Pagination triggered, fetching more for {game_id}")
                return data + await get_streams(game_id, cursor=new_cursor)

            return data
