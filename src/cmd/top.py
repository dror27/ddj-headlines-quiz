# sources command

import cmd.common
import core.db
import core.user
import core.rss
import datetime
from pprint import pprint

def top_handler(update, context):

	info = core.user.get_user_info(update)
	domain = core.user.get_user_domain(info)
	keyword  = info["keyword"] if "keyword" in info  else None
	limit = 10

	tail = cmd.common.cmd_tail(update)
	if tail:
		if tail.isnumeric():
			limit = int(tail)
		else:
			keyword = tail

	top = build_top(domain, keyword=keyword, limit=limit)
	if not top:
		top = "no headlines found."
	update.message.reply_text(top, parse_mode="Markdown", disable_web_page_preview=True)

def tops_handler(update, context):

	info = core.user.get_user_info(update)
	domain = core.user.get_user_domain(info)
	keyword  = info["keyword"] if "keyword" in info  else None
	limit = 2

	tail = cmd.common.cmd_tail(update)
	if tail:
		if tail.isnumeric():
			limit = int(tail)
		else:
			keyword = tail

	top = ""
	for source in core.db.db_sources(domain):
		top += "*%s:*\n" % source["name"]
		top += build_top(domain, keyword=keyword, limit=limit, source=source["name"], prefix="- ")
		top += "\n"


	if not top:
		top = "no headlines found."
	update.message.reply_text(top, parse_mode="Markdown", disable_web_page_preview=True)

def build_top(domain, keyword=None, source=None, limit=10, prefix=""):
	top = ""
	for h in core.db.db_top_headings_iter(domain, keyword=keyword, source=source):
		#pprint(h)
		top += '%s%s: %s - [%s](%s)\n' % \
			(prefix, h["_timestamp"].strftime("%H:%M:%S"), h["title"], h["_source"]["name"], core.rss.get_entry_link(h))
		limit -= 1
		if not limit:
			break

	return top


def main():
	top = build_top("uknews", limit=10)
	print(top)

if __name__ == '__main__':
    main()

