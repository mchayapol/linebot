from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import oil_price

app = Flask(__name__)

line_bot_api = LineBotApi('Y2LM8a+jPmOBZRF2uiTeErE4rJAet1caN51/cjyTgGv2tsfCsJLhupNVAtaH5qaKEeloJPCuDqKpWLeoGaYUEqMpWKj5tQsnjz54crg6Ar88xdPhF9YTtV9pOnCwuKyGmOWXMnf/YqpxxX4Eo1o9EwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('e0c9c1415d73e1480aac32ca1b4e01e1')

@app.route("/", methods=['GET'])
def default_action():
    l = oil_price.get_prices()
    s = ""
    for p in l:
        s += "%s %f บาท\n"%(p[0],p[1])
    return s

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == 'ราคาน้ำมัน':
        l = oil_price.get_prices()
        s = ""
        for p in l:
            s += "%s %.2f บาท\n"%(p[0],p[1])

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=s))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text+'ค่ะ'))


if __name__ == "__main__":
    app.run()