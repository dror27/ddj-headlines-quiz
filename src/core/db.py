# handle db stuff

from pymongo import MongoClient
import os
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db():

    # open database connection
    username = db_env("DBUSER", "root")
    password=  db_env("DBPASS", "mongo")
    host = db_env("DBHOST", "mongo")
    url = ('mongodb://%s:%s@' + host) % (username, password)
    logger.info("url: " + url)
    client = MongoClient(url)
    db = client.headings
    return db

def db_env(name, defaultValue=None):
	key = "TEL_BOT_" + name
	value = os.environ[key] if key in os.environ else defaultValue
	logger.info("key %s value %s" % (key, value))
	return value

def db_sources():
    return [source for source in get_db().sources.find()]

