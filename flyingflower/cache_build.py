# -*- coding:utf-8 -*-
"""
By:JiangJinhe
Intro: 由于服务器性能问题，没有办法一次性将所有的数据加载进 redis，所以我们选择的策略是
每隔一定时间刷新一小部分诗句到 redis 中，存储的结构为

{
    "花": [1,2,34,57] # 令词以及对应的 poetry_id
    "月": [4,5,67,89]
}



"""
import asyncio
import re
import logging
import traceback
import time

import aioredis
import aiomysql

from .settings import MYSQL_DATABASE, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_USER
from .settings import SELECTED_WORDS, REDIS_DB, REDIS_HOST
from .utils import pack, unpack


_Logger = logging.getLogger()
POETRY_CACHE_KEY = "cache_build_key"
REFRESH_PERIOD = 1 * 60 * 60


# 设置redis缓存定时任务
class CacheBuilder():

    def __init__(self):
        words_list = "".join([i for i in SELECTED_WORDS if i])
        self.words = list(set(words_list))

    async def _mysql_conn(self):
        conn = await aiomysql.connect(
            host=MYSQL_HOST,
            port=int(MYSQL_PORT),
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            db=MYSQL_DATABASE
        )
        return conn

    async def _redis_conn(self):
        conn = await aioredis.create_redis(
            'redis://{}'.format(REDIS_HOST), db=int(REDIS_DB)
        )
        return conn

    # 1 将words表刷新如缓存 （仅挑选出一些）
    async def _get_table_word(self):
        """
        select * from word where text in ('春', '江');
        :return:
        """
        conn = await self._mysql_conn()
        sql = "select id, text from word where text in ({0})".format(
            ','.join([repr(i) for i in self.words]))

        cur = await conn.cursor()
        await cur.execute(sql)
        result = await cur.fetchall()
        await cur.close()
        conn.close()
        return result

    # 1 将words表刷新如缓存 （仅挑选出一些）
    async def _get_sentence_words_association(self, limit=1024):
        """
        select * from word where text in ('春', '江');
        :return:
        """
        conn = await self._mysql_conn()
        cur = await conn.cursor()

        # 缓存新方案：　每个令词随机取出1000条左右的数据，定时刷新到缓存
        sql_list = []
        sql = ""
        for i in range(len(self.words)):
            word = self.words[i]
            sub_sql = """
                SELECT
                    *
                FROM
                    (SELECT
                        w.id, swa.sentence_id
                    FROM
                        `sentence_word_association` AS swa
                    JOIN (SELECT
                        ROUND(RAND() * ((SELECT
                                    MAX(id)
                                FROM
                                    `sentence_word_association`) - (SELECT
                                    MIN(id)
                                FROM
                                    `sentence_word_association`)) + (SELECT
                                    MIN(id)
                                FROM
                                    `sentence_word_association`)) AS id
                    ) AS t2
                    LEFT JOIN word w ON w.id = swa.word_id
                    WHERE
                        swa.id >= t2.id AND w.text = {word}
                    LIMIT {limit}) x{index}
            """.format(word=repr(word), index=i, limit=limit)
            sql_list.append(sub_sql)

        if sql_list:
            sql = """
            select union_table.id, group_concat(union_table.sentence_id) as sentence_ids
             from ({sqls})union_table
             group by union_table.id;

            """.format(sqls=" union all ".join(sql_list))
        if sql:
            await cur.execute("SET SESSION group_concat_max_len = {0};".format(1024000))
            await cur.execute(sql)
            result = await cur.fetchall()
            await cur.close()
            conn.close()
            return result

    # 2 sentence_word_association表
    async def sentence_word_association_cacher(self, limit=1024):
        sentence_word_ids = await self._get_sentence_words_association(limit)
        table_words = dict(await self._get_table_word())
        if sentence_word_ids:
            mapping = dict([(table_words[word_id], sentence_ids.split(","))
                            for word_id, sentence_ids in sentence_word_ids if sentence_ids])
            redis_cli = await self._redis_conn()
            result = await redis_cli.set(POETRY_CACHE_KEY, pack(mapping))
            redis_cli.close()
            await redis_cli.wait_closed()
            return result

    async def build_cache(self):
        # 定时刷新缓存
        while True:
            _Logger.info("{0} [刷新缓存]: sentence_word_association => start".format(
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
            try:
                await self.sentence_word_association_cacher(limit=100)
            except:
                _Logger.info(traceback.print_exc())
            _Logger.info("{0} [刷新缓存]: sentence_word_association => success!".format(
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
            await asyncio.sleep(REFRESH_PERIOD)   # 分钟刷新一次缓存

    async def runner(self):
        await self.build_cache()

    async def get_cache(self):
        redis_cli = await self._redis_conn()
        result = await redis_cli.get(POETRY_CACHE_KEY)
        print(unpack(result))
