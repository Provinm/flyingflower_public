import os 
import sys
import asyncio

BASE_DIR = os.path.abspath(os.path.join("..", os.path.dirname(__file__)))
print(BASE_DIR)
sys.path.append(BASE_DIR)

from sqlalchemy import create_engine
from sqlalchemy.orm import Session


from flyingflower.cache_build import CacheBuilder

try:
    from .db_create import Poetry, Sentence, Word, SentenceWordAssociation
except:
    from db_create import Poetry, Sentence, Word, SentenceWordAssociation


MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_HOST = os.environ.get("MYSQL_HOST")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT"))


class DbHandler:

    def __init__(self):
        self.session = self.create_session()

    def create_session(self):
        mysql_url = 'mysql+pymysql://' + MYSQL_USER + ":" + MYSQL_PASSWORD + \
        "@" + MYSQL_HOST + ":" + str(MYSQL_PORT) + "/" + MYSQL_DATABASE
        engine = create_engine(mysql_url, echo=True)
        session = Session(bind=engine)
        return session

    def test_word(self, text):

        word = self.session.query(Word).filter(Word.text==text).first()

        # print(word.sentences)
        for s in word.sentences:
            print(s.text)


    def commit(self):
        self.session.commit()


async def test_cache_build():

    cache_build = CacheBuilder()
    await cache_build.runner()
    await cache_build.get_cache()


if __name__ == "__main__":
    # dbs = DbHandler()
    # dbs.test_word("一")
    asyncio.run(test_cache_build())