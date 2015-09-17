import sys
import asyncio
import telepot
import telepot.async

"""
$ python3.4 skeletona.py <token>

A skeleton for your **async** telepot programs.
"""

# Add this decorator if you have `yield from` inside the function.
# @asyncio.coroutine
def handle(msg):
    msg_type, from_id, chat_id = telepot.glance(msg)
    print(msg_type, from_id, chat_id)
    # Do your stuff according to `msg_type` ...


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.async.Bot(TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop(handle))
print('Listening ...')

loop.run_forever()
