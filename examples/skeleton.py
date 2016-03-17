import sys
import time
import telepot

"""
$ python2.7 skeleton.py <token>

A skeleton for your telepot programs.
"""

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print content_type, chat_type, chat_id
    

TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.Bot(TOKEN)
bot.notifyOnMessage(handle)
print 'Listening ...'

# Keep the program running.
while 1:
    time.sleep(10)
