from aiocache import Cache
from typing import Callable

cache = Cache(Cache.REDIS, endpoint="cache", port=6379)


def cached(ttl: int = 30):
    def decorator_cached(func: Callable):
        async def wrapped_func(*args, **kwargs):
            key: str = func.__name__ + str(args) + str(kwargs)
            cached_value: str = await cache.get(key)

            if cached_value is not None:
                return cached_value

            result = await func(*args, **kwargs)
            await cache.set(key, result, ttl=ttl)

            return result

        return wrapped_func

    return decorator_cached
