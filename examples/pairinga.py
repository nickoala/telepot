import asyncio
import sys
import random
import telepot
import telepot.async
from telepot.delegate import per_chat_id, per_from_id, per_inline_from_id
from telepot.async.delegate import create_open

"""
$ python3.4 pairinga.py <token>

Demonstrates pairing patterns between per_ZZZ() and handler classes.
"""

# Captures only normal chat messages, to be paired with per_chat_id()
class ChatHandlerSubclass(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(ChatHandlerSubclass, self).__init__(seed_tuple, timeout)
        self._count = 0

    def on_message(self, msg):
        self._count += 1
        print('%s %d: %d: %s' % (type(self).__name__, self.id, self._count, telepot.glance(msg, flavor='normal')))

    def on_close(self, exception):
        print('%s %d: closed' % (type(self).__name__, self.id))

# Captures all flavors of messages from a user, to be paired with per_from_id()
class UserHandlerSubclass(telepot.helper.UserHandler):
    def __init__(self, seed_tuple, timeout):
        super(UserHandlerSubclass, self).__init__(seed_tuple, timeout)
        self._count = 0

    def on_message(self, msg):
        self._count += 1
        flavor = telepot.flavor(msg)

        print('%s %d: %d: %s: %s' % (type(self).__name__, self.id, self._count, flavor, telepot.glance(msg, flavor=flavor)))

    def on_close(self, exception):
        print('%s %d: closed' % (type(self).__name__, self.id))

# Captures inline-related messages from a user, to be paired with per_inline_from_id()
class UserHandlerSubclassInlineOnly(telepot.helper.UserHandler):
    def __init__(self, seed_tuple, timeout):
        super(UserHandlerSubclassInlineOnly, self).__init__(seed_tuple, timeout, flavors=['inline_query', 'chosen_inline_result'])
        self._count = 0

    def on_message(self, msg):
        self._count += 1
        flavor = telepot.flavor(msg)

        print('%s %d: %d: %s: %s' % (type(self).__name__, self.id, self._count, flavor, telepot.glance(msg, flavor=flavor)))

    def on_close(self, exception):
        print('%s %d: closed' % (type(self).__name__, self.id))


TOKEN = sys.argv[1]

bot = telepot.async.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(ChatHandlerSubclass, timeout=10)),

    (per_from_id(), create_open(UserHandlerSubclass, timeout=20)),

    (per_inline_from_id(), create_open(UserHandlerSubclassInlineOnly, timeout=10)),
])

loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop())
print('Listening ...')

loop.run_forever()
