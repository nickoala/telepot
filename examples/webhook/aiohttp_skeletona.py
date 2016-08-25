import sys
import asyncio
from aiohttp import web
import telepot
import telepot.aio

"""
$ python3.5 aiohttp_skeletona.py <token> <listening_port> <webhook_url>

Webhook path is '/abc', therefore:

<webhook_url>: https://<base>/abc
"""

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Chat Message:', content_type, chat_type, chat_id)

def on_callback_query(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    print('Callback query:', query_id, from_id, data)

# need `/setinline`
@asyncio.coroutine
def on_inline_query(msg):
    query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
    print('Inline Query:', query_id, from_id, query_string)

    # Compose your own answers
    articles = [{'type': 'article',
                    'id': 'abc', 'title': 'ABC', 'message_text': 'Good morning'}]

    yield from bot.answerInlineQuery(query_id, articles)

# need `/setinlinefeedback`
def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print('Chosen Inline Result:', result_id, from_id, query_string)


TOKEN = sys.argv[1]
PORT = int(sys.argv[2])
URL = sys.argv[3]

bot = telepot.aio.Bot(TOKEN)
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
loop.create_task(
    bot.message_loop({
        'chat': on_chat_message,
        'callback_query': on_callback_query,
        'inline_query': on_inline_query,
        'chosen_inline_result': on_chosen_inline_result},
        source=update_queue))  # take updates from queue
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
