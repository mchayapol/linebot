# LINE BOT
สำหรับทดลองเขียน  LINE BOT

## Run The Bot
1. python app.py
2. ngrok http 5000
3. Verify webhook

## Make into script
```shell
export LINE_CHANNEL_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export LINE_CHANNEL_ACCESS_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
export FLASK_APP=app.py
export FLASK_DEBUG=1
flask run
```