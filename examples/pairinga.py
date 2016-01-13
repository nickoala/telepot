import asyncio
import sys
import random
import telepot
import telepot.async
from telepot.delegate import per_chat_id, per_from_id, per_inline_from_id
from telepot.async.delegate import create_open

class MessageOnlyHandler(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(MessageOnlyHandler, self).__init__(seed_tuple, timeout)
        self._count = 0

    def on_message(self, msg):
        self._count += 1
        print('%s %d: %d: %s' % (type(self).__name__, self.id, self._count, telepot.glance2(msg, flavor='message')))

    def on_close(self, exception):
        print('%s %d: closed' % (type(self).__name__, self.id))

class MessageAndInlineHandler(telepot.helper.UserHandler):
    def __init__(self, seed_tuple, timeout):
        super(MessageAndInlineHandler, self).__init__(seed_tuple, timeout, flavors=['message', 'inline_query'])
        self._count = 0

    def on_message(self, msg):
        self._count += 1
        flavor = telepot.flavor(msg)

        print('%s %d: %d: %s: %s' % (type(self).__name__, self.id, self._count, flavor, telepot.glance2(msg, flavor=flavor)))

    def on_close(self, exception):
        print('%s %d: closed' % (type(self).__name__, self.id))

class InlineOnlyHandler(telepot.helper.UserHandler):
    def __init__(self, seed_tuple, timeout):
        super(InlineOnlyHandler, self).__init__(seed_tuple, timeout, flavors=['inline_query'])
        self._count = 0

    def on_message(self, msg):
        self._count += 1
        print('%s %d: %d: %s' % (type(self).__name__, self.id, self._count, telepot.glance2(msg, flavor='inline_query')))

    def on_close(self, exception):
        print('%s %d: closed' % (type(self).__name__, self.id))


TOKEN = sys.argv[1]

bot = telepot.async.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(MessageOnlyHandler, timeout=10)),

    (per_from_id(), create_open(MessageAndInlineHandler, timeout=20)),

    (per_inline_from_id(), create_open(InlineOnlyHandler, timeout=10)),
])

loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop())
print('Listening ...')

loop.run_forever()
