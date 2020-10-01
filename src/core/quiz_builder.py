# build quizes

import random
import datetime
import logging

import core.db

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def build_heading_quiz(answers, keyword=None, sources_subset=None):

    db = core.db.get_db()
    
    # loop for 10 attempts
    midnight = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
    sources_all = [x["name"] for x in db.sources.find()]
    domain = core.db.db_env("DOMAIN", "uknews")

    # subset sources?
    if sources_subset and len(sources_subset) > 1 :
        sources_all = [ sources_all[i-1] for i in sources_subset]
    logger.info("sources_all: " + str(sources_all))
    if len(sources_all) < answers:
        answers = len(sources_all)

    logger.info("build_heading_quiz: %s" % domain)
    for _ in range(10):
    
        # pick random sources
        sources = random.sample(sources_all, answers)
        random.shuffle(sources)
        
        # get heading for one of the sources
        heading_source_name = None
        for s in sources:
            query_fields =  {
                "$and": [
                    {
                        "_timestamp": 
                        {
                            "$gte": midnight
                        }
                    }, 
                    {
                        "_source.name": s
                    },
                    {
                        "_source.domain": domain
                    }
                ]
            }
            if keyword:
                query_fields["$text"] = {"$search": keyword}
            
            source_headings = list(db.headings.aggregate(
                [
                    {"$match": query_fields },
                    {"$sample": {"size": 1} }
                ]
            )
                                  )
            if source_headings and len(source_headings) > 0:
                heading = source_headings[0]
                heading_source_name = s
                break
                
        # did we get an answer?
        if heading_source_name:
            random.shuffle(sources)
            index = sources.index(heading_source_name)
            return {"title": heading["title"], "sources": sources, "index": index, "link": heading["link"]}
    
    # if here, not found, try without keyword
    if keyword:
        return build_heading_quiz(answers, sources_subset=sources_subset)
    else:
        return None

def build_default_quiz():
    
    # get a prime or a non trivial odd between 100 and 200. at bit clumsy ...
    primes = []
    odds = []
    for num in range(100, 200):
        for i in range(2, num):
            if (num % i) == 0:
                if (num % 2) == 1 and (num % 5) != 0:
                    odds.append(num)
                break
        else:
            primes.append(num)
        
    
    # create Yes/No distribution
    answers = ["Yes", "No"]
    random.shuffle(answers)    
    number = random.sample(primes, 1)[0] if random.random() < 0.5 else random.sample(odds, 1)[0]
    answer = "Yes" if number in primes else "No"
    
    title = "Could not find suitable heading. This will have to do ... is %d a prime number?" % number
    
    return {"title": title, "sources": answers, "index": answers.index(answer), "link": None}

