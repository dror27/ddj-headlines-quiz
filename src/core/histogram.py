# histogram stuff

import numpy as np
import datetime
from pprint import pprint
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import tempfile
import os
import time
import io

import core.db
import core.time

limitcount = 30

def wordcount(s):
	return len(s) - len(s.replace(" ", ""))

def histogram_count_data(domain, since):
	data = {}
	for h in core.db.db_headings_iter(domain, since):
		count = wordcount(h["title"])
		source = h["_source"]["name"]
		if count  > limitcount:
			count = limitcount 
		if not source in data:
			data[source] = np.zeros(limitcount + 1)
		data[source][count] += 1

	for _, d in data.items():
		d /= np.sum(d)

	return data

def histogram_plot(data, title, file):
	plt.clf()
	plt.bar(range(len(data)), data,  width=1.0)
	plt.xlabel("headline words")
	plt.ylabel("percentage")
	plt.title(title)
	axes = plt.gca()
	axes.set_ylim([0.0,0.35])
	axes.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: "%d%%" % int((x * 100))))
	plt.savefig(file, format="png")

def main():
	since = datetime.datetime.min
	sources_data = histogram_count_data("uknews", since)
	for source, data in sources_data.items():
			with io.BytesIO() as buf:
				histogram_plot(data,  source , buf)
				buf.seek(0)
				break

def main2():
	since = datetime.datetime.min
	sources_data = histogram_count_data("uknews", since)
	for source, data in sources_data.items():
			file = "/tmp/hist.png"
			histogram_plot(data,  source , file)
			pprint(file)
			os.system("open " + file)
			break


if __name__ == '__main__':
    main()