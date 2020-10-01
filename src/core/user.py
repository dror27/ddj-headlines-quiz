# handler user info

import hashlib
import core.db

def user_sha(update):

    if update.effective_chat.username:
        prefix = "u-"
        username = update.effective_chat.username
    else:
        prefix = "c-"
        username = str(update.effective_chat.id)

    return prefix + hashlib.sha256(username.encode()).hexdigest()

def get_user_info(update):

    uid = user_sha(update)

    info = core.db.get_db().users.find_one({"uid": uid})
    if not info:
        info = {
            "uid": uid,
        }
    if not "quizs" in info:
        info["quizs"] = 0
    if not "sources" in info:
        info["sources"] = [1,2,3,4]

    return info

def set_user_info(update, info):

    uid = user_sha(update)

    key = {"uid": uid}
    core.db.get_db().users.replace_one(key, info, True)

