# handler user info

import hashlib
import core.db

def user_sha(username):
   return hashlib.sha256(username.encode()).hexdigest()

def get_user_info(update):

    uid = user_sha(update.effective_chat.username)

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

    uid = user_sha(update.effective_chat.username)

    key = {"uid": uid}
    core.db.get_db().users.replace_one(key, info, True)

