import sys
from flask import Flask, request
import telepot
from telepot.delegate import per_chat_id, create_open

try:
    from Queue import Queue
except ImportError:
    from queue import Queue

"""
$ python3.4 webhook_flask_counter.py <token> <listening_port> <webhook_url>
"""

class MessageCounter(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(MessageCounter, self).__init__(seed_tuple, timeout)
        self._count = 0

    def on_message(self, msg):
        self._count += 1
        self.sender.sendMessage(self._count)


TOKEN = sys.argv[1]
PORT = int(sys.argv[2])
URL = sys.argv[3]

app = Flask(__name__)
update_queue = Queue()  # channel between `app` and `bot`

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(MessageCounter, timeout=10)),
])
bot.notifyOnMessage(source=update_queue)  # take updates from queue

@app.route('/abc', methods=['GET', 'POST'])
def pass_update():
    update_queue.put(request.data)  # pass update to bot
    return 'OK'

if __name__ == '__main__':
    bot.setWebhook(URL)
    app.run(port=PORT, debug=True)
