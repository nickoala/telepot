import sys
import random
import telepot
import telepot.helper


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
        answer = random.randint(0,100)

        self.sender.sendMessage('Guess my number')

        while 1:
            msg = self.listener.wait(chat__id=self.chat_id)

            msg_type, from_id, chat_id = telepot.glance(msg)

            if msg_type != 'text':
                self.sender.sendMessage('Give me a number, please.')
                continue

            try:
               guess = int(msg['text'])
            except ValueError:
                self.sender.sendMessage('Give me a number, please.')
                continue

            if guess != answer:
                hint = self._hint(answer, guess)
                self.sender.sendMessage(hint)
            else:
                self.sender.sendMessage('Correct!')
                return


TOKEN = sys.argv[1]

from telepot.delegate import per_chat_id, create_run

bot = telepot.DelegatorBot(TOKEN, [
                               (per_chat_id(), create_run(Player)),
                          ])
bot.notifyOnMessage(run_forever=True)
