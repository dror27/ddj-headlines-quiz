#!/usr/bin/env python
# coding: utf-8

from pymongo import MongoClient
import feedparser
from pprint import pprint
import datetime
import random
import logging
import os

from telegram import (Poll, ParseMode, KeyboardButton, KeyboardButtonPollType,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, PollAnswerHandler, PollHandler, MessageHandler,
                          Filters)

import cmd.start
import cmd.quiz
import cmd.help
import cmd.sources
import cmd.domain
import cmd.userinfo
import cmd.download


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

                              
def main():
    logger.info("creating updater")
    updater = Updater(os.environ['TEL_BOT_TOKEN'], use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', cmd.start.start))
    
    dp.add_handler(CommandHandler('quiz', cmd.quiz.quiz))
    dp.add_handler(CommandHandler('q', cmd.quiz.quiz))
    dp.add_handler(CommandHandler(['quiz2', 'q2'], lambda update,context: cmd.quiz.quiz(update, context, 2)))
    dp.add_handler(CommandHandler(['quiz3', 'q3'], lambda update,context: cmd.quiz.quiz(update, context, 3)))
    dp.add_handler(CommandHandler(['quiz4', 'q4'], lambda update,context: cmd.quiz.quiz(update, context, 4)))
    dp.add_handler(PollHandler(cmd.quiz.receive_quiz_answer))
                              
    dp.add_handler(CommandHandler(['help', 'h'], cmd.help.help_handler))
    dp.add_handler(CommandHandler('short', cmd.help.short_handler))
    dp.add_handler(CommandHandler('credits', cmd.help.credits_handler))
    dp.add_handler(CommandHandler('qr', cmd.download.qr_handler))
    dp.add_handler(CommandHandler('wc', cmd.download.wc_handler))
    dp.add_handler(CommandHandler('wcm', cmd.download.wc_movie_handler))
    dp.add_handler(CommandHandler('hd', cmd.download.headings_handler))
    dp.add_handler(CommandHandler('sources', cmd.sources.sources_handler))
    dp.add_handler(CommandHandler('domain', cmd.domain.domain_handler))
    dp.add_handler(CommandHandler('userinfo', cmd.userinfo.userinfo_handler))
    dp.add_handler(CommandHandler('hist', cmd.download.histograms_handler))

    logger.info("starting to poll")
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    print('Bot starting ...')
    main()
