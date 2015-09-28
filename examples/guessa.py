import sys
import asyncio
import random
import math
import telepot
import telepot.async

class GuessBot(telepot.async.SpeakerBot):
    def __init__(self, token):
        super(GuessBot, self).__init__(token)
        self._tasks = {}

    def _hint(self, answer, guess):
        if answer > guess:
            return 'larger'
        else:
            return 'smaller'

    @asyncio.coroutine
    def _player(self, chat_id, listener):
        answer = random.randint(0,100)

        try:
            yield from self.sendMessage(chat_id, 'Guess my number')

            while 1:
                msg = yield from asyncio.wait_for(listener.wait(chat__id=chat_id), self.DEFAULT_TIMEOUT)

                msg_type, from_id, chat_id = telepot.glance(msg)

                if msg_type != 'text':
                    yield from self.sendMessage(chat_id, 'Give me a number, please.')   # built-in retry???
                    continue

                try:
                   guess = int(msg['text'])
                except ValueError:
                    yield from self.sendMessage(chat_id, 'Give me a number, please.')   # built-in retry???
                    continue

                if guess != answer:
                    hint = self._hint(answer, guess)
                    yield from self.sendMessage(chat_id, hint)   # built-in retry???
                else:
                    yield from self.sendMessage(chat_id, 'Correct!')   # built-in retry???
                    return
        finally:
            del self._tasks[chat_id]

    def handle(self, msg):
        self.mic.send(msg)
        msg_type, from_id, chat_id = telepot.glance(msg)

        if chat_id not in self._tasks:
            ln = self.listener()
            p = self._player(chat_id, ln)
            self._tasks[chat_id] = p
            self._loop.create_task(p)


TOKEN = sys.argv[1]

bot = GuessBot(TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop())
print('Listening ...')

loop.run_forever()
