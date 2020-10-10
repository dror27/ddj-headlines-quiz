# download commands

import os
import io
import tempfile
import wordcloud
import datetime
import logging
from bidi.algorithm import get_display

import core.db
import core.user
import core.histogram
import core.time

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
					font_path='ArialHB.ttc',
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

def headings_handler(update, context):

	info = core.user.get_user_info(update)
	domain = core.user.get_user_domain(info)

	with tempfile.NamedTemporaryFile() as tmp:
		core.db.db_export("headings", domain, tmp.name, 
			"_id,title,link,summary,published,credit,author,updated,_source.name,_source.domain,_source.rss,_source.url,_fetched,_timestamp")
		filename = "%s_headlines_%s.csv" % (domain, datetime.datetime.now().strftime("%y%m%d"))
		update.message.reply_document(open(tmp.name, 'rb'), filename=filename)

def histograms_handler(update, context):
	info = core.user.get_user_info(update)
	domain = core.user.get_user_domain(info)
	since = core.time.midnight()
	sources_data = core.histogram.histogram_count_data(domain, since)
	title = "headlines wordcount, %s\n@HeadlinerQuizBot" % since.strftime("%d/%m/%Y")
	with io.BytesIO() as buf:
		core.histogram.histogram_plot_all(sources_data,  title , buf)
		buf.seek(0)
		update.message.reply_photo(buf)

