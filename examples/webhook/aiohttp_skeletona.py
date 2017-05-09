import sys
import asyncio
from aiohttp import web
import telepot
import telepot.aio
from telepot.aio.loop import OrderedWebhook

"""
$ python3.5 aiohttp_skeletona.py <token> <listening_port> <webhook_url>

Webhook path is '/webhook', therefore:

<webhook_url>: https://<base>/webhook
"""

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Chat Message:', content_type, chat_type, chat_id)

def on_callback_query(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    print('Callback query:', query_id, from_id, data)

# need `/setinline`
async def on_inline_query(msg):
    query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
    print('Inline Query:', query_id, from_id, query_string)

    # Compose your own answers
    articles = [{'type': 'article',
                    'id': 'abc', 'title': 'ABC', 'message_text': 'Good morning'}]

    await bot.answerInlineQuery(query_id, articles)

# need `/setinlinefeedback`
def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print('Chosen Inline Result:', result_id, from_id, query_string)

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
bot = telepot.aio.Bot(TOKEN, loop=loop)
webhook = OrderedWebhook(bot, {'chat': on_chat_message,
                               'callback_query': on_callback_query,
                               'inline_query': on_inline_query,
                               'chosen_inline_result': on_chosen_inline_result})

loop.run_until_complete(init(app, bot))

loop.create_task(webhook.run_forever())

try:
    web.run_app(app, port=PORT)
except KeyboardInterrupt:
    pass
