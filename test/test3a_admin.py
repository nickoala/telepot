import sys
import asyncio
import telepot
import telepot.namedtuple
import telepot.aio
from telepot.aio.routing import by_content_type, make_content_type_routing_table
from telepot.exception import NotEnoughRightsError

class AdminBot(telepot.aio.Bot):
    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if 'edit_date' not in msg:
            await self.sendMessage(chat_id, 'Edit the message, please.')
        else:
            await self.sendMessage(chat_id, 'Add me to a group, please.')

            # Make a router to route `new_chat_member` and `left_chat_member`
            r = telepot.aio.helper.Router(by_content_type(), make_content_type_routing_table(self))

            # Replace current handler with that router
            self._router.routing_table['chat'] = r.route

    async def on_new_chat_member(self, msg, new_chat_member):
        print('New chat member:', new_chat_member)
        content_type, chat_type, chat_id = telepot.glance(msg)

        r = await self.getChat(chat_id)
        print(r)

        r = await self.getChatAdministrators(chat_id)
        print(r)
        print(telepot.namedtuple.ChatMemberArray(r))

        r = await self.getChatMembersCount(chat_id)
        print(r)

        while 1:
            try:
                await self.setChatTitle(chat_id, 'AdminBot Title')
                print('Set title successfully.')
                break
            except NotEnoughRightsError:
                print('No right to set title. Try again in 10 seconds ...')
                await asyncio.sleep(10)

        while 1:
            try:
                await self.setChatPhoto(chat_id, open('gandhi.png', 'rb'))
                print('Set photo successfully.')
                await asyncio.sleep(2)  # let tester see photo briefly
                break
            except NotEnoughRightsError:
                print('No right to set photo. Try again in 10 seconds ...')
                await asyncio.sleep(10)

        while 1:
            try:
                await self.deleteChatPhoto(chat_id)
                print('Delete photo successfully.')
                break
            except NotEnoughRightsError:
                print('No right to delete photo. Try again in 10 seconds ...')
                await asyncio.sleep(10)

        print('I am done. Remove me from the group.')

    async def on_left_chat_member(self, msg, left_chat_member):
        print('I see that I have left.')


TOKEN = sys.argv[1]

bot = AdminBot(TOKEN)
loop = asyncio.get_event_loop()
#loop.set_debug(True)

loop.create_task(bot.message_loop())
print('Send me a text message ...')

loop.run_forever()
