import sys
import asyncio
import telepot
from telepot.delegate import per_inline_from_id
from telepot.async.delegate import create_open

"""
$ python3.4 answerera_handler.py <token>

Use Answerer within a UserHandler.

In response to an inline query, it echoes the query string in the returned article.
You can easily check that the latest answer is the one displayed.
"""

class InlineHandler(telepot.helper.UserHandler):
    def __init__(self, seed_tuple, timeout):
        super(InlineHandler, self).__init__(seed_tuple, timeout, flavors=['inline_query', 'chosen_inline_result'])

        # Create the Answerer, give it the compute function.
        self._answerer = telepot.async.helper.Answerer(self.bot, self.compute_answer)

    @asyncio.coroutine
    def compute_answer(self, inline_query):
        query_id, from_id, query_string = telepot.glance(inline_query, flavor='inline_query')
        print('Computing for: %s' % query_string)

        # Test compute function being a coroutine
        yield from asyncio.sleep(1)

        articles = [{'type': 'article',
                         'id': 'abc', 'title': query_string, 'message_text': query_string}]
        return articles

        # You may control positional arguments to bot.answerInlineQuery() by returning a tuple
        # return (articles, 60)

        # You may control keyword arguments to bot.answerInlineQuery() by returning a dict
        # return {'results': articles, 'cache_time': 60}


    @asyncio.coroutine
    def on_message(self, msg):
        flavor = telepot.flavor(msg)

        if flavor == 'inline_query':
            # Just dump inline query to answerer
            self._answerer.answer(msg)

        elif flavor == 'chosen_inline_result':
            result_id, from_id, query_string = telepot.glance(msg, flavor=flavor)
            print(self.id, ':', 'Chosen Inline Result:', result_id, from_id, query_string)


TOKEN = sys.argv[1]

bot = telepot.async.DelegatorBot(TOKEN, [
    (per_inline_from_id(), create_open(InlineHandler, timeout=60)),
])
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop())
print('Listening ...')

loop.run_forever()
