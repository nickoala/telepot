import sys
from flask import Flask, request
import telepot

try:
    from Queue import Queue
except ImportError:
    from queue import Queue

"""
$ python2.7 webhook_flask_skeleton.py <token> <listening_port> <webhook_url>
"""

def handle(msg):
    print msg
    content_type, chat_type, chat_id = telepot.glance2(msg)
    print content_type, chat_type, chat_id


TOKEN = sys.argv[1]
PORT = int(sys.argv[2])
URL = sys.argv[3]

app = Flask(__name__)
bot = telepot.Bot(TOKEN)
update_queue = Queue()  # channel between `app` and `bot`

bot.notifyOnMessage(handle, source=update_queue)  # take updates from queue

@app.route('/abc', methods=['GET', 'POST'])
def pass_update():
    update_queue.put(request.data)  # pass update to bot
    return 'OK'

if __name__ == '__main__':
    bot.setWebhook(URL)
    app.run(port=PORT, debug=True)
