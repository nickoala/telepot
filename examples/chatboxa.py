import os
import sys
import re
import configparser
import pymongo
import asyncio
import telepot
import telepot.async

class OwnerHandler(telepot.helper.ChatHandler):
    WAIT_TIMEOUT = 20

    def __init__(self, seed_tuple, database):
        super(OwnerHandler, self).__init__(*seed_tuple)
        self._database = database

    def _aggregate_unread_per_chat(self):
        pipeline = [{'$match': {'_read': {'$exists': False}}}, {'$group': {'_id': '$chat.id', "count": {"$sum": 1}}}]
        return self._database.messages.aggregate(pipeline)

    @asyncio.coroutine
    def _display_messages(self, messages):
        for msg in messages:
            # assume all messages are text
            yield from self.sender.sendMessage(msg['text'])

            # update message as read
            self._database.messages.update_one({'_id': msg['_id']}, {'$set': {'_read': True}})

    def _looks_like_chat_id(self, command):
        return re.match('/[0-9]+', command)

    def _extract_chat_id(self, command):
        m = re.match('/([0-9]+)', command)
        return int(m.group(1))

    @asyncio.coroutine
    def _handle(self, msg):
        msg_type, from_id, chat_id = telepot.glance(msg)

        if msg_type != 'text':
            yield from self.sender.sendMessage("I don't understand")
            return

        command = msg['text'].strip().lower()

        if command == '/unread':
            results = self._aggregate_unread_per_chat()

            lines = []
            for r in results:
                n = '/%d\n      %d unread' % (r['_id'], r['count'])
                lines.append(n)

            if not len(lines):
                yield from self.sender.sendMessage('No unread messages')
            else:
                yield from self.sender.sendMessage('\n'.join(lines))

        elif command == '/next':
            results = self._aggregate_unread_per_chat()

            try:
                r = results.next()
                unread = self._database.messages.find({'chat.id': r['_id'], '_read': {'$exists': False}}).sort('date', 1)

                yield from self.sender.sendMessage('From ID: %d' % r['_id'])
                yield from self._display_messages(unread)

            except StopIteration:
                yield from self.sender.sendMessage('No unread messages')

        elif self._looks_like_chat_id(command):
            try:
                chat_id = self._extract_chat_id(command)
                unread = self._database.messages.find({'chat.id': chat_id, '_read': {'$exists': False}}).sort('date', 1)

                if unread.count() == 0:
                    yield from self.sender.sendMessage('No unread messages for this chat')
                    return

                yield from self._display_messages(unread)

            except ValueError:
                yield from self.sender.sendMessage('Chat ID must be a number')
        else:
            yield from self.sender.sendMessage("I don't understand")

    @asyncio.coroutine
    def run(self):
        yield from self._handle(self.initial_message)

        while 1:
            msg = yield from asyncio.wait_for(self.listener.wait(chat__id=self.chat_id), self.WAIT_TIMEOUT)
            yield from self._handle(msg)

class NewcomerHandler(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple):
        super(NewcomerHandler, self).__init__(*seed_tuple)

    @asyncio.coroutine
    def run(self):
        print('NewcomerHandler: sending welcome')
        yield from self.sender.sendMessage('Hello!')

from telepot.delegate import per_chat_id_in
from telepot.async.delegate import call, create_run

class ChatBox(telepot.async.DelegatorBot):
    def __init__(self, token, owner_id, db_info):
        host, port, dbname, dbuser, dbpwd = db_info
        self._dbclient = pymongo.MongoClient(host, port)
        self._database = self._dbclient[dbname]
        self._database.authenticate(dbuser, dbpwd)

        super(ChatBox, self).__init__(token, [
                                         (per_chat_id_in([owner_id]), create_run(OwnerHandler, self._database)),
                                         (self._others, call(self._handle_others, self._database)),
                                         (self._newcomer, create_run(NewcomerHandler)),
                                     ])
        self._owner_id = owner_id
        self._seen = set()


    def _owner(self, msg):
        chat_id = msg['chat']['id']
        return chat_id if chat_id == self._owner_id else None

    def _others(self, msg):
        chat_id = msg['chat']['id']
        return [] if chat_id != self._owner_id else None

    def _newcomer(self, msg):
        chat_id = msg['chat']['id']
        if chat_id == self._owner_id:
            return None

        if chat_id in self._seen:
            return None

        self._seen.add(chat_id)

        # In database, are there any messages from this chat_id, but not the current message?
        if self._database.messages.find_one({'chat.id':chat_id, 'message_id': {'$ne': msg['message_id']}}):
            # Seen him before, not a newcomer.
            return None
        else:
            # Never seen him. He is a newcomer.
            return []

    @asyncio.coroutine
    def _handle_others(self, seed_tuple, db):
        msg = seed_tuple[1]
        print('_handle_others(): inserting %s' % msg)
        db.messages.insert_one(msg)


config = configparser.ConfigParser()
config.read(sys.argv[1])

filename = os.path.basename(sys.argv[0])

TOKEN = config[filename]['bot_token']
OWNER_ID = int(config[filename]['owner_id'])

bot = ChatBox(TOKEN, OWNER_ID, [type(config[filename][name]) for type,name in [
          (str, 'db_host'), (int, 'db_port'), (str, 'db_name'), (str, 'db_username'), (str, 'db_password')]])

loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop())
print('Listening ...')

loop.run_forever()
