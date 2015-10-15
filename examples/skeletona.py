import sys
import asyncio
import telepot
import telepot.async

"""
$ python3.4 skeletona.py <token>

A skeleton for your **async** telepot programs.
"""

@asyncio.coroutine
def handle(msg):
    content_type, chat_type, chat_id = telepot.glance2(msg)
    print(content_type, chat_type, chat_id)
    # Do your stuff according to `content_type` ...


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.async.Bot(TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop(handle))
print('Listening ...')

loop.run_forever()
