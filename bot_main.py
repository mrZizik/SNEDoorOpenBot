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
ser = serial.Serial('/dev/ttyUSB1', 9600)


global bot 
bot = telegram.Bot(token=TOKEN) 

def load_whitefile():
    whitefile = open("whitelist",'rt')
    whitelist = whitefile.readline().strip().split(",")
    whitefile.close()
    print( str(whitelist) )
    return whitelist

whitelist = load_whitefile()

#Вот на эту часть кода мы подключим вебхук 
@app.route('/HOOK', methods=['POST', 'GET']) 
def webhook_handler():
    if request.method == "POST": 
        update = telegram.Update.de_json(request.get_json(force=True))
        try:
            whitelist = load_whitefile()
            chat_id = update.message.chat.id 
            text = update.message.text
            username = update.message.from_user.username
            text = text.lower()
            print( "Got message from {}: {}".format( username, text ) )
            if text == "/help":
                bot.sendMessage(chat_id=chat_id, text='SNE 2016-17 MAKES US CRY \n/add <password> - Add to whitelist \nPress <anykey> or /open to open the door \n/list - List all with open magic')
            elif text.startswith("/add"):
                if username in whitelist:
                    bot.sendMessage(chat_id=chat_id, text='Already in whitelist')
                elif len(text.split(" "))==2 and HASH == hashlib.sha512(SALT + text.split(" ")[1]).hexdigest():
                    whitelist.append(username)
                    whitefile = open("whitelist",'wt')
                    whitefile.write( ','.join(whitelist) )
                    whitefile.close()
                    bot.sendMessage(chat_id=chat_id, text='Added to whitelist')
                else:
                    bot.sendMessage(chat_id=chat_id, text='YOU SHALL NOT PASS!')
            elif text == "/list":
                bot.sendMessage(chat_id=chat_id, text="@" + "\n@".join(whitelist[0:]))
            else:
                print( "Searching {} in {}...".format( username, str( whitelist ) ), );
                if username in whitelist:
                    print( "OK" )
                    ser.write(b'o')
                    bot.sendMessage(chat_id=chat_id, text='Door opened')
                else:
                    print( "NO" )
                    bot.sendMessage(chat_id=chat_id, text='Speak \'friend\' and enter. What\'s the Elvish word for friend?')
        except Exception, e:
            print e
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
