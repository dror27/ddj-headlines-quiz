# start command

import cmd.quiz

def start(update, context):
    update.message.reply_text("Headings Quiz Bot, (c) Dror Kessler 2020\n"
                              "headings sources from public rss feeds\n"
                              "\n"
                              "Please select /quiz or /help for more commands")
    new_job = context.job_queue.run_once(start_post_timer, 2, context=update)

def start_post_timer(context):
    update = context.job.context
    chat_id = update.effective_chat.id
    cmd.quiz.quiz(update, context)
