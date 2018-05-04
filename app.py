from flask import Flask, request, abort

import tempfile
import os
import sys

from features.CarAnalytics import LicencePlate

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    ImageMessage, VideoMessage, AudioMessage,
    StickerMessage
)

import oil_price

app = Flask(__name__)

latest_image_path = ""

# น้องรถถัง
# line_bot_api = LineBotApi('Y2LM8a+jPmOBZRF2uiTeErE4rJAet1caN51/cjyTgGv2tsfCsJLhupNVAtaH5qaKEeloJPCuDqKpWLeoGaYUEqMpWKj5tQsnjz54crg6Ar88xdPhF9YTtV9pOnCwuKyGmOWXMnf/YqpxxX4Eo1o9EwdB04t89/1O/w1cDnyilFU=')
# handler = WebhookHandler('e0c9c1415d73e1480aac32ca1b4e01e1')

# อุ๋มอิ๋ม
line_bot_api = LineBotApi('OOsNsQLfne//a6O7Nz2AQfwSaIzk2kNMy2A3qaGQjvYWXxRYqItTnI5GP76cl2QMfpjkFSlohX/rJoCKFQ7dc+w6MJz8qs12iVzQ6sWONBnLIiUFp0dlALsvLUSJ3uOGH4F9/avOWY/BouEI3aZ1rQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('1fba0150b21dc471d820a51ea2c51098')


static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise


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
    except InvalidSignatureError as e:
        print("InvalidSignatureError:",e)
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    # Handle webhook verification
    print("Sticker Message")
    if event.reply_token == "ffffffffffffffffffffffffffffffff":
        return



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global latest_image_path

    # Handle webhook verification
    if event.reply_token == "00000000000000000000000000000000":
        return

    if event.message.text == 'ราคาน้ำมัน':
        l = oil_price.get_prices()
        s = ""
        for p in l:
            s += "%s %.2f บาท\n"%(p[0],p[1])

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=s))
    elif event.message.text == 'วิเคราะห์รูป':
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='สักครู่ค่ะ')
            ])

        # Process image
        try:
            lp = LicencePlate()
            result = lp.process(latest_image_path)
            s = lp.translate(result)

            line_bot_api.push_message(
                event.source.user_id, [
                    TextSendMessage(text=s)
                ])
        except Exception as e:
            print('Exception:',type(e),e)
            line_bot_api.push_message(
                event.source.user_id, [
                    TextSendMessage(text='ไม่สามารถวิเคราะห์รูปได้ค่ะ-')
                ])
            
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text+'จ้า'))

@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    global latest_image_path

    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    # Save image path
    latest_image_path = dist_path
    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='เก็บรูปให้แล้วค่ะ')
        ])



if __name__ == "__main__":
    app.run()