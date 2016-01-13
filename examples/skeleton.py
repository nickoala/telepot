import sys
import time
import telepot

"""
$ python2.7 skeleton.py <token>

A skeleton for your telepot programs.
"""

def handle(msg):
    flavor = telepot.flavor(msg)

    # a normal message
    if flavor == 'message':
        content_type, chat_type, chat_id = telepot.glance2(msg)
        print content_type, chat_type, chat_id

        # Do your stuff according to `content_type` ...

    # an inline query - possible only AFTER `/setinline` has been done for the bot.
    elif flavor == 'inline_query':
        query_id, from_id, query_string = telepot.glance2(msg, flavor=flavor)
        print query_id, from_id, query_string

        # bot.answerInlineQuery(...)


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.Bot(TOKEN)
bot.notifyOnMessage(handle)
print 'Listening ...'

# Keep the program running.
while 1:
    time.sleep(10)
