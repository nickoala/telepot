import sys
import asyncio
import telepot
import telepot.async

"""
$ python3.4 answerera_global.py <token>

Use Answerer globally.

In response to an inline query, it echoes the query string in the returned article.
You can easily check that the latest answer is the one displayed.
"""

@asyncio.coroutine
def handle(msg):
    flavor = telepot.flavor(msg)

    if flavor == 'inline_query':
        # Just dump inline query to answerer
        answerer.answer(msg)

    elif flavor == 'chosen_inline_result':
        result_id, from_id, query_string = telepot.glance(msg, flavor=flavor)
        print('Chosen Inline Result:', result_id, from_id, query_string)

def compute_answer(inline_query):
    query_id, from_id, query_string = telepot.glance(inline_query, flavor='inline_query')
    print('Computing for: %s' % query_string)

    articles = [{'type': 'article',
                     'id': 'abc', 'title': query_string, 'message_text': query_string}]
    return articles

    # You may control positional arguments to bot.answerInlineQuery() by returning a tuple
    # return (articles, 60)

    # You may control keyword arguments to bot.answerInlineQuery() by returning a dict
    # return {'results': articles, 'cache_time': 60}


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.async.Bot(TOKEN)
loop = asyncio.get_event_loop()

# Create the Answerer, give it the compute function.
answerer = telepot.async.helper.Answerer(bot, compute_answer)

loop.create_task(bot.messageLoop(handle))
print('Listening ...')

loop.run_forever()
