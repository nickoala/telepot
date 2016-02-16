import sys
import asyncio
import telepot
import telepot.async

"""
$ python3.4 skeletona_extend.py <token>

A skeleton for your async telepot programs.
"""

class YourBot(telepot.async.Bot):
    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print('Normal Message:', content_type, chat_type, chat_id)

    # need `/setinline`
    @asyncio.coroutine
    def on_inline_query(self, msg):
        query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
        print('Inline Query:', query_id, from_id, query_string)

        # Compose your own answers
        articles = [{'type': 'article',
                        'id': 'abc', 'title': 'ABC', 'message_text': 'Good morning'}]

        yield from bot.answerInlineQuery(query_id, articles)

    # need `/setinlinefeedback`
    def on_chosen_inline_result(self, msg):
        result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
        print('Chosen Inline Result:', result_id, from_id, query_string)


TOKEN = sys.argv[1]  # get token from command-line

bot = YourBot(TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop())
print('Listening ...')

loop.run_forever()
