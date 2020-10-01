# userinfo command
import tempfile
import os
import json

import core.user
import cmd.common

def userinfo_handler(update, context):

	# generate text
	info = dict(core.user.get_user_info(update))
	del info["_id"]
	text = json.dumps(info, indent=4)

	# dump to console or download a file
	tail = cmd.common.cmd_tail(update)
	if tail:
		update.message.reply_text(text)
	else:
		with tempfile.NamedTemporaryFile() as tmp:
			with open(tmp.name, 'w') as f:
				info = dict(core.user.get_user_info(update))
				del info["_id"]
				f.write(text)
			update.message.reply_document(open(tmp.name, 'rb'), filename="userinfo.json")
