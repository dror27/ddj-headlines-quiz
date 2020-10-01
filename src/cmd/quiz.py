# quiz command

from telegram import (Poll)


import cmd.common
import core.user
import core.quiz_builder

def quiz(update, context, qs=2):

    info = core.user.get_user_info(update)
    info["quizs"] = info["quizs"] + 1

    # extract keyword text or get it from user info
    keyword = cmd.common.cmd_tail(update)
    if keyword:
        if keyword == "0":
            info["keyword"] = ""
            keyword = None
        else:
            info["keyword"] = keyword
    elif "keyword" in info and info["keyword"]:
        keyword = info["keyword"]
    
    q = core.quiz_builder.build_heading_quiz(qs, keyword=keyword, sources_subset=info["sources"])
    if not q:
        q = core.quiz_builder.build_default_quiz()
        
    questions = q["sources"]
    prefix = "Where was this heading published?\n\n"  if info["quizs"] <= 3 else ""
    message = update.effective_message.reply_poll(prefix + q["title"],
                                                  questions, type=Poll.QUIZ, correct_option_id=q["index"])
    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    payload = {message.poll.id: {"chat_id": update.effective_chat.id,
                                 "message_id": message.message_id,
                                 "q": q,
                                 "qs": qs}}
    context.bot_data.update(payload)
    core.user.set_user_info(update, info)

def quiz_post_timer(context):
    quiz_data = context.job.context
    msg = ""
    if quiz_data["q"]["link"]:
        msg += quiz_data["q"]["link"] + "\n\n"
    context.bot.send_message(quiz_data["chat_id"], text=msg + "/quiz, /quiz3, /quiz4 or /help")  
            

def receive_quiz_answer(update, context):
    # the bot can receive closed poll updates we don't care about
    if update.poll.is_closed:
        return
    if update.poll.total_voter_count == 3:
        try:
            quiz_data = context.bot_data[update.poll.id]
        # this means this poll answer update is from an old poll, we can't stop it then
        except KeyError:
            return
        context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])
        
    if update.poll:
        quiz_data = context.bot_data[update.poll.id]
        chat_id = quiz_data["chat_id"]
        new_job = context.job_queue.run_once(quiz_post_timer, 2, context=quiz_data)
