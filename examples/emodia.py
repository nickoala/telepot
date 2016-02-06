import sys
import logging
import asyncio
import os
import configparser
import telepot
import telepot.namedtuple
import telepot.async

"""
$ python3.4 emodia.py <config_path>

Emodi: An Emoji Unicode Decoder - You send me an emoji, I give you the unicode.

Because this program is run on a hosted server, I don't want the token on the
command-line, which may be seen by listing the processes. I put the token in a 
config file, which looks like:

[emodia.py]
bot_token = .........

Caution: Python's treatment of unicode characters longer than 2 bytes (which 
most emojis are) varies across versions and platforms. I have tested this program 
on Python3.4.3/Raspbian & CentOS6. If you try it on other versions/platforms, the
length-checking and substring-extraction below may not work as expected.
"""

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
logger = logging.getLogger()

@asyncio.coroutine
def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    m = telepot.namedtuple.namedtuple(msg, 'Message')

    if chat_id < 0:
        # group message
        logger.info('Received a %s from %s, by %s' % (content_type, m.chat, m.from_))
    else:
        # private message
        logger.info('Received a %s from %s' % (content_type, m.chat))  # m.chat == m.from_

    if content_type == 'text':
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

        # Length-checking and substring-extraction may work differently 
        # depending on Python versions and platforms. See above.

        reply += msg['text'][:10].encode('unicode-escape').decode('ascii')

        logger.info('>>> %s', reply)
        yield from bot.sendMessage(chat_id, reply)


# Read token from config file, whose path is specified on command-line.
config = configparser.ConfigParser()
config.read(sys.argv[1])

filename = os.path.basename(sys.argv[0])

TOKEN = config[filename]['bot_token']

bot = telepot.async.Bot(TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop(handle))
logger.info('Listening ...')

loop.run_forever()
