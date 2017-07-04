# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals

import os
import sys
import string
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ConfirmTemplate, MessageTemplateAction
)

from pymongo import MongoClient


app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

regist_waiting_user = []
regist_info = []

@app.route("/callback", methods=['POST'])
def callback():
    global regist_waiting_user
    global regist_info

    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue

        if str(event.message.type) == 'text':
            msg = event.message.text.lower().split()
            d = None
            n = None
            for i in xrange(len(msg)):
                if msg[i] == 'link' or msg[i] == 'unlink':
                    d = msg[i+1]
                if msg[i] == 'as':
                    n = msg[i+1]

            if d and n:
                print d, n
                client = MongoClient()
                db = client['iot-project']
                collection = db[event.source.user_id]
                q = collection.find()

                text = None

                for i in q:
                    if i['device'] == d:
                        text = "Your device is already linked"

                if text:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=text)
                    )

                else:
                    text = 'Are you sure to link ' + str(d) + ' as ' + str(n) + '?'
                    alt_text=text + ' (Yes/No)'

                    regist_waiting_user.append(event.source.user_id)
                    regist_info.append((event.source.user_id, str(d), str(n)))

                    confirm_template = ConfirmTemplate(text=text, actions=[
                        MessageTemplateAction(label='Yes', text='Yes'),
                        MessageTemplateAction(label='No', text='No'),
                    ])

                    template_message = TemplateSendMessage(alt_text=alt_text, template=confirm_template)

                    line_bot_api.reply_message(
                        event.reply_token,
                        template_message
                    )

            if not n and d:
                print 'unlink request'
                client = MongoClient()
                db = client['iot-project']
                collection = db[event.source.user_id]
                q = collection.find()

                text = None
                target = None

                for i in q:
                    if i['device'] == d:
                        target = i['_id']

                if not target:
                    text = "No device found"
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=text)
                    )

                else:
                    result = collection.delete_many({'_id': target})
                    print result.deleted_count
                    text = "Unlinked"
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=text)
                    )

            elif msg[0] == "yes" and event.source.user_id in regist_waiting_user:
                regist_waiting_user.remove(event.source.user_id)
                info = regist_info.pop()
                #registed_user.append(event.source.user_id)
                client = MongoClient()
                db = client['iot-project']
                collection = db[event.source.user_id]
                data = {'device': info[1],
                        'alias': info[2]}
                collection.insert_one(data)
                text = "Your device has linked with this Line account, you could moniter your sensing data via " + vis_url + " at any moment!"
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=text)
                )

            elif msg[0] == "no" and event.source.user_id in regist_waiting_user:
                regist_waiting_user.remove(event.source.user_id)
                text = "That's OK! you could regist anytime you like, but you probably could not access the services so far :("
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=text)
                )

            elif "!list" in msg:
                client = MongoClient()
                db = client['iot-project']
                collection = db[event.source.user_id]
                data = collection.find()
                text = ""
                for i in data:
                    text += str(i)

                if len(text) < 5:
                    text = "No devices found"

                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=text)
                )

            else:
                print event.message.type
                print type(event.message.type)
                text = 'Message: ' + event.message.text + ' from ' + event.source.user_id
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=text)
                )

    return 'OK'


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
