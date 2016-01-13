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
    flavor = telepot.flavor(msg)

    # a normal message
    if flavor == 'normal':
        content_type, chat_type, chat_id = telepot.glance2(msg)
        print(content_type, chat_type, chat_id)

        # Do your stuff according to `content_type` ...

    # an inline query - possible only AFTER `/setinline` has been done for the bot.
    elif flavor == 'inline_query':
        query_id, from_id, query_string = telepot.glance2(msg, flavor=flavor)
        print(query_id, from_id, query_string)

        # bot.answerInlineQuery(...)


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.async.Bot(TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop(handle))
print('Listening ...')

loop.run_forever()
