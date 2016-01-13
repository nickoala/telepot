import sys
import time
import telepot

"""
$ python3.2 skeleton_extend.py <token>

A skeleton for your telepot programs - extend from `Bot` and define a `handle` method.
"""

class YourBot(telepot.Bot):
    def handle(self, msg):
        flavor = telepot.flavor(msg)

        # a normal message
        if flavor == 'message':
            content_type, chat_type, chat_id = telepot.glance2(msg)
            print(content_type, chat_type, chat_id)

            # Do your stuff according to `content_type` ...

        # an inline query - possible only AFTER `/setinline` has been done for the bot.
        elif flavor == 'inline_query':
            query_id, from_id, query_srting = telepot.glance2(msg, flavor=flavor)
            print(query_id, from_id, query_srting)

            # bot.answerInlineQuery(...)


TOKEN = sys.argv[1] # get token from command-line

bot = YourBot(TOKEN)
bot.notifyOnMessage()
print('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
