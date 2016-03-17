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
    print('Chat Message:', content_type, chat_type, chat_id)


def on_inline_query(msg):
    def compute_answer():
        query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
        print('Computing for: %s' % query_string)

        articles = [{'type': 'article',
                         'id': 'abc', 'title': query_string, 'message_text': query_string}]
        return articles

        # You may control positional arguments to bot.answerInlineQuery() by returning a tuple
        # return (articles, 60)

        # You may control keyword arguments to bot.answerInlineQuery() by returning a dict
        # return {'results': articles, 'cache_time': 60}

    answerer.answer(msg, compute_answer)


def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print('Chosen Inline Result:', result_id, from_id, query_string)


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.async.Bot(TOKEN)
answerer = telepot.async.helper.Answerer(bot)

loop = asyncio.get_event_loop()
loop.create_task(bot.messageLoop({'normal': on_chat_message,
                                  'inline_query': on_inline_query,
                                  'chosen_inline_result': on_chosen_inline_result}))
print('Listening ...')

loop.run_forever()
