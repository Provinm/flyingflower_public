#-*- coding:utf-8 -*-
from logging import getLogger
import traceback
import random
import re

from sanic.log import logger as _Logger
from sanic import response
from sanic.request import Request

from .decorators import check_token, set_token
from .utils import aip_asr, aip_tts, split_sentence
from .db_manager import get_sentence_by_text, get_sentence_by_id, get_poetry_by_id
from .cache_manager import set_user_cache, get_pivot_cache

_Logger = getLogger(__name__)


class Ret:
    # success code -> 0xx 
    # err code
    #   1xx session 
    #   2xx asr 
    #   3xx tts
    SUCCESS_CODE = 0
    EMPTY_ASR_AUDIO = 201
    BAIDU_ASR_ERR = 202
    INVALID_PIVOT_ERR = 101
    UNLOGIN_ERR = 102
    FAIL_NOT_VALID_SENTENCE = 103
    FAIL_REPEATED = 104
    FAIL_LOSE = 105
    FAIL_PARAMS_ERROR = 106
    SYS_AUDIO_ERR = 301
    UNHANDLED_ERR = 400


@check_token
async def asr_view(request, user_cache):
    # 解包相关信息，供之后逻辑调用`
    token, pivot = user_cache["token"], user_cache["pivot"]
    processed_id = user_cache["processed"]

    audio_bytes = request.files.get("file")
    _Logger.info(f"get audio_bytes = {audio_bytes}")
    if not audio_bytes:
        _Logger.debug("empty audio bytes")
        return response.json(
            {
                "status": False,
                "msg": "音频为空",
                "ret": Ret.EMPTY_ASR_AUDIO
            }
        )

    res = await aip_asr(audio_bytes)

    # 请求失败
    if not res or res.get("err_no") == 2000:
        _Logger.warning("err happened when processing baidu asr")
        return response.json(
            {
                "status": False,
                "msg": "请求百度 asr 失败",
                "ret": Ret.BAIDU_ASR_ERR
            }
        )

    #　请求成功
    asr_res = res.get("result") or [""]
    sentence = asr_res[0]

    _Logger.debug(f"successfully processed baidu asr res = {res}")
    if not sentence:
        return response.json(
            {
                "status": False,
                "msg": "语音内容为空",
                "ret": Ret.EMPTY_ASR_AUDIO
            }
        )

    sentence = split_sentence(sentence, pivot)
    _Logger.debug(f"get baidu asr sentence = {sentence}")
    if not sentence:
        resp = {"msg":f"需要说含有{pivot}的诗句哦", 
                "ret": Ret.FAIL_NOT_VALID_SENTENCE, 
                "status": False}

        return response.json(resp)

    result = await get_sentence_by_text(sentence)
    _Logger.debug(f"mysql search result = {result}")
    if not result:
        resp = {"msg":"没听过这句诗哦", 
                "ret": Ret.FAIL_NOT_VALID_SENTENCE, 
                "status": False}

        return response.json(resp)

    sent_id, poetry_id, _ = result
    sent_id = int(sent_id)
    if sent_id in processed_id:
        resp = {
            "msg": "这句已经说过了",
            "ret": Ret.FAIL_REPEATED,
            "status": False
        }
        return response.json(resp)

    user_cache["processed"].append(sent_id)
    user_cache["count"] += 1
    await set_user_cache(token, user_cache)
    author, title, poetry_text = await get_poetry_by_id(poetry_id)
    _Logger.debug(f"get poetry from sql text = {poetry_text}, author = {author}, {title}")
    return response.json(
        {
            "status": True,
            "ret": Ret.SUCCESS_CODE,
            "data": {
                "author": author,
                "title": title,
                "text": poetry_text
            }
        }
    )


@check_token
async def tts_speech_view(request: Request, user_cache: dict):

    # 解包相关信息，供之后逻辑调用
    sentence = request.args.get("sentence")

    if not sentence:
        return response.json({
            "msg": "句子为空",
            "status": False,
            "ret": Ret.FAIL_NOT_VALID_SENTENCE
        })
    
    synthesis_audio = await aip_tts(sentence)
    # 返回错误
    if isinstance(synthesis_audio, dict):
        return response.json(
            {
                "msg": "语音合成错误",
                "ret": Ret.SYS_AUDIO_ERR,
                "status": False
            }
        )
    # 发送二进制文件到小程序
    return response.raw(synthesis_audio)


@check_token
async def tts_view(request: Request, user_cache: dict):

    # 解包相关信息，供之后逻辑调用
    token, pivot = user_cache["token"], user_cache["pivot"]
    processed_id = user_cache["processed"]
    _Logger.debug(f"tts view token = {token} processed_id = {processed_id}")
    # 获取当前的缓存中的关于 pivot 的诗句
    sent_ids = await get_pivot_cache(pivot)
    sent_ids = [int(i) for i in sent_ids]
    random.shuffle(sent_ids)
    ans_id = None
    for _id in sent_ids:
        if _id not in processed_id:
            ans_id = _id
            break

    if not ans_id:
        return response.json(
            {
                "status": False,
                "ret": Ret.FAIL_LOSE,
                "msg": "当前刷新的id已经全部在 processed id 中"
            }
        )

    _id, poetry_id, _ = await get_sentence_by_id(ans_id)

    user_cache["processed"].append(_id)
    await set_user_cache(token, user_cache)

    author, title, poetry_text = await get_poetry_by_id(poetry_id)
    _Logger.debug(f"get poetry from sql text = {poetry_text}, author = {author}, {title}")
    return response.json(
        {
            "status": True,
            "ret": Ret.SUCCESS_CODE,
            "data": {
                "author": author,
                "title": title,
                "text": poetry_text
            }
        }
    )


@set_token
async def pivot_view(request: Request, user_cache:dict):
    _Logger.info("in pivot")
    new_token = user_cache["token"]
    return response.json({
        "token": new_token,
        "msg": "记录成功",
        "ret": Ret.SUCCESS_CODE,
        "status": True
    })
