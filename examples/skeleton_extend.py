import sys
import time
import telepot

"""
$ python3.2 skeleton_extend.py <token>

A skeleton for your telepot programs - extend from `Bot` and define a `handle` method.
"""

class YourBot(telepot.Bot):
    def handle(self, msg):
        content_type, chat_type, chat_id = telepot.glance2(msg)
        print(content_type, chat_type, chat_id)
        # Do your stuff according to `content_type` ...


TOKEN = sys.argv[1] # get token from command-line

bot = YourBot(TOKEN)
bot.notifyOnMessage()
print('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
