import sys
import random
import telepot
from telepot.delegate import per_chat_id, per_from_id, per_inline_from_id, per_application, per_message, create_open, call

"""
$ python2.7 pairing.py <token>

Demonstrates pairing patterns between per_ZZZ() and handler classes.
"""

# Captures only chat messages, to be paired with per_chat_id()
class ChatHandlerSubclass(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(ChatHandlerSubclass, self).__init__(seed_tuple, timeout)
        self._count = 0

    def on_message(self, msg):
        self._count += 1
        print '%s %d: %d: %s' % (type(self).__name__, self.id, self._count, telepot.glance(msg, flavor='chat'))

    def on_close(self, exception):
        print '%s %d: closed' % (type(self).__name__, self.id)

# Captures all flavors of messages from a user, to be paired with per_from_id()
class UserHandlerSubclass(telepot.helper.UserHandler):
    def __init__(self, seed_tuple, timeout):
        super(UserHandlerSubclass, self).__init__(seed_tuple, timeout)
        self._count = 0

    def on_message(self, msg):
        self._count += 1
        flavor = telepot.flavor(msg)

        print '%s %d: %d: %s: %s' % (type(self).__name__, self.id, self._count, flavor, telepot.glance(msg, flavor=flavor))

    def on_close(self, exception):
        print '%s %d: closed' % (type(self).__name__, self.id)

# Captures inline-related messages from a user, to be paired with per_inline_from_id()
class UserHandlerSubclassInlineOnly(telepot.helper.UserHandler):
    def __init__(self, seed_tuple, timeout):
        super(UserHandlerSubclassInlineOnly, self).__init__(seed_tuple, timeout, flavors=['inline_query', 'chosen_inline_result'])
        self._count = 0

    def on_message(self, msg):
        self._count += 1
        flavor = telepot.flavor(msg)

        print '%s %d: %d: %s: %s' % (type(self).__name__, self.id, self._count, flavor, telepot.glance(msg, flavor=flavor))

    def on_close(self, exception):
        print '%s %d: closed' % (type(self).__name__, self.id)

# Captures all messages, to be paired with per_application()
class OnlyOneInstance(telepot.helper.Monitor):
    def __init__(self, seed_tuple):
        super(OnlyOneInstance, self).__init__(seed_tuple, capture=[{'_': lambda msg: True}])
        self._count = 0

    def on_message(self, msg):
        self._count += 1
        flavor = telepot.flavor(msg)

        print '%s %d: %d: %s: %s' % (type(self).__name__, self.id, self._count, flavor, telepot.glance(msg, flavor=flavor))

# Do some simple stuff for every message, to be paired with per_message()
def simple_function(seed_tuple):
    bot, msg, id = seed_tuple
    print 'Simply print:', msg


TOKEN = sys.argv[1]

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(ChatHandlerSubclass, timeout=10)),

    (per_from_id(), create_open(UserHandlerSubclass, timeout=20)),

    (per_inline_from_id(), create_open(UserHandlerSubclassInlineOnly, timeout=10)),

    (per_application(), create_open(OnlyOneInstance)),

    (per_message(), call(simple_function)),
])
bot.message_loop(run_forever=True)
