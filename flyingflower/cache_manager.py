# -*- coding:utf-8 -*-
import logging
from typing import Any
import aioredis

from .settings import REDIS_HOST, REDIS_DB, REDIS_PORT
from .utils import pack, unpack

_Logger = logging.getLogger()
PREFIX_CACHE = "ebrose_"
POETRY_CACHE_KEY = "cache_build_key"

async def connect():

    redis_addr = f"redis://{REDIS_HOST}:{REDIS_PORT}"
    conn = await aioredis.create_redis_pool(redis_addr, db=int(REDIS_DB))
    return conn


cache = None


async def redis_set(key, value, expire=24*60*60):
    global cache
    if not cache:
        cache = await connect()

    value = pack(value)

    try:
        await cache.set(key, value, expire=expire)
    except Exception as err:
        _Logger.error(f"redis error when set {key} to {value}, err = {err}")
        return None
    return True


async def redis_get(key):
    global cache
    if not cache:
        cache = await connect()

    try:
        value = await cache.get(key)
    except Exception as err:
        _Logger.error(f"redis error when set {key} to {value}, err = {err}")
        return None

    return unpack(value)


async def set_user_cache(uid: str, value: Any, timeout=24*60*60):
    '''set user cache 

    struct:
        {
            "pivot": "花",
            "processed": [1,2,3]
            "count": 0,
            "token": "x"
        }
    '''
    key = "%s%s"%(PREFIX_CACHE, uid)
    return await redis_set(key, value, timeout)


async def get_user_cache(uid):

    key = "%s%s"%(PREFIX_CACHE, uid)
    return await redis_get(key)


async def get_pivot_cache(pivot):

    key = POETRY_CACHE_KEY
    all_cache = await redis_get(key)
    if pivot in all_cache:
        return all_cache[pivot]
    return []