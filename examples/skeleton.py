import sys
import time
import pprint
import telepot

"""
This can be a skeleton for a lot of telepot programs.
It basically waits for messages and prints out each one.

Run:
$ python skeleton.py <token>

Ctrl-C to kill.
"""

def handle(msg):
    pprint.pprint(msg)

bot = telepot.Bot(sys.argv[1])  # get token from command-line
bot.notifyOnMessage(handle)

while 1:
    time.sleep(10)
