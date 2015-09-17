import sys
import time
import telepot

"""
$ python2.7 emodi.py <token>

Emodi: An Emoji Unicode Decoder - You send me an emoji, I give you the unicode.
"""

def handle(msg):
    msg_type, from_id, chat_id = telepot.glance(msg)
    m = telepot.namedtuple(msg, 'Message')

    if chat_id < 0:
        # group message
        print 'Received a %s from %s, by %s' % (msg_type, m.chat, m.from_)
    else:
        # private message
        print 'Received a %s from %s' % (msg_type, m.chat)  # m.chat == m.from_

    if msg_type == 'text':
        reply = ''

        # For long messages, only return the first 10 characters.
        if len(msg['text']) > 10:
            reply = u'First 10 characters:\n'

        reply += msg['text'][:10].encode('unicode-escape').decode('ascii')
        bot.sendMessage(chat_id, reply)


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.Bot(TOKEN)
bot.notifyOnMessage(handle)
print 'Listening ...'

# Keep the program running.
while 1:
    time.sleep(10)
