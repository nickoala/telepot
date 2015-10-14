import sys
import random
import telepot
import telepot.helper

"""
$ python2.7 guess.py <token>

Guess a number:

1. The bot randomly picks an integer between 0-100. 
2. You make a guess. 
3. The bot tells you to go higher or lower.
4. Repeat step 2 and 3, until guess is correct.
"""

# Being a subclass of ChatHandler is useful, for it gives you many facilities,
# e.g. listener, sender, etc.
class Player(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple):
        super(Player, self).__init__(*seed_tuple)
        self.listener.timeout = 10
        # Raise exception after 10 seconds of no reply, ending the thread.

    def _hint(self, answer, guess):
        if answer > guess:
            return 'larger'
        else:
            return 'smaller'

    def run(self):
        # pick a number
        answer = random.randint(0,100)

        self.sender.sendMessage('Guess my number')

        while 1:
            # wait for user's guess
            msg = self.listener.wait(chat__id=self.chat_id)

            content_type, chat_type, chat_id = telepot.glance2(msg)

            if content_type != 'text':
                self.sender.sendMessage('Give me a number, please.')
                continue

            try:
               guess = int(msg['text'])
            except ValueError:
                self.sender.sendMessage('Give me a number, please.')
                continue

            # check the guess against the answer ...
            if guess != answer:
                # give a descriptive hint
                hint = self._hint(answer, guess)
                self.sender.sendMessage(hint)
            else:
                self.sender.sendMessage('Correct!')
                return


TOKEN = sys.argv[1]

from telepot.delegate import per_chat_id, create_run

bot = telepot.DelegatorBot(TOKEN, [
                          # For each chat_id, create a Player and delegate to its `run` method.
                               (per_chat_id(), create_run(Player)),
                          ])
bot.notifyOnMessage(run_forever=True)
