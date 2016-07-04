import sys
import time
import telepot
import telepot.helper
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import per_chat_id, create_open
from functools import reduce

"""
$ python3.5 referendum.py <token>

Add the bot to a group. Then send a command `/vote` to the group. The bot will
organize a referendum.

When all group members have cast a vote or when time expires, it will announce
the result.
"""

class VoteCounter(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(VoteCounter, self).__init__(seed_tuple, timeout)
        self._editor = None
        self._votes = None
        self._members_count = None

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type != 'text':
            print('Not a text message.')
            return

        if msg['text'] != '/vote':
            print('Not /vote')
            return

        # Have to set options before sending inline keyboard
        options = self.callback_query_coordinator.make_options(scheme='independent',
                                                               callback_timeout=10)
        self.callback_query_coordinator.set_options('group', **options)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                       InlineKeyboardButton(text='Yes', callback_data='yes'),
                       InlineKeyboardButton(text='Nah!!!!', callback_data='no'),
                   ]])
        sent = self.sender.sendMessage("Let's do a referendum.", reply_markup=keyboard)
        self._editor = telepot.helper.Editor(self.bot, sent)
        self._votes = {}
        self._members_count = self.administrator.getChatMembersCount() - 1  # exclude myself, the bot

    def _count_votes(self):
        yes = reduce(lambda a,b: a+(1 if b=='yes' else 0), self._votes.values(), 0)
        no = reduce(lambda a,b: a+(1 if b=='no' else 0), self._votes.values(), 0)
        return yes, no, self._members_count-yes-no

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

        if from_id in self._votes:
            self.bot.answerCallbackQuery(query_id, text='You have already voted %s' % self._votes[from_id])
        else:
            self.bot.answerCallbackQuery(query_id, text='Ok')
            self._votes[from_id] = query_data

        if len(self._votes) >= self._members_count:
            self._editor.editMessageReplyMarkup(reply_markup=None)
            self.sender.sendMessage('Everyone has voted. Thank you.')
            self.sender.sendMessage('Yes: %d\nNo: %d\nSilent: %d' % self._count_votes())

    def on_timeout(self, exception):
        self._editor.editMessageReplyMarkup(reply_markup=None)
        self.sender.sendMessage('Time is up.')
        self.sender.sendMessage('Yes: %d\nNo: %d\nSilent: %d' % self._count_votes())


TOKEN = sys.argv[1]

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(types=['group']), create_open(VoteCounter, timeout=20)),
])
bot.message_loop()
print('Listening ...')

while 1:
    time.sleep(10)
