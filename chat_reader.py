# chat_reader.py

import pyperclip

def get_chat_history():
    text = pyperclip.paste()
    if not text:
        return ""
    return text.strip()
