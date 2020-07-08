#!/usr/bin/python

import sys
import telegram
import logging

from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.filters import Filters


import paho.mqtt.client as mqtt
import threading
import signal

import config as cfg


#logging.basicConfig(
#        level=logging.DEBUG,
#        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#        )


#
#MQTT
#
class MqttClient():

    def __init__(self, callback):

        self.exit = False
        self.callback = callback
        
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(
                cfg.MQTT_BROKER_ADDR, 
                cfg.MQTT_BROKER_PORT, 
                cfg.MQTT_BROKER_TIMEOUT
                )
        
        self.main_thread = threading.Thread(target=self.mqtt_thread_body)
        self.main_thread.start()
        return


    def on_connect(self, client, userdata, flags, rc):
        """
        The callback for when the client receives a CONNACK response from the server.
        """
        
        print("Connected with result code {}".format(rc))
    
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        #self.client.subscribe("/CANE")
        return
    
    
    def on_message(self, client, userdata, msg):
        """
        The callback for when a PUBLISH message is received from the server.
        """
        self.callback(msg)
        return


    def publish(self, topic, msg):
        self.client.publish(topic, msg)
        return
    
    
    def mqtt_thread_body(self):
        while not self.exit:
            self.client.loop()
        return


    def close(self):
        self.client.disconnect()
        self.exit = True
        self.main_thread.join()
        return


class TelegramClient():

    def __init__(self, callback):

        self.callback = callback
        
        keyboard = [
                [
                    InlineKeyboardButton("Open", callback_data='open'),
                #    InlineKeyboardButton("Option 2", callback_data='2')
                ],
                #[
                #    InlineKeyboardButton("Option 3", callback_data='3')
                #]
        ]
        self.reply_markup = InlineKeyboardMarkup(keyboard)
        
        self.updater = Updater(
                token=cfg.TELEGRAM_API_KEY, 
                use_context=True
                )
        self.dispatcher = self.updater.dispatcher
        
        chat_filter = Filters.chat(chat_id=cfg.ALLOWED_CHAT)
        user_filter = Filters.user(cfg.ALLOWED_USERS)

        self.start_handler = CommandHandler("start", self.start_cmd)
        self.open_handler = CommandHandler(
                "open", 
                self.open_cmd, 
                filters=(chat_filter and user_filter)
                )
        
        self.dispatcher.add_handler(self.start_handler)
        self.dispatcher.add_handler(self.open_handler)

        self.dispatcher.add_handler(CallbackQueryHandler(self.button_callback))

        self.main_thread = threading.Thread(target=self.thread_body)
        self.main_thread.start()
        return


    def thread_body(self):
        #while not self.exit:
        self.updater.start_polling()
        return


    def close(self):
        self.exit = True
        self.updater.stop()
        self.main_thread.join()
        return


    def start_cmd(self, update, context):
        self.send_help_message(update, context)
        return
    

    def open_cmd(self, update, context):

        context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="Opening"
                )
        
        self.callback()        
        return


    def button_callback(self, update, context):
        
        query = update.callback_query

        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        query.answer()
        
        self.callback()

        query.edit_message_text(text="Opening")
        self.send_help_message(update, context)
        return


    def send_help_message(self, update, context):
        context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="Touch to open",
                reply_markup=self.reply_markup
                )
        return


def received(msg):
    print("mqtt message received")
    print("receiverd on {} msg: {}".format(msg.topic, msg.payload))
    return


def received_telegram():
    MQTT_OBJ.publish(cfg.CMD_TOPIC, "TOGGLE")
    return


def signal_handler(sig, frame):
    print("ctrl-c received")
    my_exit()
    return


def my_exit(): 
    MQTT_OBJ.close()
    if TEL_OBJ is not None:
        TEL_OBJ.close()
    sys.exit(0)
    return


if __name__ == "__main__":

#    bot = telegram.Bot(token=TELEGRAM_API_KEY)
#    print(bot.get_me())
#    sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    MQTT_OBJ = MqttClient(received)
    TEL_OBJ = TelegramClient(received_telegram)
    
    #import time
    #time.sleep(5)
    
    signal.pause()
    
    my_exit()
