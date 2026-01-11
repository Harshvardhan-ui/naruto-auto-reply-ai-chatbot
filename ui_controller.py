# ui_controller.py

import pyautogui
import time
from config import CHAT_AREA_START, CHAT_AREA_END, CHAT_INPUT_BOX

pyautogui.FAILSAFE = True

def open_chat_app():
    time.sleep(3)  # manual open or extend logic later

def select_and_copy_chat():
    pyautogui.moveTo(CHAT_AREA_START)
    pyautogui.dragTo(CHAT_AREA_END, duration=1.2, button="left")
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.5)

def paste_and_send_message():
    pyautogui.click(CHAT_INPUT_BOX)
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.2)
    pyautogui.press("enter")
