import telegram
import os
from sexybaby.constants import *


def sendMessage(message):
    autoBot = telegram.Bot(token=TELEGRAM_TOKEN)
    autoBot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
