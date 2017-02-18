#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
from __future__ import unicode_literals 

import site 
import os.path 
import logging 
import json
site.addsitedir(os.path.join(os.path.dirname(__file__), 'libs')) 

import telegram 
from flask import Flask, request

#URL, CERT, TOKEN, PASSWORD_HASH
from secret import *

app = Flask(__name__) 


# serial
import serial
ser = serial.Serial('/dev/ttyUSB0', 9600)


global bot 
bot = telegram.Bot(token=TOKEN) 

whitelist = [103823343, 115199937, 142509377, 187493679, 25437788, 79338539, 83683719]

#Вот на эту часть кода мы подключим вебхук 
@app.route('/HOOK', methods=['POST', 'GET']) 
def webhook_handler():
    if request.method == "POST": 
        update = telegram.Update.de_json(request.get_json(force=True))
        chat_id = update.message.chat.id 
        text = update.message.text
        text = text.lower()
        print text
        if text == "/help":
            pass
        elif text.startswith("/add"):
            if len(text.split(" "))==2 and hashlib.sha512(SALT + text.split(" ")[1]).hexdigest():
                whitelist.append(chat_id)
                bot.sendMessage(chat_id=chat_id, text='Added to whitelist')
            else:
                bot.sendMessage(chat_id=chat_id, text='YOU SHALL NOT PASS!')
        else:
            if chat_id in whitelist:
                ser.write(b'o')
                bot.sendMessage(chat_id=chat_id, text='Door opened')
            else:
                bot.sendMessage(chat_id=chat_id, text='Speak \'friend\' and enter. What\'s the Elvish word for friend?')
    return 'ok' 

#А вот так подключается вебхук 
@app.route('/set_webhook', methods=['GET', 'POST']) 
def set_webhook(): 
    s = bot.setWebhook('https://%s:8443/HOOK' % URL, certificate=open('server.crt', 'rb')) 
    if s:
        print(s)
        return "webhook setup ok" 
    else: 
        return "webhook setup failed" 

@app.route('/') 
def index(): 
    return '.' 


app.run(host= '0.0.0.0', port=8443, debug=True, ssl_context=context)
