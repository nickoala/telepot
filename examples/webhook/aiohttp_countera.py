import sys
import asyncio
from aiohttp import web
import telepot
from telepot.aio.delegate import per_chat_id, create_open

"""
$ python3.5 aiohttp_countera.py <token> <listening_port> <webhook_url>

Webhook path is '/abc', therefore:

<webhook_url>: https://<base>/abc
"""

class MessageCounter(telepot.aio.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(MessageCounter, self).__init__(seed_tuple, timeout)
        self._count = 0

    @asyncio.coroutine
    def on_chat_message(self, msg):
        self._count += 1
        yield from self.sender.sendMessage(self._count)


TOKEN = sys.argv[1]
PORT = int(sys.argv[2])
URL = sys.argv[3]

bot = telepot.aio.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(MessageCounter, timeout=10)),
])
update_queue = asyncio.Queue()  # channel between web app and bot

@asyncio.coroutine
def webhook(request):
    data = yield from request.text()
    yield from update_queue.put(data)  # pass update to bot
    return web.Response(body='OK'.encode('utf-8'))

@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/abc', webhook)
    app.router.add_route('POST', '/abc', webhook)

    srv = yield from loop.create_server(app.make_handler(), '0.0.0.0', PORT)
    print("Server started ...")

    yield from bot.setWebhook(URL)

    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.create_task(bot.message_loop(source=update_queue))  # take updates from queue
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
