# sources command

import cmd.common
import core.db
import core.user

def sources_handler(update, context):

	sources = core.db.db_sources()
	info = core.user.get_user_info(update)
	msg = ""

	# parse optional command
	tail = cmd.common.cmd_tail(update)
	if tail:
		new_sources = []
		for tok in tail.split(' '):
			if tok.isdigit():
				i = int(tok)
				i = ((i - 1) % len(sources) + 1) if i > 0 else 0
				new_sources .append(i)

		# set back in info
		if 0 in new_sources:
			info["sources"] = []
			core.user.set_user_info(update, info)			
		elif len(new_sources) >= 2:
			info["sources"] = new_sources
			core.user.set_user_info(update, info)			
		else:
			msg += "Please specify at least two sources\n\n"

	# output (user) sources
	index = 0
	for source in sources:
	    index = index + 1;
	    marker = "*" if index in info["sources"] else ""
	    msg += (str(index) + marker + " " + source["name"] + " - " + source["rss"] + "\n")
	update.message.reply_text(msg)