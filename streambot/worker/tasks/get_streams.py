from streambot.constants import SPEEDRUN_TAG_ID
from streambot.db import TwitchStream, Reservation, connection as db
from streambot.discord import managed_client
from streambot.twitch import get_streams

import asyncio
import discord


def _stream_to_instance(stream, game_id: str) -> TwitchStream:
    res: TwitchStream = TwitchStream(
        username=stream["user_login"],
        game_id=game_id,
        thumbnail_url=stream["thumbnail_url"],
        description=stream["title"],
    )
    if stream["tag_ids"] is not None and SPEEDRUN_TAG_ID in stream["tag_ids"]:
        res.is_speedrun = True

    return res


async def _pull(game_id: str, client: discord.Client) -> None:
    live_streams = await get_streams(game_id)
    unsaved_instances = [_stream_to_instance(stream, game_id) for stream in live_streams]

    # Fetch the list of entries to delete ahead of time and make sure
    # the new ones are inserted first to avoid a race condition
    old_stream_ids = [
        t.id for t in TwitchStream.select().where(TwitchStream.game_id == game_id)
    ]

    with db.atomic("EXCLUSIVE"):
        TwitchStream.bulk_create(unsaved_instances)
        q = TwitchStream.delete().where(TwitchStream.id.in_(old_stream_ids))
        q.execute()


async def _run() -> None:
    async with managed_client() as client:
        tasks = []
        # Deduplicate game_ids to avoid unnecessary database operations
        game_ids = {reservation.game_id for reservation in Reservation.select()}

        for game_id in game_ids:
            tasks.append(_pull(game_id, client))

        await asyncio.gather(*tasks)


def task() -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_run())
