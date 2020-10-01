#!/usr/bin/env python

from pymongo import MongoClient
import pymongo
from pprint import pprint
import logging
import os
import json
import datetime
import time
import sys

import core.db

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# open database connection
logging.info("attempting to connect to database ...")
db = core.db.get_db()

# load
for fname in sys.argv[1:]:
    logger.info("loading sources from:" + fname)
    with open(fname) as f:
        data = json.load(f)
        db.sources.insert_many(data)






