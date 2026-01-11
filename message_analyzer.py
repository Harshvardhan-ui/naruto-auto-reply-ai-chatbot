# message_analyzer.py

from config import TARGET_USER

def get_last_sender(chat_text):
    lines = [line.strip() for line in chat_text.split("\n") if line.strip()]
    if not lines:
        return None

    last_line = lines[-1]

    if ":" in last_line:
        sender = last_line.split(":")[0].strip()
        return sender

    return None

def should_reply(chat_text):
    sender = get_last_sender(chat_text)
    return sender == TARGET_USER
