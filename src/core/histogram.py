# histogram stuff

import numpy as np
import datetime
from pprint import pprint
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.pyplot import figure
import matplotlib
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

	# determine average
	avg = round(np.sum(data * range(len(data))), 1)

	plt.clf()
	plt.bar(range(len(data)), data,  width=1.0)
	plt.xlabel("headline words, %.1f on average" % avg)
	plt.ylabel("percentage")
	plt.title(title)
	axes = plt.gca()
	axes.set_ylim([0.0,0.35])
	axes.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: "%d%%" % int((x * 100))))
	plt.savefig(file, format="png")

def histogram_plot_all(sources_data, title, file):
	plt.clf()

	sources = list(sources_data.keys())
	cols = 3
	rows = len(sources) // cols + (1 if (len(sources) % cols) else 0)
	while len(sources) % cols:
		bins = len(sources_data[sources[0]])
		sources.append("")
		sources_data[""] = np.zeros(bins)

	fig, axs = plt.subplots(rows, cols)
	fig.suptitle(title)
	for i in range(len(sources_data)):
		row = i // cols
		col = i % cols
		source = sources[i]
		data = sources_data[source]
		avg = round(np.sum(data * range(len(data))), 1)
		axs[row, col].bar(range(len(data)), data,  width=1.0)
		if source:
			axs[row, col].set_title("%s - %.1f" % (source, avg))
		axs[row, col].set_ylim([0.0,0.35])
		axs[row, col].get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda x, p: "%d%%" % int((x * 100))))

	for ax in axs.flat:
	    ax.set(xlabel='', ylabel='')

	for ax in axs.flat:
		ax.label_outer()

	fig = matplotlib.pyplot.gcf()
	fig.set_size_inches(10, 10)
	plt.savefig(file, format="png")


def main1():
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

def main():
	since = datetime.datetime.min
	sources_data = histogram_count_data("uknews", since)
	file = "/tmp/hist.png"
	title = "headlines wordcount, since %s" % since.strftime("%y%m%d")
	histogram_plot_all(sources_data , title, file)
	pprint(file)
	os.system("open " + file)

if __name__ == '__main__':
    main()