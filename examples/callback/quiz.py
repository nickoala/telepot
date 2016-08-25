import sys
import random
import telepot
import telepot.helper
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space)

"""
$ python3.5 quiz.py <token>

Send a chat message to the bot. It will give you a math quiz. Stay silent for
10 seconds to end the quiz.

It handles callback query by their origins. All callback query originated from
the same chat message will be handled by the same `CallbackQueryOriginHandler`.
"""

class QuizStarter(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(QuizStarter, self).__init__(*args, **kwargs)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        self.sender.sendMessage(
            'Press START to do some math ...',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(text='START', callback_data='start'),
                ]]
            )
        )
        self.close()  # let Quizzer take over

class Quizzer(telepot.helper.CallbackQueryOriginHandler):
    def __init__(self, *args, **kwargs):
        super(Quizzer, self).__init__(*args, **kwargs)
        self._score = {True: 0, False: 0}
        self._answer = None

    def _show_next_question(self):
        x = random.randint(1,50)
        y = random.randint(1,50)
        sign, op = random.choice([('+', lambda a,b: a+b),
                                  ('-', lambda a,b: a-b),
                                  ('x', lambda a,b: a*b)])
        answer = op(x,y)
        question = '%d %s %d = ?' % (x, sign, y)
        choices = sorted(list(map(random.randint, [-49]*4, [2500]*4)) + [answer])

        self.editor.editMessageText(question,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    list(map(lambda c: InlineKeyboardButton(text=str(c), callback_data=str(c)), choices))
                ]
            )
        )
        return answer

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

        if query_data != 'start':
            self._score[self._answer == int(query_data)] += 1

        self._answer = self._show_next_question()

    def on__idle(self, event):
        text = '%d out of %d' % (self._score[True], self._score[True]+self._score[False])
        self.editor.editMessageText(text, reply_markup=None)
        self.close()


TOKEN = sys.argv[1]

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, QuizStarter, timeout=3),
    pave_event_space()(
        per_callback_query_origin(), create_open, Quizzer, timeout=10),
])

bot.message_loop(run_forever='Listening ...')
