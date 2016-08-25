import sys
import time
import telepot
import telepot.namedtuple

"""
$ python2.7 emodi.py <token>

Emodi: An Emoji Unicode Decoder - You send it some emoji, it tells you the unicodes.

Caution: Python's treatment of unicode characters longer than 2 bytes (which
most emojis are) varies across versions and platforms. I have tested this program
on Python2.7.9/Raspbian. If you try it on other versions/platforms, the length-
checking and substring-extraction below may not work as expected.
"""

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    m = telepot.namedtuple.Message(**msg)

    if chat_id < 0:
        # group message
        print 'Received a %s from %s, by %s' % (content_type, m.chat, m.from_)
    else:
        # private message
        print 'Received a %s from %s' % (content_type, m.chat)  # m.chat == m.from_

    if content_type == 'text':
        reply = ''

        # For long messages, only return the first 10 characters.
        if len(msg['text']) > 10:
            reply = u'First 10 characters:\n'

        # Length-checking and substring-extraction may work differently
        # depending on Python versions and platforms. See above.

        reply += msg['text'][:10].encode('unicode-escape').decode('ascii')
        bot.sendMessage(chat_id, reply)


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print 'Listening ...'

# Keep the program running.
while 1:
    time.sleep(10)
