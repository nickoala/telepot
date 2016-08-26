import sys
import time
from functools import reduce
import telepot
import telepot.helper
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, create_open, pave_event_space, include_callback_query_chat_id)

"""
$ python3.5 vote.py <token>

Add the bot to a group. Then send a command `/vote` to the group. The bot will
organize a ballot.

When all group members have cast a vote or when time expires (30 seconds),
it will announce the result. It demonstrates how to use the scheduler to
generate an expiry event after a certain delay.

It statically captures callback query according to the originating chat id.
This is the chat-centric approach.
"""

votes = telepot.helper.SafeDict()  # thread-safe dict

class VoteCounter(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(VoteCounter, self).__init__(*args, **kwargs)

        global votes
        if self.id in votes:
            self._ballot_box, self._keyboard_msg_ident, self._expired_event = votes[self.id]
            self._editor = telepot.helper.Editor(self.bot, self._keyboard_msg_ident) if self._keyboard_msg_ident else None
        else:
            self._ballot_box = None
            self._keyboard_msg_ident = None
            self._editor = None
            self._expired_event = None

        self._member_count = self.administrator.getChatMembersCount() - 1  # exclude myself, the bot

        # Catch _vote_expired event
        self.router.routing_table['_vote_expired'] = self.on__vote_expired

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type != 'text':
            print('Not a text message.')
            return

        if msg['text'] != '/vote':
            print('Not /vote')
            return

        if self._ballot_box is not None:
            self.sender.sendMessage('Voting still in progress')
        else:
            self._init_ballot()

    def _count_votes(self):
        yes = reduce(lambda a,b: a+(1 if b=='yes' else 0), self._ballot_box.values(), 0)
        no = reduce(lambda a,b: a+(1 if b=='no' else 0), self._ballot_box.values(), 0)
        return yes, no, self._member_count-yes-no

    def _init_ballot(self):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                       InlineKeyboardButton(text='Yes', callback_data='yes'),
                       InlineKeyboardButton(text='Nah!!!!', callback_data='no'),
                   ]])
        sent = self.sender.sendMessage("Let's Vote ...", reply_markup=keyboard)

        self._ballot_box = {}
        self._keyboard_msg_ident = telepot.message_identifier(sent)
        self._editor = telepot.helper.Editor(self.bot, self._keyboard_msg_ident)

        # Generate an expiry event 30 seconds later
        self._expired_event = self.scheduler.event_later(30, ('_vote_expired', {'seconds': 30}))

    def _close_ballot(self):
        try:
            self.scheduler.cancel(self._expired_event)
        # The expiry event may have already occurred and cannot be found in scheduler.
        except telepot.exception.EventNotFound:
            pass

        self._editor.editMessageReplyMarkup(reply_markup=None)

        self._ballot_box = None
        self._keyboard_msg_ident = None
        self._editor = None

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

        if from_id in self._ballot_box:
            self.bot.answerCallbackQuery(query_id, text='You have already voted %s' % self._ballot_box[from_id])
        else:
            self.bot.answerCallbackQuery(query_id, text='Ok')
            self._ballot_box[from_id] = query_data

        # Announce results if everyone has voted.
        if len(self._ballot_box) >= self._member_count:
            result = self._count_votes()
            self._close_ballot()
            self.sender.sendMessage('Everyone has voted:\nYes: %d\nNo: %d\nSilent: %d' % result)

    def on__vote_expired(self, event):
        result = self._count_votes()
        self._close_ballot()
        self.sender.sendMessage('Time is up:\nYes: %d\nNo: %d\nSilent: %d' % result)

    def on_close(self, ex):
        global votes
        if self._ballot_box is None:
            try:
                del votes[self.id]
            except KeyError:
                pass
        else:
            votes[self.id] = (self._ballot_box, self._keyboard_msg_ident, self._expired_event)

        from pprint import pprint
        pprint(votes)


TOKEN = sys.argv[1]

bot = telepot.DelegatorBot(TOKEN, [
    include_callback_query_chat_id(
        pave_event_space())(
            per_chat_id(types=['group']), create_open, VoteCounter, timeout=10),
])
bot.message_loop(run_forever='Listening ...')
