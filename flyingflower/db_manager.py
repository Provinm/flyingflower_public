# -*- coding:utf-8 -*-

import asyncio
import aiomysql
import traceback
import logging

from .settings import MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
from .settings import MYSQL_HOST, MYSQL_PORT

_Logger = logging.getLogger()

async def mysql_connect():

    pool = await aiomysql.create_pool(
        host=MYSQL_HOST, port=MYSQL_PORT,
        user=MYSQL_USER, password=MYSQL_PASSWORD,
        db=MYSQL_DATABASE, autocommit=False)

    return pool

mysql_pool = None


async def execute(statement):
    global mysql_pool

    if not statement:
        return None

    if not mysql_pool:
        mysql_pool = await mysql_connect()

    async with mysql_pool.acquire() as conn:
        cur = await conn.cursor()
        try:
            await cur.execute(statement)
        except Exception as err:
            _Logger.error(traceback.print_exc())
            raise err
        finally:
            await cur.close()

        return await cur.fetchone()


async def get_sentence_by_text(sentence_txt):
    sql = "select id, poetry_id, text from sentence where locate({0}, text)>0 limit 1;".format(
        repr(sentence_txt))
    result = await execute(sql)
    return result


# 根据id从sentence表中查询诗句
async def get_sentence_by_id(sentence_id):
    sql = "select id, poetry_id, text from sentence where id={0} limit 1;".format(
        sentence_id)
    result = await execute(sql)
    return result


async def get_poetry_by_id(poetry_id):
    sql = "select author_id, title, paragraphs from poetry where id={0} limit 1;".format(
        poetry_id)
    result = await execute(sql)
    return result
