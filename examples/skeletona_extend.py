import sys
import asyncio
import telepot
import telepot.async

"""
$ python3.4 skeletona_extend.py <token>

A skeleton for your **async** telepot programs.
"""

class YourBot(telepot.async.Bot):
    @asyncio.coroutine
    def handle(self, msg):
        flavor = telepot.flavor(msg)

        # normal message
        if flavor == 'normal':
            content_type, chat_type, chat_id = telepot.glance(msg)
            print('Normal Message:', content_type, chat_type, chat_id)

            # Do your stuff according to `content_type` ...

        # inline query - need `/setinline`
        elif flavor == 'inline_query':
            query_id, from_id, query_string = telepot.glance(msg, flavor=flavor)
            print('Inline Query:', query_id, from_id, query_string)

            # Compose your own answers
            articles = [{'type': 'article',
                            'id': 'abc', 'title': 'ABC', 'message_text': 'Good morning'}]

            yield from bot.answerInlineQuery(query_id, articles)

        # chosen inline result - need `/setinlinefeedback`
        elif flavor == 'chosen_inline_result':
            result_id, from_id, query_string = telepot.glance(msg, flavor=flavor)
            print('Chosen Inline Result:', result_id, from_id, query_string)

            # Remember the chosen answer to do better next time

        else:
            raise telepot.BadFlavor(msg)


TOKEN = sys.argv[1]  # get token from command-line

bot = YourBot(TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop())
print('Listening ...')

loop.run_forever()
