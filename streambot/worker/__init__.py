from contextlib import suppress
from asyncio import gather

from .tasks import tasks


async def work():
    with suppress(Exception):
        await gather(*[task.run() for task in tasks])
