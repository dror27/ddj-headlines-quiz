# help command

import os

def help_handler(update, context):
    update.message.reply_text(
"""
/quiz - get a quiz\n
/quiz3 - get a quiz with 3 answers
/quiz4 - get a quiz with 4 answers
/help - get this help message
/short - list shortcuts

/sources - list sources
/sources 1 2 4 7 - set preferred sources to 1 2 3 and 7
/sources 0 - reset sources to all

/credits - list credits
/userinfo - download your user info
/qr - get a qr code to the bot
""")

def short_handler(update, context):
    update.message.reply_text(
"""
/q - /quiz
/q3 - /quiz3
/q4 - /quiz4

/q <keyword> - filter for keyword
/q 0 - cancel filter

/qr - send qr code

/h - /help
""")

def credits_handler(update, context):
    update.message.reply_text(
"""
- rss information: public rss feeds
- uknews list of rss sources: feedburner

contact: @drorkessler
""")

def qr_handler(update, context):
    for path in [".", "../data"]:
      fname = path + "/qr-code.png"
      if os.path.isfile(fname):
        update.message.reply_photo(open(fname, 'rb'))
        break

