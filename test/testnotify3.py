import time
import threading
import sys
import telepot

def handle1(msg):
    if msg['from']['id'] != USER_ID:
        print('Unauthorized user:', msg['from']['id'])
        return

    print('1. Received message from ID: %d' % msg['from']['id'])
    print('Content:', msg['text'])

def handle2(msg):
    if msg['from']['id'] != USER_ID:
        print('Unauthorized user:', msg['from']['id'])
        return

    print('^^2^^ Received message from ID: %d' % msg['from']['id'])
    print('Content:', msg['text'])

def handle3(msg):
    if msg['from']['id'] != USER_ID:
        print('Unauthorized user:', msg['from']['id'])
        return

    print('-----3----- Received message from ID: %d' % msg['from']['id'])
    print('Content:', msg['text'])

def print_active_thread_count():
    while 1:
        print('Number of active threads: %d' % threading.active_count())
        time.sleep(5)


TOKEN = sys.argv[1]
USER_ID = int(sys.argv[2])

bot = telepot.Bot(TOKEN)
print(bot.getMe())  # check token

t = threading.Thread(target=print_active_thread_count)
t.daemon = True
t.start()

print('I am listening with handle1() ...')
bot.notifyOnMessage(handle1)
time.sleep(30)

print('Stop listening for a while ...')
bot.notifyOnMessage(None)
time.sleep(30)

print('I am listening with handle2() ...')
bot.notifyOnMessage(handle2, timeout=0)
time.sleep(30)

print('I am listening with handle3() ...')
bot.notifyOnMessage(handle3)

while 1:
    time.sleep(10)
