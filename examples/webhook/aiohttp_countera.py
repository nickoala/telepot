import sys
import asyncio
from aiohttp import web
import telepot
from telepot.aio.loop import OrderedWebhook
from telepot.aio.delegate import per_chat_id, create_open, pave_event_space

"""
$ python3.5 aiohttp_countera.py <token> <listening_port> <webhook_url>

Webhook path is '/webhook', therefore:

<webhook_url>: https://<base>/webhook
"""

class MessageCounter(telepot.aio.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageCounter, self).__init__(*args, **kwargs)
        self._count = 0

    async def on_chat_message(self, msg):
        self._count += 1
        await self.sender.sendMessage(self._count)

async def feeder(request):
    data = await request.text()
    webhook.feed(data)
    return web.Response(body='OK'.encode('utf-8'))

async def init(app, bot):
    app.router.add_route('GET', '/webhook', feeder)
    app.router.add_route('POST', '/webhook', feeder)

    await bot.setWebhook(URL)


TOKEN = sys.argv[1]
PORT = int(sys.argv[2])
URL = sys.argv[3]

loop = asyncio.get_event_loop()

app = web.Application(loop=loop)
bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, MessageCounter, timeout=10)],
    loop=loop)
webhook = OrderedWebhook(bot)

loop.run_until_complete(init(app, bot))

loop.create_task(webhook.run_forever())

try:
    web.run_app(app, port=PORT)
except KeyboardInterrupt:
    pass
