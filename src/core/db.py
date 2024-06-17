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
    username, password, host = db_vars()
    url = ('mongodb://%s:%s@' + host + ':27017') % (username, password)
    logger.info("url: " + url)
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

def db_headings_iter(domain, since=datetime.datetime.min):
    query = {
        "_timestamp": 
        {
            "$gte": since
        },
        "_source.domain": domain
    }

    return get_db().headings.find(query)


def db_top_headings_iter(domain, source=None, keyword=None):
    query = {
        "_source.domain": domain
    }
    if keyword:
        query["$text"] = {"$search": keyword}
    if source:
        query["_source.name"] = source

    return get_db().headings.find(query).sort("_timestamp", -1)


def db_vars():
    username = db_env("DBUSER", "root")
    password = db_env("DBPASS", "mongo")
    host = db_env("DBHOST", "mongo")
    return (username, password, host)


def db_export(collection, domain, fields, file):
    username, password, host = db_vars()
    cmd = "mongoexport --collection=%s -d headings -u %s -p %s -h %s --authenticationDatabase admin --type=csv -f %s --out %s -q '{\"_source.domain\":\"%s\"}'" %(
        collection, username, password, host, file, fields, domain)
    logger.info(cmd)
    os.system(cmd)
  

