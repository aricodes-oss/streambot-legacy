import aioredis
import msgpack
from typing import Callable

from streambot.logging import logger

cache = aioredis.from_url("redis://cache:6379")


def cached(ttl: int = 30):
    def decorator_cached(func: Callable):
        async def wrapped_func(*args, bypass_cache=False, require_cache=False, **kwargs):
            key: str = func.__name__ + str(args) + str(kwargs)
            cached_value: str = await cache.get(key)

            if not bypass_cache and cached_value is not None:
                parsed_value = msgpack.loads(cached_value)

                logger.debug(
                    "Cache hit for {}({}, {})".format(func.__name__, str(args), str(kwargs)),
                )
                logger.debug(f"Number of results: {len(parsed_value)}")
                if len(parsed_value) < 5:
                    logger.debug(f"Cached results: {parsed_value}")
                return parsed_value

            logger.debug(
                "Cache miss for {}({}, {})".format(func.__name__, str(args), str(kwargs)),
            )
            if require_cache:
                logger.debug("Cache required but missed")
                return None

            result = await func(*args, **kwargs)
            if result is not None:
                stored_result = msgpack.dumps(result)

                await cache.set(key, stored_result, ex=ttl)

            return result

        return wrapped_func

    return decorator_cached
