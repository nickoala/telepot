import sys
import time
import threading
import telepot

"""
$ python3.4 skeleton_extend.py <token>

A skeleton for your telepot programs - extend from `Bot` and define handler methods as needed.
"""

class YourBot(telepot.Bot):
    def __init__(self, *args, **kwargs):
        super(YourBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print('Normal Message:', content_type, chat_type, chat_id)

    def on_inline_query(self, msg):
        def compute_answer():
            query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
            print('%s: Computing for: %s' % (threading.current_thread().name, query_string))

            articles = [{'type': 'article',
                            'id': 'abc', 'title': query_string, 'message_text': query_string}]

            return articles

        self._answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
        print('Chosen Inline Result:', result_id, from_id, query_string)


TOKEN = sys.argv[1]  # get token from command-line

bot = YourBot(TOKEN)
bot.notifyOnMessage()
print('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
