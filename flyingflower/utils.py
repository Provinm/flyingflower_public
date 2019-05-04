# -*- coding:utf-8 -*-
import logging
import re
import base64
from uuid import uuid4
from io import BytesIO
from typing import Any

import msgpack
from pydub import AudioSegment

from .settings import APP_ID, API_KEY, SECRETE_KEY
from .aip.aio_speech import AipSpeech

_Logger = logging.getLogger()
AipClient = AipSpeech(APP_ID, API_KEY, SECRETE_KEY)
CHINESE_RE_PAT = re.compile(r"[\u4e00-\u9fa5]")


def pack(obj: Any):

    return msgpack.packb(obj, use_bin_type=True)


def unpack(obj: Any):

    return msgpack.unpackb(obj, raw=False)


async def aip_tts(text: str):
    voice_option = {
        "vol": 5,
        "per": 4,
        "spd": 4,
    }
    synthesis_audio = await AipClient.synthesis(text, options=voice_option)
    return synthesis_audio


async def aip_asr(audio_bytes):
    audio_bytes_io = BytesIO(audio_bytes.body)
    audio_bytes = AudioSegment.from_mp3(audio_bytes_io)._data
    res = await AipClient.asr(audio_bytes) or {}
    return res


def split_sentence(sentence, pivot):
    '''把识别的整句分开
    '''
    # 用 逗号 分离句子
    sentences = sentence.split("，")
    for s in sentences:
        if pivot in s:
            # 仅留下中文
            s = "".join(list(re.findall(CHINESE_RE_PAT, s)))
            return s

    return ""