import sys
import time
import telepot
import telepot.namedtuple
from telepot.routing import by_content_type, make_content_type_routing_table
from telepot.exception import NotEnoughRightsError

class AdminBot(telepot.Bot):
    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if 'edit_date' not in msg:
            self.sendMessage(chat_id, 'Edit the message, please.')
        else:
            self.sendMessage(chat_id, 'Add me to a group, please.')
            r = telepot.helper.Router(by_content_type(), make_content_type_routing_table(self))
            self._router.routing_table['chat'] = r.route

    def on_new_chat_member(self, msg, new_chat_member):
        print 'New chat member:', new_chat_member
        content_type, chat_type, chat_id = telepot.glance(msg)

        r = self.getChat(chat_id)
        print r

        r = self.getChatAdministrators(chat_id)
        print r
        print telepot.namedtuple.ChatMemberArray(r)

        r = self.getChatMembersCount(chat_id)
        print r

        while 1:
            try:
                self.setChatTitle(chat_id, 'AdminBot Title')
                print 'Set title successfully.'
                break
            except NotEnoughRightsError:
                print 'No right to set title. Try again in 10 seconds ...'
                time.sleep(10)

        while 1:
            try:
                self.setChatPhoto(chat_id, open('gandhi.png', 'rb'))
                print 'Set photo successfully.'
                time.sleep(2)  # let tester see photo briefly
                break
            except NotEnoughRightsError:
                print 'No right to set photo. Try again in 10 seconds ...'
                time.sleep(10)

        while 1:
            try:
                self.deleteChatPhoto(chat_id)
                print 'Delete photo successfully.'
                break
            except NotEnoughRightsError:
                print 'No right to delete photo. Try again in 10 seconds ...'
                time.sleep(10)

        print 'I am done. You may remove me from the group.'


TOKEN = sys.argv[1]

bot = AdminBot(TOKEN)
bot.message_loop()
print 'Send me a text message ...'

while 1:
    time.sleep(1)
