# coding=utf8

import time
import sys
import pprint
import telepot

def handle(msg):
    if msg['from']['id'] != USER_ID:
        print('Unauthorized user:', msg['from']['id'])
        return

    msg_id = msg['message_id']
    chat_id = msg['from']['id']

    print('Received message from ID: %d' % chat_id)
    print('Start sending various messages ...')

    ##### forwardMessage
    
    bot.forwardMessage(chat_id, chat_id, msg_id)

    ##### sendMessage

    bot.sendMessage(chat_id, 'Hello, I am going to send you a lot of things.', reply_to_message_id=msg_id)

    bot.sendMessage(chat_id, '中文')

    bot.sendMessage(chat_id, 'http://www.yahoo.com\nwith web page preview')

    bot.sendMessage(chat_id, 'http://www.yahoo.com\nno web page preview', disable_web_page_preview=True)

    show_keyboard = {'keyboard': [['Yes', 'No'], ['Maybe', 'Maybe not']]}
    bot.sendMessage(chat_id, 'Here is a custom keyboard', reply_markup=show_keyboard)

    time.sleep(2)

    hide_keyboard = {'hide_keyboard': True}
    bot.sendMessage(chat_id, 'Hiding it now.', reply_markup=hide_keyboard)

    force_reply = {'force_reply': True}
    bot.sendMessage(chat_id, 'Force reply', reply_markup=force_reply)

    ##### sendPhoto

    bot.sendChatAction(chat_id, 'upload_photo')
    r = bot.sendPhoto(chat_id, open('lighthouse.jpg', 'rb'))

    pprint.pprint(r)
    file_id = r['photo'][0]['file_id']
    print('Photo file id:', file_id)

    bot.sendPhoto(chat_id, file_id, caption='Show original message and keyboard', reply_to_message_id=msg_id, reply_markup=show_keyboard)

    bot.sendPhoto(chat_id, file_id, caption='Hide keyboard', reply_markup=hide_keyboard)

    ##### sendAudio
    # Need one of `performer` or `title' for server to regard it as audio. Otherwise, server treats it as voice.

    bot.sendChatAction(chat_id, 'upload_audio')
    r = bot.sendAudio(chat_id, open('dgdg.mp3', 'rb'), title='Ringtone')

    pprint.pprint(r)
    file_id = r['audio']['file_id']
    print('Audio file id:', file_id)

    bot.sendAudio(chat_id, file_id, duration=6, performer='Ding Dong', title='Ringtone', reply_to_message_id=msg_id, reply_markup=show_keyboard)

    bot.sendAudio(chat_id, file_id, performer='Ding Dong', reply_markup=hide_keyboard)

    ##### sendDocument

    bot.sendChatAction(chat_id, 'upload_document')
    r = bot.sendDocument(chat_id, open('document.txt', 'rb'))

    pprint.pprint(r)
    file_id = r['document']['file_id']
    print('Document file id:', file_id)

    bot.sendDocument(chat_id, file_id, reply_to_message_id=msg_id, reply_markup=show_keyboard)

    bot.sendDocument(chat_id, file_id, reply_markup=hide_keyboard)

    ##### sendSticker

    r = bot.sendSticker(chat_id, open('gandhi.png', 'rb'))

    pprint.pprint(r)
    file_id = r['sticker']['file_id']
    print('Sticker file id:', file_id)

    bot.sendSticker(chat_id, file_id, reply_to_message_id=msg_id, reply_markup=show_keyboard)

    bot.sendSticker(chat_id, file_id, reply_markup=hide_keyboard)

    ##### sendVideo

    bot.sendChatAction(chat_id, 'upload_video')
    r = bot.sendVideo(chat_id, open('hktraffic.mp4', 'rb'))

    pprint.pprint(r)
    file_id = r['video']['file_id']
    print('Video file id:', file_id)

    bot.sendVideo(chat_id, file_id, duration=5, caption='Hong Kong traffic', reply_to_message_id=msg_id, reply_markup=show_keyboard)

    bot.sendVideo(chat_id, file_id, reply_markup=hide_keyboard)

    ##### sendVoice

    r = bot.sendVoice(chat_id, open('example.ogg', 'rb'))

    pprint.pprint(r)
    file_id = r['voice']['file_id']
    print('Voice file id:', file_id)

    bot.sendVoice(chat_id, file_id, duration=6, reply_to_message_id=msg_id, reply_markup=show_keyboard)

    bot.sendVoice(chat_id, file_id, reply_markup=hide_keyboard)

    ##### sendLocation

    bot.sendChatAction(chat_id, 'find_location')
    bot.sendLocation(chat_id, 22.33, 114.18)  # Hong Kong

    bot.sendLocation(chat_id, 49.25, -123.1, reply_to_message_id=msg_id, reply_markup=show_keyboard)  # Vancouver

    bot.sendLocation(chat_id, -37.82, 144.97, reply_markup=hide_keyboard)  # Melbourne

    ##### getUserProfilePhotos

    # Reply: Is this your photo? Report number of photos
    # Download photo

    ##### Bye

    bot.sendMessage(chat_id, 'I am done.')


TOKEN = sys.argv[1]
USER_ID = int(sys.argv[2])

bot = telepot.Bot(TOKEN)
print(bot.getMe())  # check token

print('Text me, please.')
bot.notifyOnMessage(handle)

while 1:
    time.sleep(10)
