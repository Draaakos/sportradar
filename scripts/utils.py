import os
import platform
import pymongo
import logging
import datetime


def make_mongo_con(host='127.0.0.1', port=27017):
    return pymongo.MongoClient(host, port)


def create_logger(filename, name):
    today = datetime.date.today()
    year = str(today.year).zfill(4)
    month = str(today.month).zfill(2)
    day = str(today.day).zfill(2)
    file = f'/tmp/{year}-{month}-{day}-{filename}.log'

    logging.basicConfig(
        filename=file,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y/%m/%d %I:%M:%S'
    )

    logger = logging.getLogger(name)
    return logger
