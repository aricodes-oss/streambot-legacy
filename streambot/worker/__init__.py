from contextlib import suppress

from .tasks import tasks


async def work():
    for task in tasks:
        with suppress(Exception):
            await task.run()
