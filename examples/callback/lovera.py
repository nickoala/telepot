import sys
import asyncio
from telepot import message_identifier, glance
import telepot.aio
import telepot.aio.helper
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.aio.delegate import (
    per_chat_id, create_open, pave_event_space, include_callback_query_chat_id)

"""
$ python3.5 lovera.py <token>

1. Send him a message
2. He will ask you to marry him
3. He will keep asking until you say "Yes"

If you are silent for 10 seconds, he will go away a little bit, but is still
there waiting for you. What a sweet bot!

It statically captures callback query according to the originating chat id.
This is the chat-centric approach.

Proposing is a private matter. This bot only works in a private chat.
"""

propose_records = dict()

class Lover(telepot.aio.helper.ChatHandler):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                   InlineKeyboardButton(text='Yes', callback_data='yes'),
                   InlineKeyboardButton(text='um ...', callback_data='no'),
               ]])

    def __init__(self, *args, **kwargs):
        super(Lover, self).__init__(*args, **kwargs)

        # Retrieve from database
        global propose_records
        if self.id in propose_records:
            self._count, self._edit_msg_ident = propose_records[self.id]
            self._editor = telepot.aio.helper.Editor(self.bot, self._edit_msg_ident) if self._edit_msg_ident else None
        else:
            self._count = 0
            self._edit_msg_ident = None
            self._editor = None

    async def _propose(self):
        self._count += 1
        sent = await self.sender.sendMessage('%d. Would you marry me?' % self._count, reply_markup=self.keyboard)
        self._editor = telepot.aio.helper.Editor(self.bot, sent)
        self._edit_msg_ident = message_identifier(sent)

    async def _cancel_last(self):
        if self._editor:
            await self._editor.editMessageReplyMarkup(reply_markup=None)
            self._editor = None
            self._edit_msg_ident = None

    async def on_chat_message(self, msg):
        await self._propose()

    async def on_callback_query(self, msg):
        query_id, from_id, query_data = glance(msg, flavor='callback_query')

        if query_data == 'yes':
            await self._cancel_last()
            await self.sender.sendMessage('Thank you!')
            self.close()
        else:
            await self.bot.answerCallbackQuery(query_id, text='Ok. But I am going to keep asking.')
            await self._cancel_last()
            await self._propose()

    async def on__idle(self, event):
        await self.sender.sendMessage('I know you may need a little time. I will always be here for you.')
        self.close()

    def on_close(self, ex):
        # Save to database
        global propose_records
        propose_records[self.id] = (self._count, self._edit_msg_ident)


TOKEN = sys.argv[1]

bot = telepot.aio.DelegatorBot(TOKEN, [
    include_callback_query_chat_id(
        pave_event_space())(
            per_chat_id(types=['private']), create_open, Lover, timeout=10),
])

loop = asyncio.get_event_loop()
loop.create_task(bot.message_loop())
print('Listening ...')

loop.run_forever()
