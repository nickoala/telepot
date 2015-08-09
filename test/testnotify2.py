import time
import threading
import ConfigParser
import telepot

CONFIG_FILE = '/home/pi/.telepot'

parser = ConfigParser.ConfigParser()
parser.read(CONFIG_FILE)

TOKEN = parser.get('test', 'BOT_TOKEN')
bot = telepot.Bot(TOKEN)

def handle1(msg):
    print '1. Received message from ID: %d' % msg['from']['id']
    print 'Content:', msg['text']

def handle2(msg):
    print '^^2^^ Received message from ID: %d' % msg['from']['id']
    print 'Content:', msg['text']

def handle3(msg):
    print '-----3----- Received message from ID: %d' % msg['from']['id']
    print 'Content:', msg['text']

def print_active_thread_count():
    while 1:
        print 'Number of active threads: %d' % threading.active_count()
        time.sleep(5)

t = threading.Thread(target=print_active_thread_count)
t.daemon = True
t.start()

print 'handle1() ...'
bot.notifyOnMessage(handle1)
time.sleep(30)

print 'No handler ...'
bot.notifyOnMessage(None)
time.sleep(30)

print 'handle2() ...'
bot.notifyOnMessage(handle2, timeout=0)
time.sleep(30)

print 'handle3() ...'
bot.notifyOnMessage(handle3)

while 1:
    time.sleep(10)
