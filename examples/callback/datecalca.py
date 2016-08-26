import sys
import asyncio
from datetime import datetime, timedelta
from functools import reduce
from telepot import glance, peel
import telepot.aio
from telepot.aio.helper import (
    InlineUserHandler, AnswererMixin, InterceptCallbackQueryMixin, Editor)
from telepot.namedtuple import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton)
from telepot.aio.delegate import (
    per_inline_from_id, create_open, pave_event_space,
    intercept_callback_query_origin)

"""
$ python3.5 datecalca.py <token>

When pondering the date of an appointment or a gathering, we usually think
in terms of "this Saturday" or "next Monday", instead of the actual date.
This *inline* bot helps you convert weekdays into actual dates.

1. Go to a group chat. The bot does not need to be a group member. You are
   going to inline-query it.

2. Type `@YourBot monday` or any weekday you have in mind. It will suggest a
   few dates based on it.

3. Choose a day from the returned results. The idea is to propose a date to
   the group. Group members have 30 seconds to vote on the proposed date.

4. After 30 seconds, the voting result is announced.

This example dynamically maps callback query back to their originating
`InlineUserHandler`, so you can do question-asking (sending a message containing
an inline keyboard) and answer-gathering (receiving callback query) in the same
object.
"""

user_ballots = dict()

class DateCalculator(InlineUserHandler,
                     AnswererMixin,
                     InterceptCallbackQueryMixin):
    def __init__(self, *args, **kwargs):
        super(DateCalculator, self).__init__(*args, **kwargs)

        global user_ballots
        if self.id in user_ballots:
            self._ballots = user_ballots[self.id]
            print('Ballot retrieved.')
        else:
            self._ballots = {}
            print('Ballot initialized.')

        self.router.routing_table['_expired'] = self.on__expired

    def on_inline_query(self, msg):
        def compute():
            query_id, from_id, query_string = glance(msg, flavor='inline_query')
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
        if 'inline_message_id' in msg:
            inline_message_id = msg['inline_message_id']
            suggested_date = msg['result_id']
            self._ballots[inline_message_id] = {}
            self.scheduler.event_later(30, ('_expired', {'seconds': 30,
                                                         'inline_message_id': inline_message_id,
                                                         'date': suggested_date}))

    async def on_callback_query(self, msg):
        if 'inline_message_id' in msg:
            inline_message_id = msg['inline_message_id']
            ballot = self._ballots[inline_message_id]

            query_id, from_id, query_data = glance(msg, flavor='callback_query')
            if from_id in ballot:
                await self.bot.answerCallbackQuery(query_id, text='You have already voted %s' % ballot[from_id])
            else:
                await self.bot.answerCallbackQuery(query_id, text='Ok')
                ballot[from_id] = query_data

    def _count(self, ballot):
        yes = reduce(lambda a,b: a+(1 if b=='yes' else 0), ballot.values(), 0)
        no = reduce(lambda a,b: a+(1 if b=='no' else 0), ballot.values(), 0)
        return yes, no

    async def on__expired(self, event):
        evt = peel(event)
        inline_message_id = evt['inline_message_id']
        suggested_date = evt['date']

        ballot = self._ballots[inline_message_id]
        text = '%s\nYes: %d\nNo: %d' % ((suggested_date,) + self._count(ballot))

        editor = Editor(self.bot, inline_message_id)
        await editor.editMessageText(text=text, reply_markup=None)

        del self._ballots[inline_message_id]
        self.close()

    def on_close(self, ex):
        global user_ballots
        user_ballots[self.id] = self._ballots
        print('Closing, ballots saved.')


TOKEN = sys.argv[1]

bot = telepot.aio.DelegatorBot(TOKEN, [
    intercept_callback_query_origin(
        pave_event_space())(
            per_inline_from_id(), create_open, DateCalculator, timeout=10),
])

loop = asyncio.get_event_loop()
loop.create_task(bot.message_loop())
print('Listening ...')

loop.run_forever()
