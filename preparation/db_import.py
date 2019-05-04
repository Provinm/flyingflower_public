#coding=utf-8

import json
import os
import sys
import re
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

try:
    from .db_create import Poetry, Sentence, Word, SentenceWordAssociation
except:
    from db_create import Poetry, Sentence, Word, SentenceWordAssociation

MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_HOST = os.environ.get("MYSQL_HOST")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT"))


CHINESE_RE_PAT = re.compile(r"[\u4e00-\u9fa5]")


class DbHandler:

    def __init__(self):
        self.session = self.create_session()

    def create_session(self):
        mysql_url = 'mysql+pymysql://' + MYSQL_USER + ":" + MYSQL_PASSWORD + \
        "@" + MYSQL_HOST + ":" + str(MYSQL_PORT) + "/" + MYSQL_DATABASE
        engine = create_engine(mysql_url, echo=True)
        session = Session(bind=engine)
        return session

    def write_poetry(self, **kw):
        kw["paragraphs"] = join_para(kw["paragraphs"])
        new_poetry = Poetry(**kw)
        self.session.add(new_poetry)
        self.session.commit()
        return new_poetry

    def write_sentence(self, **kw):
        new_sentence = Sentence(**kw)
        self.session.add(new_sentence)
        # self.session.commit()
        return new_sentence

    def write_word(self, text):
        #get or create 
        word = self.session.query(Word).filter(Word.text==text).first()
        if not word:
            word = Word(text=text)
            self.session.add(word)
        # self.session.commit()
        return word

    def commit(self):
        self.session.commit()


def join_para(para, joiner=""):
    return joiner.join(para)


def is_chn(s):
    return bool(re.match(CHINESE_RE_PAT, s))


def normalized(keys):
    def out_wrapper(func):
        @wraps(func)
        def in_wrapper(self, dct, *args, **kw):
            valid = all([False for k in keys if k not in dct])
            if not valid:
                return False

            dct = func(self, dct, *args, **kw)

            new_keys = ["author", "paragraphs", "title", "type"]
            for key in list(dct):
                if key not in new_keys:
                    del dct[key]
            return dct
        return in_wrapper
    return out_wrapper


class FileHandler:
    
    def __init__(self, path):

        self.dir_path = path
        self.db_handler = DbHandler()

    @normalized(keys=["author", "paragraphs", "rhythmic"])
    def pre_process_ci(self, dct:dict):
        dct["title"] = dct["rhythmic"]
        dct["_type"] = "C"
        return dct

    @normalized(keys=["author", "paragraphs", "title"])
    def pre_process_poet(self, dct: dict):
        dct["_type"] = "S"
        return dct

    @normalized(keys=["chapter", "content", "section", "title"])
    def pre_process_shijing(self, dct:dict):

        dct["title"] = "{}-{}-{}".format(dct["chapter"], dct["section"], dct["title"])
        dct["paragraphs"] = dct["content"]
        dct["author"] = "佚名"
        dct["_type"] = "J"
        return dct

    @normalized(keys=["author", "paragraphs", "title"])
    def pre_process_wudai(self, dct: dict):
        dct["_type"] = "S"
        return dct

    def process_poet(self, obj:dict):
        '''call after pre_process_
        '''
        new_poetry = self.db_handler.write_poetry(**obj)
        return new_poetry

    def process_sentence(self, obj:str, poetry_id:int):
        obj = {
            "text": obj,
            "poetry_id": poetry_id
        }
        new_sentence = self.db_handler.write_sentence(**obj)
        return new_sentence
    
    def process_word(self, obj:str):

        # obj = {
        #     "text": obj,
        # }
        new_word = self.db_handler.write_word(obj)
        return new_word

    def process_item(self, obj:dict):

        poetry = self.process_poet(obj)
        para = obj["paragraphs"]

        for sentence in para:
            sentence = sentence.replace('□','')
            new_sentence = self.process_sentence(sentence, poetry.id)
            for word in sentence:
                if is_chn(word):
                    word = self.process_word(word)
                    new_sentence.words.append(word)
            poetry.sentences.append(new_sentence)

        self.db_handler.commit()
    
    def process_file(self, file_path):
        pre_process_cb = self.find_file_cb(file_path)
        if not pre_process_cb:
            return 

        with open(file_path, "r")as f:
            data = json.loads(f.read())

        try:
            for item in data:
                normalized_item = pre_process_cb(item)
                self.process_item(normalized_item)
                break
        
        except Exception as err:
            print(f"err happened when processing {file_path} error = {err}")


    def find_file_cb(self, file_path):

        file_name = file_path.split("/")[-1]

        if not (file_name.endswith("json")):
            return None
        
        # ci
        if file_name.startswith("ci"):
            return self.pre_process_ci

        elif file_name.startswith("poet"):
            return self.pre_process_poet

        elif file_name.startswith("shijing"):
            return self.pre_process_shijing

        elif file_name.startswith("poetrys"):
            return self.pre_process_wudai

        return None

    def run(self):

        for root, _, files in os.walk(self.dir_path):
            for f in files:
                file_path = os.path.abspath(os.path.join(root, f))
                self.process_file(file_path)


if __name__ == "__main__":
    path = r"/var/data/poetry"
    fh = FileHandler(path)
    fh.run()