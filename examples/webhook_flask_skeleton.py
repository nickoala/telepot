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
    flavor = telepot.flavor(msg)

    # normal message
    if flavor == 'normal':
        content_type, chat_type, chat_id = telepot.glance(msg)
        print 'Normal Message:', content_type, chat_type, chat_id

        # Do your stuff according to `content_type` ...

    # inline query - need `/setinline`
    elif flavor == 'inline_query':
        query_id, from_id, query_string = telepot.glance(msg, flavor=flavor)
        print 'Inline Query:', query_id, from_id, query_string

        # Compose your own answers
        articles = [{'type': 'article',
                        'id': 'abc', 'title': 'ABC', 'message_text': 'Good morning'}]

        bot.answerInlineQuery(query_id, articles)

    # chosen inline result - need `/setinlinefeedback`
    elif flavor == 'chosen_inline_result':
        result_id, from_id, query_string = telepot.glance(msg, flavor=flavor)
        print 'Chosen Inline Result:', result_id, from_id, query_string

        # Remember the chosen answer to do better next time

    else:
        raise telepot.BadFlavor(msg)


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
