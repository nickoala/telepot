import sys
import asyncio
import telepot
import telepot.async

"""
$ python3.4 skeletona.py <token>

A skeleton for your async telepot programs.
"""

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Normal Message:', content_type, chat_type, chat_id)

# need `/setinline`
@asyncio.coroutine
def on_inline_query(msg):
    query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
    print('Inline Query:', query_id, from_id, query_string)

    # Compose your own answers
    articles = [{'type': 'article',
                    'id': 'abc', 'title': 'ABC', 'message_text': 'Good morning'}]

    yield from bot.answerInlineQuery(query_id, articles)

# need `/setinlinefeedback`
def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print('Chosen Inline Result:', result_id, from_id, query_string)


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.async.Bot(TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop({'normal': on_chat_message,
                                  'inline_query': on_inline_query,
                                  'chosen_inline_result': on_chosen_inline_result}))
print('Listening ...')

loop.run_forever()
