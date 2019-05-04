
# -*- coding: utf-8 -*-

"""
自然语言处理
"""

import re
import sys
import math
import time
import base64
import json
from urllib.parse import urlencode
from urllib.parse import quote
from urllib.parse import urlparse

from .aio_base import AipBase


class AipNlp(AipBase):

    """
    自然语言处理
    """

    __lexerUrl = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer'

    __lexerCustomUrl = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer_custom'

    __depParserUrl = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/depparser'

    __wordEmbeddingUrl = 'https://aip.baidubce.com/rpc/2.0/nlp/v2/word_emb_vec'

    __dnnlmCnUrl = 'https://aip.baidubce.com/rpc/2.0/nlp/v2/dnnlm_cn'

    __wordSimEmbeddingUrl = 'https://aip.baidubce.com/rpc/2.0/nlp/v2/word_emb_sim'

    __simnetUrl = 'https://aip.baidubce.com/rpc/2.0/nlp/v2/simnet'

    __commentTagUrl = 'https://aip.baidubce.com/rpc/2.0/nlp/v2/comment_tag'

    __sentimentClassifyUrl = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify'

    def _proccessResult(self, content):
        """
            formate result
        """
        
        return json.loads(str(content, 'gbk')) or {}

    def _proccessRequest(self, url, params, data, headers):
        """
            _proccessRequest
        """

        return json.dumps(data, ensure_ascii=False).encode('gbk')
    
    async def lexer(self, text, options=None):
        """
            词法分析
        """
        options = options or {}

        data = {}
        data['text'] = text

        data.update(options)

        return await self._request(self.__lexerUrl, data)
    
    async def lexerCustom(self, text, options=None):
        """
            词法分析（定制版）
        """
        options = options or {}

        data = {}
        data['text'] = text

        data.update(options)

        return await self._request(self.__lexerCustomUrl, data)
    
    async def depParser(self, text, options=None):
        """
            依存句法分析
        """
        options = options or {}

        data = {}
        data['text'] = text

        data.update(options)

        return await self._request(self.__depParserUrl, data)
    
    async def wordEmbedding(self, word, options=None):
        """
            词向量表示
        """
        options = options or {}

        data = {}
        data['word'] = word

        data.update(options)

        return await self._request(self.__wordEmbeddingUrl, data)
    
    async def dnnlm(self, text, options=None):
        """
            DNN语言模型
        """
        options = options or {}

        data = {}
        data['text'] = text

        data.update(options)

        return await self._request(self.__dnnlmCnUrl, data)
    
    async def wordSimEmbedding(self, word_1, word_2, options=None):
        """
            词义相似度
        """
        options = options or {}

        data = {}
        data['word_1'] = word_1
        data['word_2'] = word_2

        data.update(options)

        return await self._request(self.__wordSimEmbeddingUrl, data)
    
    async def simnet(self, text_1, text_2, options=None):
        """
            短文本相似度
        """
        options = options or {}

        data = {}
        data['text_1'] = text_1
        data['text_2'] = text_2

        data.update(options)

        return await self._request(self.__simnetUrl, data)
    
    async def commentTag(self, text, options=None):
        """
            评论观点抽取
        """
        options = options or {}

        data = {}
        data['text'] = text

        data.update(options)

        return await self._request(self.__commentTagUrl, data)
    
    async def sentimentClassify(self, text, options=None):
        """
            情感倾向分析
        """
        options = options or {}

        data = {}
        data['text'] = text

        data.update(options)

        return await self._request(self.__sentimentClassifyUrl, data)
    