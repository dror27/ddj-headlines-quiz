# download commands

import os
import tempfile
import wordcloud
import datetime
import logging
import core.db
import core.user
from bidi.algorithm import get_display

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)



def qr_handler(update, context):
    for path in [".", "../data"]:
      fname = path + "/qr-code.png"
      if os.path.isfile(fname):
        update.message.reply_photo(open(fname, 'rb'))
        break

def wc_handler(update, context):
	info = core.user.get_user_info(update)
	domain = core.user.get_user_domain(info)
	keyword  = info["keyword"] if "keyword" in info  else None
	with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
		text = wc_text(domain, keyword=keyword)
		logger.info("text length: %d" % len(text))
		if domain != "ilnews":
			wc = wordcloud.WordCloud(width=400, height=200, random_state=1, 
					background_color='black', colormap='Set2', collocations=False, 
					stopwords = wordcloud.STOPWORDS).generate(text)
		else:
			wc = wordcloud.WordCloud(width=400, height=200, random_state=1, 
					background_color='black', colormap='Set2', collocations=False, 
					font_path='/System/Library/Fonts/ArialHB.ttc',
					stopwords = wordcloud.STOPWORDS).generate(get_display(text))

		wc.to_file(tmp.name)

		update.message.reply_photo(open(tmp.name, 'rb'))

def wc_text(domain, keyword=None):
	db = core.db.get_db()
	midnight = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())

    # get heading for one of the sources
	query_fields =  {
	    "$and": [
	        {
	            "_timestamp": 
	            {
	                "$gte": midnight
	            }
	        }, 
	        {
	            "_source.domain": domain
	        }
	    ]
	}
	if keyword:
	    query_fields["$text"] = {"$search": keyword}

	text = ""
	for heading in db.headings.find(query_fields):
		text += (" " + heading["title"])
	return text
