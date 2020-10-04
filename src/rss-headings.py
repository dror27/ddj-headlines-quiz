#!/usr/bin/env python

from pymongo import MongoClient
import pymongo
import feedparser
from pprint import pprint
import datetime

import core.db
import core.rss

# open database connection
db = core.db.get_db()

# loop on sources
if core.db.db_env("FETCH", 1): 
    for source in db.sources.find():

        if "userAgent" in source:
            feed = feedparser.parse(source["rss"], agent=source["userAgent"])
        else:
            feed = feedparser.parse(source["rss"])
        print(feed.href, len(feed.entries))
        
        for entry in feed.entries:
            entry["_source"] = source
            entry["_fetched"] = datetime.datetime.utcnow()
            entry["_timestamp"] = datetime.datetime(*entry["published_parsed"][0:6]) if "published_parsed" in entry else entry["_fetched"]
            core.rss.ensure_entry_has_id(entry)
                        
            try:
                key = {"id": entry.id}
                db.headings.replace_one(key, entry, True)
            except AttributeError as e:
                pprint("exception:")
                pprint(e)
                pprint("source:")
                pprint(source)
                pprint("entry:")
                pprint(entry)
                break

# summarise number of headings per source
if core.db.db_env("SUMMARISE", 1): 
    midnight = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
    for domain in core.db.db_domains():
        print("%s:"  % domain)
        for key,value in core.db.db_headings_count(domain, midnight).items():
            print("%s (%d)" % (key,value))

