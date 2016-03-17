import sys
import time
import threading
import telepot

"""
$ python2.7 skeleton.py <token>

A skeleton for your telepot programs.
"""

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print 'Chat Message:', content_type, chat_type, chat_id


def on_inline_query(msg):
    def compute_answer():
        query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
        print '%s: Computing for: %s' % (threading.current_thread().name, query_string)

        articles = [{'type': 'article',
                         'id': 'abc', 'title': query_string, 'message_text': query_string}]
        return articles

        # You may control positional arguments to bot.answerInlineQuery() by returning a tuple
        # return (articles, 60)

        # You may control keyword arguments to bot.answerInlineQuery() by returning a dict
        # return {'results': articles, 'cache_time': 60}

    answerer.answer(msg, compute_answer)


def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print 'Chosen Inline Result:', result_id, from_id, query_string


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)

bot.notifyOnMessage({'normal': on_chat_message,
                     'inline_query': on_inline_query,
                     'chosen_inline_result': on_chosen_inline_result})
print 'Listening ...'

# Keep the program running.
while 1:
    time.sleep(10)
