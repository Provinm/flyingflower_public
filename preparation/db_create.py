#-*- coding:utf-8 -*-
import os 

from sqlalchemy import create_engine, Table, ForeignKey
from sqlalchemy.orm import query, Session, scoped_session, sessionmaker
from sqlalchemy import Column, Integer, SmallInteger, Text, DECIMAL, Boolean, BigInteger, TEXT, VARCHAR
from sqlalchemy.dialects import mysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_HOST = os.environ.get("MYSQL_HOST")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT"))

BaseModel = declarative_base()

class Poetry(BaseModel):
    '''诗词内容
    '''
    __tablename__ = 'poetry'
    id = Column(Integer, autoincrement=True, primary_key=True)
    author = Column(VARCHAR(20), default="佚名")  # 作者
    title = Column(VARCHAR(100), default="")    # 标题
    paragraphs = Column(TEXT, default="")    # 正文
    """
    CONTENT_TYPE = (
        ("S", "诗"),
        ("C", "词"),
        ("J", "经"),
        ("O", "其他"))
    """
    _type = Column(VARCHAR(1),  default="S")
    sentences = relationship("Sentence", backref="poetry")

    def __str__(self):
        return self.title

# manytomany 中间表
SentenceWordAssociation = Table("sentence_word_association", BaseModel.metadata,
                                Column("id", Integer, primary_key=True),
                                Column("sentence_id", Integer, ForeignKey("sentence.id")),
                                Column("word_id", Integer, ForeignKey("word.id"))
                                # Column("position", Integer, nullable=False)  # word位于sentence位置 从1开始
                          )

class Sentence(BaseModel):
    '''每一句诗词
    '''
    __tablename__ = 'sentence'
    id = Column(Integer, autoincrement=True, primary_key=True)
    poetry_id = Column(Integer, ForeignKey("poetry.id"), nullable=False) # 诗词id
    text = Column(TEXT, default="", nullable=False) # 句
    words = relationship("Word", secondary=SentenceWordAssociation, backref="sentences")
    def __str__(self):
        return self.text

class Word(BaseModel):
    '''每一个字
    '''
    __tablename__ = 'word'
    id = Column(Integer, autoincrement=True, primary_key=True)
    text = Column(VARCHAR(1), default="", nullable=False, index=True)  # 句

    def __str__(self):
        return self.text

def main():
    mysql_url = 'mysql+pymysql://' + MYSQL_USER + ":" + MYSQL_PASSWORD + \
        "@" + MYSQL_HOST + ":" + str(MYSQL_PORT) + "/" + MYSQL_DATABASE
    engine = create_engine(mysql_url, echo=True)
    BaseModel.metadata.create_all(engine)   

if __name__ == "__main__":
    main()

