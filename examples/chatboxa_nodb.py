import os
import sys
import re
import traceback
import asyncio
import telepot
import telepot.async

""" Python3.4.3 or newer

$ python3.4 chatboxa_nodb.py <token> <owner_id>

Chatbox - a mailbox for chats

1. People send messages to your bot.
2. Your bot remembers the messages.
3. You read the messages later.

This version only stores the messages in memory. If the bot is killed, all messages are lost.
This version only handles text messages.

It accepts the following commands from you, the owner, only:

- /unread - tells you who has sent you messages and how many
- /next - read next sender's messages

It can be a starting point for customer-support type of bots.
"""

# Simulate a database to store unread messages
class UnreadStore(object):
    def __init__(self):
        self._db = {}

    def put(self, msg):
        chat_id = msg['chat']['id']
        
        if chat_id not in self._db:
            self._db[chat_id] = []

        self._db[chat_id].append(msg)

    # Pull all unread messages of a `chat_id`
    def pull(self, chat_id):
        messages = self._db[chat_id]
        del self._db[chat_id]
        
        # sort by date
        messages.sort(key=lambda m: m['date'])
        return messages

    # Tells how many unread messages per chat_id
    def unread_per_chat(self):
        return [(k,len(v)) for k,v in self._db.items()]


# See `ChatBox` constructor to see how this class is used.
# Being a subclass of `ChatHandler` is useful, for it gives you many facilities,
# e.g. listener, sender, etc
class OwnerHandler(telepot.helper.ChatHandler):
    WAIT_TIMEOUT = 20

    def __init__(self, seed_tuple, store):
        super(OwnerHandler, self).__init__(*seed_tuple)
        self.listener.timeout = 20  # timeout after 20 seconds of inactivity
        self._store = store

    @asyncio.coroutine
    def _read_messages(self, messages):
        for msg in messages:
            # assume all messages are text
            yield from self.sender.sendMessage(msg['text'])

    @asyncio.coroutine
    def _handle(self, msg):
        content_type, chat_type, chat_id = telepot.glance2(msg)
        
        if content_type != 'text':
            yield from self.sender.sendMessage("I don't understand")
            return

        command = msg['text'].strip().lower()

        # Tells who has sent you how many messages
        if command == '/unread':
            results = self._store.unread_per_chat()

            lines = []
            for r in results:
                n = 'ID: %d\n%d unread' % r
                lines.append(n)

            if not len(lines):
                yield from self.sender.sendMessage('No unread messages')
            else:
                yield from self.sender.sendMessage('\n'.join(lines))

        # read next sender's messages
        elif command == '/next':
            results = self._store.unread_per_chat()

            if not len(results):
                yield from self.sender.sendMessage('No unread messages')
                return

            chat_id = results[0][0]
            unread_messages = self._store.pull(chat_id)

            yield from self.sender.sendMessage('From ID: %d' % chat_id)
            yield from self._read_messages(unread_messages)

        else:
            yield from self.sender.sendMessage("I don't understand")

    @asyncio.coroutine
    def run(self):
        yield from self._handle(self.initial_message)

        try:
            while 1:
                # Use listener to wait for next message from owner
                msg = yield from asyncio.wait_for(self.listener.wait(chat__id=self.chat_id), self.WAIT_TIMEOUT)
                yield from self._handle(msg)
        except:
            traceback.print_exc()
            # display exceptions immediately


# See `ChatBox` constructor to see how this class is used.
class NewcomerHandler(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple):
        super(NewcomerHandler, self).__init__(*seed_tuple)

    # The action is very simple: just send a welcome message.
    @asyncio.coroutine
    def run(self):
        print('NewcomerHandler: sending welcome')
        yield from self.sender.sendMessage('Hello!')


from telepot.delegate import per_chat_id_in
from telepot.async.delegate import call, create_run

class ChatBox(telepot.async.DelegatorBot):
    def __init__(self, token, owner_id):
        self._owner_id = owner_id
        self._seen = set()
        self._store = UnreadStore()

        super(ChatBox, self).__init__(token, [
                                         # For each owner, create an OwnerHandler and obtain a coroutine object 
                                         #                                              from its `run()` method.
                                         (per_chat_id_in([owner_id]), create_run(OwnerHandler, self._store)),
                                         # Note how extra arguments are supplied to OwnerHandler's constructor.

                                         # For non-owners, just store the message. Since this is very simple,
                                         #               I choose to do it in a method - no objects required.
                                         (self._others, call(self._store_message, self._store)),
                                         # Note how extra arguments are supplied to the method.

                                         # For non-owners who have never been seen,
                                         #                create a NewcomerHandler and obtain a coroutine object
                                         #                                               from its `run()` method.
                                         (self._newcomer, create_run(NewcomerHandler)),

                                         # Note that the 2nd and 3rd condition are not exclusive. For a newcomer,
                                         # both are triggered - that is, a welcome message is sent AND the message
                                         # is stored.
                                     ])

    def _others(self, msg):
        chat_id = msg['chat']['id']
        return [] if chat_id != self._owner_id else None
        # [] non-hashable --> delegates are independent, no need to associate with a seed.

    def _newcomer(self, msg):
        chat_id = msg['chat']['id']
        if chat_id == self._owner_id:
            return None

        if chat_id in self._seen:
            return None

        self._seen.add(chat_id)
        return []
        # [] non-hashable --> delegates are independent, no need to associate with a seed.

    # Must be a coroutine because it is used as a delegate
    @asyncio.coroutine
    def _store_message(self, seed_tuple, store):
        msg = seed_tuple[1]
        print('Storing message: %s' % msg)
        store.put(msg)


TOKEN = sys.argv[1]
OWNER_ID = int(sys.argv[2])

bot = ChatBox(TOKEN, OWNER_ID)
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop())
print('Listening ...')

loop.run_forever()
