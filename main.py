# main.py

import time
import pyperclip

from config import CHECK_INTERVAL, UI_LOAD_WAIT
from ui_controller import open_chat_app, select_and_copy_chat, paste_and_send_message
from chat_reader import get_chat_history
from message_analyzer import should_reply
from ai_responder import generate_roast

def run_bot():
    print("[INFO] Naruto Auto-Reply Bot Started 🥷")
    open_chat_app()
    time.sleep(UI_LOAD_WAIT)

    while True:
        try:
            select_and_copy_chat()
            chat_text = get_chat_history()

            if chat_text and should_reply(chat_text):
                print("[INFO] Target user detected. Generating roast...")
                reply = generate_roast(chat_text)

                pyperclip.copy(reply)
                paste_and_send_message()

                print("[SENT]", reply)

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n[STOPPED] Bot manually terminated.")
            break

        except Exception as e:
            print("[ERROR]", e)
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
