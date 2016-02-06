import sys
import asyncio
from aiohttp import web
import telepot
import telepot.async

"""
$ python3.4 webhook_aiohttp_skeletona.py <token> <listening_port> <webhook_url>
"""

@asyncio.coroutine
def handle(msg):
    flavor = telepot.flavor(msg)

    # normal message
    if flavor == 'normal':
        content_type, chat_type, chat_id = telepot.glance(msg)
        print('Normal Message:', content_type, chat_type, chat_id)

        # Do your stuff according to `content_type` ...

    # inline query - need `/setinline`
    elif flavor == 'inline_query':
        query_id, from_id, query_string = telepot.glance(msg, flavor=flavor)
        print('Inline Query:', query_id, from_id, query_string)

        # Compose your own answers
        articles = [{'type': 'article',
                        'id': 'abc', 'title': 'ABC', 'message_text': 'Good morning'}]

        yield from bot.answerInlineQuery(query_id, articles)

    # chosen inline result - need `/setinlinefeedback`
    elif flavor == 'chosen_inline_result':
        result_id, from_id, query_string = telepot.glance(msg, flavor=flavor)
        print('Chosen Inline Result:', result_id, from_id, query_string)

        # Remember the chosen answer to do better next time

    else:
        raise telepot.BadFlavor(msg)


TOKEN = sys.argv[1]
PORT = int(sys.argv[2])
URL = sys.argv[3]

bot = telepot.async.Bot(TOKEN)
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
loop.create_task(bot.messageLoop(handle, source=update_queue))  # take updates from queue
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
