import sys
import threading
import random
import math
import telepot
import telepot.listener

class Player(threading.Thread):
    def __init__(self, chat_id, bot, listener):
        super(Player, self).__init__()
        self._chat_id = chat_id
        self._bot = bot
        self._listener = listener

    def _hint(self, answer, guess):
        if answer > guess:
            return 'larger'
        else:
            return 'smaller'

    def run(self):
        answer = random.randint(0,100)

        try:
            self._bot.sendMessage(self._chat_id, 'Guess my number')

            while 1:
                msg = self._listener.wait(chat__id=self._chat_id)

                msg_type, from_id, chat_id = telepot.glance(msg)

                if msg_type != 'text':
                    self._bot.sendMessage(self._chat_id, 'Give me a number, please.')   # built-in retry???
                    continue

                try:
                   guess = int(msg['text'])
                except ValueError:
                    self._bot.sendMessage(self._chat_id, 'Give me a number, please.')   # built-in retry???
                    continue

                if guess != answer:
                    hint = self._hint(answer, guess)
                    self._bot.sendMessage(self._chat_id, hint)   # built-in retry???
                else:
                    self._bot.sendMessage(self._chat_id, 'Correct!')   # built-in retry???
                    return
        finally:
            self._bot.remove_thread(self._chat_id)


class GuessBot(telepot.SpeakerBot):
    def __init__(self, token):
        super(GuessBot, self).__init__(token)

        self._threads = {}
        self._lock = threading.Lock()

    def remove_thread(self, chat_id):
        with self._lock:
            del self._threads[chat_id]

    def handle(self, msg):
        self.mic.send(msg)
        msg_type, from_id, chat_id = telepot.glance(msg)

        with self._lock:
            if chat_id not in self._threads:
                ln = self.listener()
                p = Player(chat_id, self, ln)
                self._threads[chat_id] = p
                p.start()


TOKEN = sys.argv[1]

bot = GuessBot(TOKEN)
bot.notifyOnMessage(run=True)
