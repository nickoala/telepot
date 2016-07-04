import sys
import time
import telepot
import telepot.helper
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import per_chat_id, create_open

"""
$ python3.5 lover.py <token>

1. Send him a message
2. He will ask you to marry him
3. He will keep asking until you say "Yes"

Proposing is a private matter. This bot only works in a private chat.
"""

class Lover(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(Lover, self).__init__(seed_tuple, timeout)
        self._count = 0
        self._editor = None
        self._keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                             InlineKeyboardButton(text='Yes', callback_data='yes'),
                             InlineKeyboardButton(text='um ...', callback_data='no'),
                         ]])

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        self._count += 1
        sent = self.sender.sendMessage('%d. Would you marry me?' % self._count, reply_markup=self._keyboard)
        self._editor = telepot.helper.Editor(self.bot, sent)

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

        if query_data == 'yes':
            # hide inline keyboard
            self._editor.editMessageReplyMarkup(reply_markup=None)
            self.sender.sendMessage('Thank you!')
            self.close()
        else:
            self.bot.answerCallbackQuery(query_id, text='Ok. But I am going to keep asking.')

            # hide inline keyboard
            self._editor.editMessageReplyMarkup(reply_markup=None)

            self._count += 1
            sent = self.sender.sendMessage('%d. Would you marry me?' % self._count, reply_markup=self._keyboard)
            self._editor = telepot.helper.Editor(self.bot, sent)


TOKEN = sys.argv[1]

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(types=['private']), create_open(Lover, timeout=10)),
])
bot.message_loop()
print('Listening ...')

while 1:
    time.sleep(10)
