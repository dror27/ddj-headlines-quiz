# help command

def help_handler(update, context):
    update.message.reply_text(
"""
/quiz - get a quiz
/quiz3 - get a quiz with 2 answers
/quiz3 - get a quiz with 3 answers
/quiz4 - get a quiz with 4 answers
/help - get this help message
/short - list shortcuts

/sources - list sources
/sources 1 2 4 7 - set preferred sources to 1 2 3 and 7
/sources 0 - reset sources to all

/domain - show current domain, list available
/domain <name> - set current domain

/credits - list credits
/userinfo - download your user info
/qr - get a qr code to the bot
""")

def short_handler(update, context):
    update.message.reply_text(
"""
/q - /quiz
/q2 - /quiz2
/q3 - /quiz3
/q4 - /quiz4

/q <keyword> - filter for keyword
/q 0 - cancel filter

/qr - send qr code
/wc - generate a wordcloud

/h - /help
""")

def credits_handler(update, context):
    update.message.reply_text(
"""
- rss information: public rss feeds
- uknews list of rss sources: feedburner

contact: @drorkessler
""")


