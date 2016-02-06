import sys
import telepot
from telepot.delegate import per_from_id, create_open

"""
$ python3.2 tracker.py <token>

Tracks user actions across all flavors.
"""

class UserTracker(telepot.helper.UserHandler):
    def __init__(self, seed_tuple, timeout):
        super(UserTracker, self).__init__(seed_tuple, timeout)

        # keep track of how many messages of each flavor
        self._counts = {'normal': 0,
                        'inline_query': 0,
                        'chosen_inline_result': 0}

    def on_message(self, msg):
        flavor = telepot.flavor(msg)
        self._counts[flavor] += 1

        print(self.id, ':', self._counts)

        # Have to answer inline query to receive chosen result
        if flavor == 'inline_query':
            query_id, from_id, query_string = telepot.glance(msg, flavor=flavor)

            articles = [{'type': 'article',
                             'id': 'abc', 'title': 'ABC', 'message_text': 'Good morning'}]

            self.bot.answerInlineQuery(query_id, articles)


TOKEN = sys.argv[1]

bot = telepot.DelegatorBot(TOKEN, [
    (per_from_id(), create_open(UserTracker, timeout=20)),
])
bot.notifyOnMessage(run_forever=True)
