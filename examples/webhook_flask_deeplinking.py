import sys
from flask import Flask, request
import telepot

try:
    from Queue import Queue
except ImportError:
    from queue import Queue

"""
$ python2.7 webhook_flask_deeplinking.py <bot_username> <token> <listening_port> <webhook_url>

Demonstrates deep linking.
- Open browser, visit: https://<base_url>/link
- Click on the link
- On Telegram conversation, click on the START button
- Bot should receive a message: /start ghijk
  where "ghijk" is the key embedded in the link, and the payload sent along with the /start command.
  You may use this key to identify the user, then his Telegram `chat_id`.
"""

key_id_map = { 'ghijk' : 123 }

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print 'Normal Message:', content_type, chat_type, chat_id

    if content_type == 'text':
        text = msg['text']
        print 'Text:', text

        if text.startswith('/start'):
            try:
                command, payload = text.split(' ')

                print 'Payload:', payload
                print 'User ID:', key_id_map[payload]
                print 'chat_id:', chat_id

            except ValueError:
                print 'No payload, or more than one chunk of payload'

            except KeyError:
                print 'Invalid key, no corresponding User ID'


BOT_USERNAME = sys.argv[1]
TOKEN = sys.argv[2]
PORT = int(sys.argv[3])
URL = sys.argv[4]

app = Flask(__name__)
bot = telepot.Bot(TOKEN)
update_queue = Queue()  # channel between `app` and `bot`

bot.notifyOnMessage(handle, source=update_queue)  # take updates from queue

@app.route('/link', methods=['GET', 'POST'])
def display_link():
    first_key_in_database = key_id_map.items()[0][0]
    return '<a href="https://telegram.me/%s?start=%s">Open conversation with bot</a>' % (BOT_USERNAME, first_key_in_database)

@app.route('/abc', methods=['GET', 'POST'])
def pass_update():
    update_queue.put(request.data)  # pass update to bot
    return 'OK'

if __name__ == '__main__':
    bot.setWebhook(URL)
    app.run(port=PORT, debug=True)
