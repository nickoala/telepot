import sys
from datetime import datetime, timedelta
from functools import reduce
from pprint import pprint
import telepot
import telepot.helper
from telepot.delegate import per_from_id, create_open
from telepot.namedtuple import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

"""
$ python3.5 datecalc.py <token>

When pondering the date of an appointment or a gathering, we usually think
in terms of "this Saturday" or "next Monday", instead of the actual date.
Yet, for clarity, we eventually want to spell out the actual date to avoid
any chance of misunderstanding. This bot helps you convert weekdays into actual
dates.

1. Go to a private chat or a group chat, perform an inline query by typing
   `@YourBot monday` or any weekday you have in mind.
2. Choose a day from the returned results. In effect, you are proposing that day
   for appointment or gathering. Your friends will have a chance to accept or
   reject your proposal (via an inline keyboard). But the final decision is yours.
3. At the same time, you will receive a private message from the bot asking you
   to make a decision (using a custom keyboard) whether to fix the appointment
   or gathering on that date. You don't have to answer right away.
4. As your friends cast their votes on the proposed date, you will see real-time
   updates of the vote count.
5. When you feel comfortable, use the custom keyboard (sent by the bot in a
   private chat) to make a decision on the date.
"""

class DateCalculator(telepot.helper.UserHandler, telepot.helper.AnswererMixin):
    def __init__(self, seed_tuple, timeout):
        super(DateCalculator, self).__init__(seed_tuple, timeout)
        self._suggested_date = None
        self._suggestion_editor = None
        self._counter_editor = None
        self._votes = None

    def on_inline_query(self, msg):
        def compute():
            query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
            print('Inline query:', query_id, from_id, query_string)

            weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            query_string = query_string.lower()

            query_weekdays = [day[0] for day in enumerate(weekdays) if day[1].startswith(query_string)]

            def days_to(today, target):
                d = target - today
                if d <= 0:
                    d += 7
                return timedelta(days=d)

            today = datetime.today()
            deltas = [days_to(today.weekday(), target) for target in query_weekdays]

            def make_result(today, week_delta, day_delta):
                future = today + week_delta + day_delta

                n = 0 if future.weekday() > today.weekday() else 1
                n += int(week_delta.days / 7)

                return InlineQueryResultArticle(
                           id=future.strftime('%Y-%m-%d'),
                           title=('next '*n if n > 0 else 'this ') + weekdays[future.weekday()].capitalize(),
                           input_message_content=InputTextMessageContent(
                               message_text=future.strftime('%A, %Y-%m-%d')
                           ),
                           reply_markup=InlineKeyboardMarkup(
                               inline_keyboard=[[
                                   InlineKeyboardButton(text='Yes', callback_data='yes'),
                                   InlineKeyboardButton(text='No', callback_data='no'),
                               ]]
                           )
                       )

            results = []
            for i in range(0,3):
                weeks = timedelta(weeks=i)
                for d in deltas:
                    results.append(make_result(today, weeks, d))

            return results

        self.answerer.answer(msg, compute)

    def on_chosen_inline_result(self, msg):
        result_id, from_id, query = telepot.glance(msg, flavor='chosen_inline_result')
        print('Chosen inline result:', result_id, from_id, query)

        self._suggested_date = datetime.strptime(msg['result_id'], '%Y-%m-%d')
        self._suggestion_editor = telepot.helper.Editor(self.bot, msg)
        self._votes = {}

        self.sender.sendMessage('Decided on %s?' % msg['result_id'],
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[
                    KeyboardButton(text='Decided'),
                    KeyboardButton(text='Cancel'),
                ]],
                one_time_keyboard=True
            )
        )

        sent = self.sender.sendMessage('Yes: %d\nNo: %d' % self._count_votes())
        self._counter_editor = telepot.helper.Editor(self.bot, sent)

    def _count_votes(self):
        yes = reduce(lambda a,b: a+(1 if b=='yes' else 0), self._votes.values(), 0)
        no = reduce(lambda a,b: a+(1 if b=='no' else 0), self._votes.values(), 0)
        return yes, no

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print('Callback query:', query_id, from_id, query_data)

        if from_id in self._votes:
            self.bot.answerCallbackQuery(query_id, text='You have already voted %s' % self._votes[from_id])
        else:
            self.bot.answerCallbackQuery(query_id, text='Ok')
            self._votes[from_id] = query_data
            self._counter_editor.editMessageText('Yes: %d\nNo: %d' % self._count_votes())

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print('Chat:', content_type, chat_type, chat_id)

        # Ignore group messages
        if not self._suggested_date:
            return

        if content_type != 'text':
            return

        text = msg['text']
        date_string = self._suggested_date.strftime('%A, %Y-%m-%d')

        if text == 'Decided':
            THUMB_UP = u'\U0001f44d\U0001f3fb'
            self._suggestion_editor.editMessageText(date_string + '\n' + THUMB_UP + "Let's meet on this day.")
        else:
            CROSS = u'\u274c'
            self._suggestion_editor.editMessageText(date_string + '\n' + CROSS + "Let me find another day.")

    # Ignore group messages
    def on_edited_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg, flavor='edited_chat')
        print('Edited chat:', content_type, chat_type, chat_id)


TOKEN = sys.argv[1]

bot = telepot.DelegatorBot(TOKEN, [
    (per_from_id(), create_open(DateCalculator, timeout=20))
])
bot.message_loop(run_forever='Listening ...')
