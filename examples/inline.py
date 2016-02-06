import sys
import telepot
from telepot.delegate import per_inline_from_id, create_open

"""
$ python3.2 inline.py <token>

A bot that only cares about inline stuff.
"""

class InlineHandler(telepot.helper.UserHandler):
    def __init__(self, seed_tuple, timeout):
        super(InlineHandler, self).__init__(seed_tuple, timeout, flavors=['inline_query', 'chosen_inline_result'])

    def on_message(self, msg):
        flavor = telepot.flavor(msg)

        if flavor == 'inline_query':
            query_id, from_id, query_string = telepot.glance(msg, flavor=flavor)
            print(self.id, ':', 'Inline Query:', query_id, from_id, query_string)

            articles = [{'type': 'article',
                             'id': 'abc', 'title': 'ABC', 'message_text': 'Good morning'}]

            self.bot.answerInlineQuery(query_id, articles)
            print(self.id, ':', 'Answers sent.')

        elif flavor == 'chosen_inline_result':
            result_id, from_id, query_string = telepot.glance(msg, flavor=flavor)
            print(self.id, ':', 'Chosen Inline Result:', result_id, from_id, query_string)


TOKEN = sys.argv[1]

bot = telepot.DelegatorBot(TOKEN, [
    (per_inline_from_id(), create_open(InlineHandler, timeout=10)),
])
bot.notifyOnMessage(run_forever=True)
