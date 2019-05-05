# -*- coding:utf-8 -*-

import os


# 百度识别配置
APP_ID = os.environ.get("APP_ID")
API_KEY = os.environ.get("API_KEY")
SECRETE_KEY = os.environ.get("SECRETE_KEY")

# mysql 配置
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_HOST = os.environ.get("MYSQL_HOST")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT"))

# redis 配置
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_DB = os.environ.get("REDIS_DB")
REDIS_PORT = int(os.environ.get("REDIS_PORT"))

# 包含的令词
# SELECTED_WORDS = '春江花月夜 风雨雷电雪 日月星石 春夏秋冬 梅兰竹菊 金木水火土'
SELECTED_WORDS = '花春月风夜 人山云酒新 年绿水松青 书香归心平 思家'

# 日志设置
EBROSE_LOGGER_CONFIG = {
    "version": 1,
    "formatters":{
        "normal":{
            "class": "logging.Formatter",
            "format": "[%(asctime)s][%(thread)d(%(threadName)s)][%(module)s(%(funcName)s)(%(lineno)d)] %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "ebrose_main.log",
            "mode": "w",
            "formatter": "normal",
            "level": "DEBUG"
        },
        "errors": {
            "class": "logging.FileHandler",
            "filename": "ebrose_error.log",
            'mode': 'w',
            'level': 'ERROR',
            'formatter': 'normal',
        }
    },

    "loggers": {
        "riverrun": {
            "level": "DEBUG",
            "handlers": ["console", "file", "errors"]
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file", "errors"]
    } 
}