from fastapi import Request
from redis.asyncio.client import Redis


async def get_redis(request: Request) -> Redis:
    return request.app.state.redis
