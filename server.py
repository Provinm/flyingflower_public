#-*- coding:utf-8 -*-

import logging
import asyncio

from dotenv import load_dotenv
load_dotenv()

from sanic import Sanic

from flyingflower.views import asr_view, tts_view, pivot_view, tts_speech_view
from flyingflower.settings import EBROSE_LOGGER_CONFIG
from flyingflower.cache_build import CacheBuilder

# 设置 log 
logging.config.dictConfig(EBROSE_LOGGER_CONFIG)

app = Sanic()
app.add_route(asr_view, '/ebrose/asr', methods=["POST"])
app.add_route(tts_view, '/ebrose/tts', methods=["POST"])
app.add_route(pivot_view, '/ebrose/pivot', methods=["GET"])
app.add_route(tts_speech_view, "/ebrose/speech", methods=["GET"])


# 启动定时任务
cachebuilder = CacheBuilder()
asyncio.ensure_future(cachebuilder.runner())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8000")