from flask import Flask, request, abort

import tempfile
import os
import sys

from features.CarAnalytics import LicencePlate

from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)

from dialog.intent.Registration import (
    Registration
)

from linebot.models import (
    MessageEvent, TextMessage, 
    TextSendMessage, ImageSendMessage,
    ImageMessage, VideoMessage, AudioMessage,
    StickerMessage, StickerSendMessage,
    JoinEvent,
    SourceGroup
)

import firebase_admin
from firebase_admin import (
    credentials, db
)
import json

import oil_price

app = Flask(__name__)

latest_image_path = ""

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

cred = credentials.Certificate('study-room-firebase-service-account.json')
default_app = firebase_admin.initialize_app(cred,
{
    'databaseURL': 'https://stellar-utility-840.firebaseio.com/'
})

conversation = {}

# น้องรถถัง
# line_bot_api = LineBotApi('Y2LM8a+jPmOBZRF2uiTeErE4rJAet1caN51/cjyTgGv2tsfCsJLhupNVAtaH5qaKEeloJPCuDqKpWLeoGaYUEqMpWKj5tQsnjz54crg6Ar88xdPhF9YTtV9pOnCwuKyGmOWXMnf/YqpxxX4Eo1o9EwdB04t89/1O/w1cDnyilFU=')
# handler = WebhookHandler('e0c9c1415d73e1480aac32ca1b4e01e1')

# อุ๋มอิ๋ม
# line_bot_api = LineBotApi('OOsNsQLfne//a6O7Nz2AQfwSaIzk2kNMy2A3qaGQjvYWXxRYqItTnI5GP76cl2QMfpjkFSlohX/rJoCKFQ7dc+w6MJz8qs12iVzQ6sWONBnLIiUFp0dlALsvLUSJ3uOGH4F9/avOWY/BouEI3aZ1rQdB04t89/1O/w1cDnyilFU=')
# handler = WebhookHandler('1fba0150b21dc471d820a51ea2c51098')


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

def saveToFirebase(event):
    ref = db.reference('/chatlog')
    ref.push(json.loads(event.as_json_string()))
        

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

    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id
        )
    )

@handler.add(JoinEvent)
def handle_join(event):
    # group_id = event.source.group_id
    # line_bot_api.get_group_member_profile(group_id,member_id)
    # member_ids_res = line_bot_api.get_group_member_ids(group_id)
    # print(member_ids_res.member_ids)
    # print(member_ids_res.next)

    try:
        profile = line_bot_api.get_group_member_profile(
            event.source.group_id,
            'U53199750dbac026a2bd87a094472ddf1'
        )
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text='สวัสดีค่า'),
                StickerSendMessage(
                    package_id=1,
                    sticker_id=2
                )
            ]
        )        
    except LineBotApiError as e:
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text='หัวหน้าไม่อยู่ในห้องนี้\nไปละค่ะ\nบัย'),
            ]
        )
        line_bot_api.leave_group(event.source.group_id)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global latest_image_path

    # Handle webhook verification
    if event.reply_token == "00000000000000000000000000000000":
        return

    saveToFirebase(event)

    # Resume existing intent
    print(conversation.keys())
    uid = event.source.user_id
    if uid in conversation:
        intent = conversation[uid]
        o = intent.handle(event.message.text)
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=o)
            ]
        )
        if intent.endIntent():
            output = intent.getData()
            print(output)
            del conversation[uid]
        return

    if event.message.text == 'register':
        uid = event.source.user_id
        rego = None

        if uid in conversation:
            rego = conversation[uid]
        else:
            rego = Registration()
            conversation[uid] = rego

        o = rego.handle(event.message.text)
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=o)
            ]
        )
        
    elif event.message.text == 'ออกไปได้แล้ว':
        if isinstance(event.source,SourceGroup):
            if event.source.user_id == 'U53199750dbac026a2bd87a094472ddf1':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextMessage(text='บะบายค่า')
                )
                line_bot_api.leave_group(event.source.group_id)
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextMessage(text='ไม่!')
                )
                
    elif event.message.text == 'profile':
        user_id = event.source.user_id
        profile = line_bot_api.get_profile(user_id)
        # image_message = ImageSendMessage(
        #             original_content_url=profile.picture_url,
        #             preview_image_url=profile.picture_url
        #         )

        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=profile.display_name),
                TextSendMessage(text=profile.user_id),
                TextSendMessage(text=profile.picture_url),
                TextSendMessage(text=profile.status_message),
                # image_message
            ]
        )
    elif event.message.text == 'ราคาน้ำมัน':
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