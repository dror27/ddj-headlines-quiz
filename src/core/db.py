# handle db stuff

from pymongo import MongoClient
import os
import logging
import datetime

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db():

    # open database connection
    username = db_env("DBUSER", "root")
    password=  db_env("DBPASS", "mongo")
    host = db_env("DBHOST", "mongo")
    url = ('mongodb://%s:%s@' + host) % (username, password)
    #logger.info("url: " + url)
    client = MongoClient(url)
    db = client.headings
    return db

def db_env(name, defaultValue=None):
    key = "TEL_BOT_" + name
    value = os.environ[key] if key in os.environ else defaultValue
    if isinstance(value, str) and value.isdigit():
        value = int(value)
    #logger.info("key %s value %s" % (key, value))
    #logger.info(type(value))
    return value

def db_sources(domain):
    return [source for source in get_db().sources.find({"domain": domain})]

def db_domains():
    return [domain for domain in get_db().sources.distinct("domain")]

def db_headings_count(domain, since=datetime.datetime.min):
    agg = [
        {
            "$match": {
                "_timestamp": 
                {
                    "$gte": since
                },
                "_source.domain": domain
            }
        },
        {
            "$group": {
                "_id": "$_source.name",
                "count": { "$sum": 1}
            }
        },
        {
            "$sort": {
                "_id": 1
            }
        }
    ]

    return {doc["_id"]: doc['count'] for doc in get_db().headings.aggregate(agg)}
  

