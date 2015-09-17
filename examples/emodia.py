import sys
import logging
import asyncio
import telepot
import telepot.async

"""
$ python3.4 emodia.py <token>

Emodi: An Emoji Unicode Decoder - You send me an emoji, I give you the unicode.
"""

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
logger = logging.getLogger()

@asyncio.coroutine
def handle(msg):
    msg_type, from_id, chat_id = telepot.glance(msg)
    m = telepot.namedtuple(msg, 'Message')

    if chat_id < 0:
        # group message
        logger.info('Received a %s from %s, by %s' % (msg_type, m.chat, m.from_))
    else:
        # private message
        logger.info('Received a %s from %s' % (msg_type, m.chat))  # m.chat == m.from_

    if msg_type == 'text':
        if msg['text'] == '/start':
            yield from bot.sendMessage(chat_id,  # Welcome message
                                       "You send me an Emoji"
                                       "\nI give you the Unicode"
                                       "\n\nOn Python 2, remember to prepend a 'u' to unicode strings,"
                                       "e.g. \U0001f604 is u'\\U0001f604'")
            return

        reply = ''

        # For long messages, only return the first 10 characters.
        if len(msg['text']) > 10:
            reply = 'First 10 characters:\n'

        reply += msg['text'][:10].encode('unicode-escape').decode('ascii')

        logger.info('>>> %s', reply)
        yield from bot.sendMessage(chat_id, reply)


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.async.Bot(TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop(handle))
logger.info('Listening ...')

loop.run_forever()
