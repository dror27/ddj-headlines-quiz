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
from pprint import pprint
import re

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

def wc_anim_handler(update, context, hourly=False, top=100):
	info, domain, keyword, historic = wc_prep(update)
	if not historic:
		historic = 10
	html = '<html><body>%s</body></html>' % \
			wc_anim(domain, keyword=keyword, historic=historic, top=top, hourly=hourly)
	filename = "wc_%s_%d.html" % (domain, historic)

	with tempfile.NamedTemporaryFile(suffix=".html") as tmp:
		with open(tmp.name, "w") as f:
			f.write(html)
		update.message.reply_document(open(tmp.name, "rb"), filename=filename)

def wc_prep(update):
	info = core.user.get_user_info(update)
	domain = core.user.get_user_domain(info)
	keyword  = info["keyword"] if "keyword" in info  else None

	tail = cmd.common.cmd_tail(update)
	historic = int(tail) if tail else 0

	return (info, domain, keyword, historic)


def wc_image(path, domain, keyword=None, historic=0, addLabel=False, hourly=False):
	text, label = wc_text(domain, keyword=keyword, historic=historic, hourly=hourly)
	#logger.info("text length: %d" % len(text))
	if domain != "ilnews":
		wc = wordcloud.WordCloud(width=400, height=200, random_state=1, 
				background_color='black', colormap='Set2', collocations=False, 
				stopwords = stopwords).generate(text)
	else:
		wc = wordcloud.WordCloud(width=400, height=200, random_state=1, 
				background_color='black', colormap='Set2', collocations=False, 
				font_path='ArialHB.ttc',
				stopwords = stopwords).generate(get_display(text))

	if path:
		wc.to_file(path)

		if addLabel:
			anchor = (0, 0)
			original = PIL.Image.open(path)
			draw = PIL.ImageDraw.Draw(original)
			draw.rectangle(((9, 0), (400, 10)), fill="black")
			draw.text((0, 0), label)
			original.save(path)

	return wc, label


def wc_text(domain, keyword=None, historic=0, hourly=False):
	db = core.db.get_db()

	# establish initial limits
	until_ts = datetime.datetime.now()
	if not hourly:
		from_ts = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())

		# walk back into history (in steps of days
		if historic > 0:
			from_ts = from_ts - datetime.timedelta(days=historic)
			until_ts = from_ts + datetime.timedelta(days=1)
	else:
		from_ts = until_ts - datetime.timedelta(hours=2)
		mid_ts = until_ts - datetime.timedelta(hours=1)
		if historic > 0:
			from_ts = from_ts - datetime.timedelta(hours=historic)
			mid_ts = from_ts + datetime.timedelta(hours=1)
			until_ts = from_ts + datetime.timedelta(hours=2)

	print(domain, from_ts, until_ts)

	# build label
	if not hourly:
		label = (from_ts + datetime.timedelta(seconds=1)).strftime("%d/%m/%y")
	else:
		label = until_ts.strftime("%H:%M")

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
		if hourly:
			if  heading["_timestamp"] >= mid_ts:
				text += (" " + heading["title"])
	if not text:
		text = "none"
	return cleanup_text(text), label

def cleanup_text(text):

	toks = [x if x.isupper() else x.capitalize() for x in re.split(r"\W[\W']*", text)]
	return " ".join(toks)

def headings_handler(update, context):

	info = core.user.get_user_info(update)
	domain = core.user.get_user_domain(info)

	with tempfile.NamedTemporaryFile(delete=False) as tmp:
		core.db.db_export("headings", domain, tmp.name, 
			"_id,title,link,summary,published,credit,author,updated,_source.name,_source.domain,_source.rss,_source.url,_fetched,_timestamp")
		filename = "%s_headlines_%s.csv" % (domain, datetime.datetime.now().strftime("%y%m%d"))
		os.system("gzip " + tmp.name)
		os.system("ls -l " + tmp.name + "*")
		update.message.reply_document(open(tmp.name + ".gz", 'rb'), filename=filename + ".gz")
		os.remove(tmp.name + ".gz")

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

def wc_anim(domain, keyword=None, historic=2, top=3, hourly=False):

	# collect layouts, words (w/ initial layout)
	layouts = []
	labels = []
	words = {}
	for depth in reversed(range(historic)):
		wc, label = wc_image(None, domain, keyword, depth, True, hourly=hourly)
		labels.append(label)
		layout = wc.layout_
		if top:
			layout = layout[:top]
		layouts.append(layout)
		for elem in layout:
			word = elem[0][0]
			if not word in words:
				words[word] = elem

	# build frames for each word
	# start with a frame where all words are at their initial position with opacipy of 0
	frames = {}
	for word, layout in words.items():
		elayout = (*layout, 0)
		frames[word] = [elayout]

	# add additional frames
	for layout in layouts:

		# add words in current layout
		cwords = set(words.keys())
		for elem in layout:
			word = elem[0][0]
			frames[word].append((*elem, 1))
			words[word] = (*elem, 0)
			cwords.remove(word)

		# add words not in current layout
		for word in cwords:
			frames[word].append([*words[word], 0])


	# generate svg
	sizeFactor = 2
	seqLength = len(layouts)
	frameSize = 1 / (seqLength + 1)
	stabilityPad = frameSize / 3
	dur  = seqLength


	svg = '';
	svg += '''<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" style="background-color:black">
<style>
text{font-family:'Droid Sans Mono';font-weight:normal;font-style:normal;}
  .label {
    font-size: 2.6em;
    text-anchor:middle;
    font-weight: bold;
    fill:grey;
    x: 100px;
    y: 100px;
  }
</style>
''' % (int(400*sizeFactor), int((200+20)*sizeFactor))

	# generate labels
	i = 0
	for label in labels:
		i += 1
		key1 = frameSize  * (i - 0.7)
		key2 = frameSize  * (i - 0.5)
		key3 = frameSize  * (i + 0.5)
		key4 = frameSize  * (i + 0.7)
		last = 1 if (i == len(labels)) else 0
		innerSVG = '<animate attributeName="opacity" values="0; 0; 1; 1; %d; %d" keyTimes="0; %f; %f; %f; %f; 1" dur="%ds" begin="0s" fill="freeze"/>\n' % \
							(last, last, key1, key2, key3, key4, dur)
		svg += '<text class="label" x="%d" y="%d" style="opacity:0">%s%s</text>\n' % \
					(sizeFactor * 200, sizeFactor * 20, innerSVG, label)

	# generate words
	for word, elem in words.items():
		clazz = "w_%s" % word
		fontSize = sizeFactor * elem[1]
		y = sizeFactor * (elem[2][0] + fontSize / sizeFactor * 3 // 4)
		y = 0
		x = sizeFactor * elem[2][1]
		fill = elem[4]
		rotate = 90 if elem[3] else 0
		innerSVG, innerSVG2 = anim_elem(frames[word], len(layouts), sizeFactor, frameSize, stabilityPad, dur)
		svg += (' <g><text class="%s" transform="translate(%d,%d) rotate(%d)" font-size="%d" style="opacity:0; fill:%s">%s%s</text>%s</g>\n' % 
					(clazz, x, y, rotate, fontSize, fill, innerSVG, word, innerSVG2))
	svg += "</svg>\n"

	return svg

def anim_elem(elayouts, seqLength, sizeFactor, frameSize, stabilityPad, dur):

	# generate key frames
	keyFrames = [0]
	for n in range(seqLength):
		center = (n + 1) * frameSize
		keyFrames.append(center - stabilityPad)
		keyFrames.append(center + stabilityPad)
	keyFrames.append(1)

	# generate series for font size, opacity
	fontSizes = []
	opacity = []
	fill = []
	location = []
	rotate = []
	fontSize = sizeFactor * elayouts[0][1]
	fontSizes.append(fontSize)
	opacity.append(elayouts[0][5])
	fill.append(elayouts[0][4])
	y = sizeFactor * (elayouts[0][2][0] + fontSize / sizeFactor * 3 // 4)
	y = 0
	x = sizeFactor * elayouts[0][2][1]
	location.append("%d,%d" % (x, y))
	rotate.append(90 if elayouts[0][3] else 0)
	for elayout in elayouts[1:]:
		fontSize = sizeFactor * elayout[1]
		fontSizes.append(fontSize)
		fontSizes.append(fontSize)

		opacity.append(elayout[5])
		opacity.append(elayout[5])

		fill.append(elayout[4])
		fill.append(elayout[4])

		y = sizeFactor * (20 + elayout[2][0] + fontSize / sizeFactor * 3 // 4)
		x = sizeFactor * elayout[2][1]
		location.append("%d,%d" % (x, y))
		location.append("%d,%d" % (x, y))

		rotate.append(90 if elayout[3] else 0)
		rotate.append(90 if elayout[3] else 0)

	fontSize = sizeFactor * elayouts[-1][1]
	fontSizes.append(fontSize)
	opacity.append(elayouts[-1][5])
	fill.append(elayouts[-1][4])
	y = sizeFactor * (20 + elayouts[-1][2][0] + fontSize / sizeFactor * 3 // 4)
	x = sizeFactor * elayouts[-1][2][1]
	location.append("%d,%d" % (x, y))
	rotate.append(90 if elayouts[-1][3] else 0)

	#　generate animation tags
	anim = ""
	anim2 = ""
	animX = ""
	keyTimes = "; ".join(["{:.2f}".format(x) for x in keyFrames])
	anim += '''<animate attributeName="font-size" values="%s" keyTimes="%s" dur="%ds" begin="0s" fill="freeze"/>\n''' % \
					("; ".join([str(x) for x in fontSizes]), keyTimes, dur)
	anim += '''<animate attributeName="opacity" values="%s" keyTimes="%s" dur="%ds" begin="0s" fill="freeze"/>\n''' % \
					("; ".join([str(x) for x in opacity]), keyTimes, dur)
	animX += '''<animate attributeName="fill" values="%s" keyTimes="%s" dur="%ds" begin="0s" fill="freeze"/>\n''' % \
					("; ".join(fill), keyTimes, dur)
	anim2 += '''<animateTransform attributeName="transform" type="translate" values="%s" keyTimes="%s" dur="%ds" begin="0s" fill="freeze"/>\n''' % \
					("; ".join(location), keyTimes, dur)
	anim += '''<animateTransform attributeName="transform" type="rotate" values="%s" keyTimes="%s" dur="%ds" begin="0s" fill="freeze"/>\n''' % \
					("; ".join([str(x) for x in rotate]), keyTimes, dur)



	return (anim, anim2)

def main():
	svg = wc_anim("uknews", historic=5, top=5)
	print(svg)

if __name__ == '__main__':
    main()