import os
import sys
import re
import telepot

"""
$ python3.2 chatbox_nodb.py <token> <owner_id>

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
    def __init__(self, seed_tuple, store):
        super(OwnerHandler, self).__init__(*seed_tuple)
        self.listener.timeout = 20  # timeout after 20 seconds of inactivity
        self._store = store

    def _read_messages(self, messages):
        for msg in messages:
            # assume all messages are text
            self.sender.sendMessage(msg['text'])

    def _handle(self, msg):
        msg_type, from_id, chat_id = telepot.glance(msg)
        
        if msg_type != 'text':
            self.sender.sendMessage("I don't understand")
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
                self.sender.sendMessage('No unread messages')
            else:
                self.sender.sendMessage('\n'.join(lines))

        # read next sender's messages
        elif command == '/next':
            results = self._store.unread_per_chat()

            if not len(results):
                self.sender.sendMessage('No unread messages')
                return

            chat_id = results[0][0]
            unread_messages = self._store.pull(chat_id)

            self.sender.sendMessage('From ID: %d' % chat_id)
            self._read_messages(unread_messages)

        else:
            self.sender.sendMessage("I don't understand")

    def run(self):
        self._handle(self.initial_message)

        while 1:
            # Use listener to wait for next message from owner
            msg = self.listener.wait(chat__id=self.chat_id)
            self._handle(msg)


# See `ChatBox` constructor to see how this class is used.
class NewcomerHandler(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple):
        super(NewcomerHandler, self).__init__(*seed_tuple)

    # The action is very simple: just send a welcome message.
    def run(self):
        print('NewcomerHandler: sending welcome')
        self.sender.sendMessage('Hello!')


import threading

# See `ChatBox` constructor to see how this class, combined with `custom_thread`
# function below, is used to wrap around a `NewcomerHandler` object to provide 
# a custom delegate implementation.
class CustomThread(threading.Thread):
    def start(self):
        print('CustomThread starting ...')
        super(CustomThread, self).start()

def custom_thread(func):
    def f(seed_tuple):
        target = func(seed_tuple)

        if type(target) is tuple:
            run, args, kwargs = target
            t = CustomThread(target=run, args=args, kwargs=kwargs)
        else:
            t = CustomThread(target=target)

        return t
    return f


from telepot.delegate import per_chat_id_in, call, create_run

class ChatBox(telepot.DelegatorBot):
    def __init__(self, token, owner_id):
        self._owner_id = owner_id
        self._seen = set()
        self._store = UnreadStore()

        super(ChatBox, self).__init__(token, [
                                         # For each owner, create an OwnerHandler and spawn a thread 
                                         #                                           around its `run()` method.
                                         (per_chat_id_in([owner_id]), create_run(OwnerHandler, self._store)),
                                         # Note how extra arguments are supplied to OwnerHandler's constructor.

                                         # For non-owners, just store the message. Since this is very simple,
                                         #               I choose to do it in a method - no objects required.
                                         (self._others, call(self._store_message, self._store)),
                                         # Note how extra arguments are supplied to the method.

                                         # For non-owners who have never been seen,
                                         #                create a NewcomerHandler and spawn a *custom* thread 
                                         #                                           around its `run()` method.
                                         (self._newcomer, custom_thread(create_run(NewcomerHandler))),

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

    def _store_message(self, seed_tuple, store):
        msg = seed_tuple[1]
        print('Storing message: %s' % msg)
        store.put(msg)


TOKEN = sys.argv[1]
OWNER_ID = int(sys.argv[2])

bot = ChatBox(TOKEN, OWNER_ID)
bot.notifyOnMessage(run_forever=True)
