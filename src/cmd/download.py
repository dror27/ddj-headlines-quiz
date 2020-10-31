# download commands

import os
import io
import tempfile
import wordcloud
import datetime
import logging
from bidi.algorithm import get_display
import moviepy.video.io.ImageSequenceClip
import PIL

import core.db
import core.user
import core.histogram
import core.time
import cmd.common

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

stopwords = ["new", "say", "says", "said", "live", "will", "best", "vs", "reveal", "revealed", 
				"man", "woman", "men", "women",
				*wordcloud.STOPWORDS]


def qr_handler(update, context):
    for path in [".", "../data"]:
      fname = path + "/qr-code.png"
      if os.path.isfile(fname):
        update.message.reply_photo(open(fname, 'rb'))
        break

def wc_handler(update, context):
	info, domain, keyword, historic = wc_prep(update)
	with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
		wc_image(tmp.name, domain, keyword=keyword, historic=historic)
		update.message.reply_photo(open(tmp.name, 'rb'))


def wc_movie_handler(update, context):
	info, domain, keyword, historic = wc_prep(update)
	if not historic:
		historic = 10
	image_files = []
	for depth in reversed(range(historic)):
		tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
		image_files.append(tmp.name)
		print(tmp.name)
		wc_image(tmp.name, domain, keyword, depth, True)
	clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=1)
	with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp:
		clip.write_videofile(tmp.name)
		update.message.reply_video(open(tmp.name, 'rb'))
	for path in image_files:
		os.remove(path)


def wc_prep(update):
	info = core.user.get_user_info(update)
	domain = core.user.get_user_domain(info)
	keyword  = info["keyword"] if "keyword" in info  else None

	tail = cmd.common.cmd_tail(update)
	historic = int(tail) if tail else 0

	return (info, domain, keyword, historic)


def wc_image(path, domain, keyword=None, historic=0, addLabel=False):
	text, label = wc_text(domain, keyword=keyword, historic=historic)
	logger.info("text length: %d" % len(text))
	if domain != "ilnews":
		wc = wordcloud.WordCloud(width=400, height=200, random_state=1, 
				background_color='black', colormap='Set2', collocations=False, 
				stopwords = stopwords).generate(text)
	else:
		wc = wordcloud.WordCloud(width=400, height=200, random_state=1, 
				background_color='black', colormap='Set2', collocations=False, 
				font_path='ArialHB.ttc',
				stopwords = stopwords).generate(get_display(text))

	wc.to_file(path)

	if addLabel:
		anchor = (0, 0)
		original = PIL.Image.open(path)
		draw = PIL.ImageDraw.Draw(original)
		draw.rectangle(((9, 0), (400, 10)), fill="black")
		draw.text((0, 0), label)
		original.save(path)


def wc_text(domain, keyword=None, historic=0):
	db = core.db.get_db()

	# establish initial limits
	until_ts = datetime.datetime.now()
	from_ts = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())

	# walk back into history (in steps of days
	if historic > 0:
		from_ts = from_ts - datetime.timedelta(days=historic)
		until_ts = from_ts + datetime.timedelta(days=1)

	# build label
	label = "%s - %s" % (from_ts.strftime("%d/%m/%y"), until_ts.strftime("%d/%m/%y"))

    # get heading for one of the sources
	query_fields =  {
	    "$and": [
	        {
	            "_timestamp": 
	            {
	                "$lte": until_ts
	            }
	        }, 
	        {
	            "_timestamp": 
	            {
	                "$gte": from_ts
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
	return text, label

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

