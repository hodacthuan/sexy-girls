import telegram
import os
from sexybaby import constants


def sendMessage(message):
    autoBot = telegram.Bot(token=constants.TELEGRAM_TOKEN)
    autoBot.send_message(chat_id=constants.TELEGRAM_CHAT_ID, text=message)
