# sources command

import cmd.common
import core.db
import core.user

def domain_handler(update, context):

	domains = core.db.db_domains()
	info = core.user.get_user_info(update)
	domain = core.user.get_user_domain(info)

	# parse optional command
	tail = cmd.common.cmd_tail(update)
	if tail and tail in domains:
		domain = tail
		core.user.set_user_domain(info, domain)
		core.user.set_user_info(update, info)			

	# establish others
	if domain in domains:
		domains.remove(domain)

	# output (user) domain
	msg = "current: %s\nothers available: %s" % (domain, ", ".join(domains))
	update.message.reply_text(msg)