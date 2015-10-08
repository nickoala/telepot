import sys
import asyncio
import random
import traceback
import telepot
import telepot.helper
import telepot.async

"""
$ python3.4 guessa.py <token>

Guess a number:

1. The bot randomly picks an integer between 0-100. 
2. You make a guess. 
3. The bot tells you to go higher or lower.
4. Repeat step 2 and 3, until guess is correct.
"""

# Being a subclass of ChatHandler is useful, for it gives you many facilities,
# e.g. listener, sender, etc.
class Player(telepot.helper.ChatHandler):
    WAIT_TIMEOUT = 10

    def __init__(self, seed_tuple):
        super(Player, self).__init__(*seed_tuple)

    def _hint(self, answer, guess):
        if answer > guess:
            return 'larger'
        else:
            return 'smaller'

    @asyncio.coroutine
    def run(self):
        try:
            # pick a number
            answer = random.randint(0,100)

            yield from self.sender.sendMessage('Guess my number')

            while 1:
                # wait for user's guess
                msg = yield from asyncio.wait_for(self.listener.wait(chat__id=self.chat_id), self.WAIT_TIMEOUT)

                msg_type, from_id, chat_id = telepot.glance(msg)

                if msg_type != 'text':
                    yield from self.sender.sendMessage('Give me a number, please.')
                    continue

                try:
                   guess = int(msg['text'])
                except ValueError:
                    yield from self.sender.sendMessage('Give me a number, please.')
                    continue

                # check the guess against the answer ...
                if guess != answer:
                    # give a descriptive hint
                    hint = self._hint(answer, guess)
                    yield from self.sender.sendMessage(hint)
                else:
                    yield from self.sender.sendMessage('Correct!')
                    return
        except:
            traceback.print_exc()
            # display exceptions immediately


TOKEN = sys.argv[1]

from telepot.delegate import per_chat_id
from telepot.async.delegate import create_run

bot = telepot.async.DelegatorBot(TOKEN, [
                               # For each chat_id, create a Player and delegate to its `run()` method.
                                    (per_chat_id(), create_run(Player)),
                                ])
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop())
print('Listening ...')

loop.run_forever()
