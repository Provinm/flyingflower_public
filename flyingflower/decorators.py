# -*- coding:utf-8 -*-
import re
import logging
from functools import wraps
from uuid import uuid4

from sanic import response

from .cache_manager import set_user_cache, get_user_cache
from .settings import SELECTED_WORDS

CHINESE_RE_PAT = re.compile(r"[\u4e00-\u9fa5]")
_Logger = logging.getLogger()

def set_token(coro):
    @wraps(coro)
    async def wrapper(request, *args, **kw):
        pivot = request.args.get("pivot")
        if len(pivot) != 1 or (not re.match(CHINESE_RE_PAT, pivot)):
            return response.json(
                {
                    "status": False,
                    "msg": "主题词输入错误",
                }
            )
        if not pivot in SELECTED_WORDS:
            return response.json(
                {
                    "status": False,
                    "msg": "主题词仅包括{}".format(SELECTED_WORDS),
                }
            )

        new_token = str(uuid4())
        user_cache = {
            "token": new_token,
            "pivot": pivot,
            "processed": [],
            "count": 0
        }
        await set_user_cache(new_token, user_cache)
        return await coro(request, user_cache)
    return wrapper

def check_token(coro):
    @wraps(coro)
    async def wrapper(request, *args, **kw):

        token = request.args.get("token") or request.form.get("token")
        if not token:
            return response.json(
                {
                    "msg": "未找到该用户",
                    "status": False
                }
            )

        user_cache = await get_user_cache(token)
        _Logger.info(f"get user_cache = {user_cache}")
        if not user_cache:
            return response.json(
                {
                    "msg": "未找到该用户",
                    "status": False
                }
            )

        return await coro(request, user_cache, *args, **kw)
    return wrapper