import time
import sys
import configparser
import telepot

CONFIG_FILE = '/home/pi/.telepot'

parser = configparser.ConfigParser()
parser.read(CONFIG_FILE)

TOKEN = parser.get('test', 'BOT_TOKEN')
bot = telepot.Bot(TOKEN)

def handle(msg):
    msg_id = msg['message_id']
    chat_id = msg['from']['id']

    print('Received message from ID: %d' % chat_id)
    print('Start sending various messages ...')

    bot.sendMessage(chat_id, 'Hello, I am going to send you a lot of things.', reply_to_message_id=msg_id)

    show_keyboard = {'keyboard': [['Yes', 'No'], ['Maybe', 'Maybe not']]}
    bot.sendMessage(chat_id, 'Here is a custom keyboard', reply_markup=show_keyboard)

    time.sleep(2)

    hide_keyboard = {'hide_keyboard': True}
    bot.sendMessage(chat_id, 'Hiding it now.', reply_markup=hide_keyboard)

    bot.sendChatAction(chat_id, 'upload_photo')
    r = bot.sendPhoto(chat_id, open('lighthouse.jpg', 'rb'), caption='This is a lighthouse')

    file_id = r['photo'][0]['file_id']
    bot.sendPhoto(chat_id, file_id, caption='Same lighthouse again')

    bot.sendChatAction(chat_id, 'upload_audio')
    r = bot.sendAudio(chat_id, open('dgdg.mp3', 'rb'))

    file_id = r['audio']['file_id']
    bot.sendAudio(chat_id, file_id)

    bot.sendMessage(chat_id, 'I am done.')

print('Text me, please.')
bot.notifyOnMessage(handle)

while 1:
    time.sleep(10)
