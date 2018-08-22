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

NAME="makin"
PATH="/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin"
APPDIR="/home/Chayapol/linebot"
APPBIN="/usr/bin/python3"
APPARGS="app.py"
USER="root"
GROUP="root"


start-stop-daemon --start --chuid "$USER:$GROUP" --background --make-pidfile --pidfile /var/run/$NAME.pid --chdir "$APPDIR" --exec "$APPBIN" -- $APPARGS


NAME="ngrok"
PATH="/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin"
APPDIR="/home/Chayapol"
APPBIN="/usr/local/bin/ngrok"
APPARGS="http 5000"
USER="root"
GROUP="root"


start-stop-daemon --start --chuid "$USER:$GROUP" --background --make-pidfile --pidfile /var/run/$NAME.pid --chdir "$APPDIR" --exec "$APPBIN" -- $APPARGS