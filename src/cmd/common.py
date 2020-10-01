# common command utils

def cmd_tail(update):
    text = update.effective_message.text
    toks = text.split(' ', 1)
    return toks[1] if len(toks) > 1 else None
