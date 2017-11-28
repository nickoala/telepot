# coding=utf8

import time
import threading
import pprint
import sys
import traceback
import urllib.request
import telepot
import telepot.namedtuple

"""
This script tests:
- setWebhook() and getUpdates(), and make sure they are exclusive
- sendZZZ() and sendChatAction() methods
- getUserProfilePhotos()

Run it by:
$ python3.X test3.py <token> <user_id>

It will assume the bot identified by <token>, and only communicate with the user identified by <user_id>.

If you don't know your user id, run:
$ python test.py <token> 0

And send it a message anyway. It will print out your user id as an unauthorized user.
Ctrl-C to kill it, then run the proper command again.
"""

def equivalent(data, nt):
    if type(data) is dict:
        keys = list(data.keys())

        # number of dictionary keys == number of non-None values in namedtuple?
        if len(keys) != len([f for f in nt._fields if getattr(nt, f) is not None]):
            return False

        # map `from` to `from_`
        fields = list([k+'_' if k in ['from'] else k for k in keys])

        return all(map(equivalent, [data[k] for k in keys], [getattr(nt, f) for f in fields]))
    elif type(data) is list:
        return all(map(equivalent, data, nt))
    else:
        return data==nt

def examine(result, type):
    try:
        print('Examining %s ......' % type)

        nt = type(**result)
        assert equivalent(result, nt), 'Not equivalent:::::::::::::::\n%s\n::::::::::::::::\n%s' % (result, nt)

        pprint.pprint(result)
        pprint.pprint(nt)
        print()
    except AssertionError:
        traceback.print_exc()
        answer = input('Do you want to continue? [y] ')
        if answer != 'y':
            exit(1)

def send_everything_on_contact(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)

    if chat_id != USER_ID:
        print('Unauthorized user:', msg['from']['id'])
        exit(1)

    print('Received message from ID: %d' % chat_id)
    print('Start sending various messages ...')

    ##### forwardMessage

    r = bot.forwardMessage(chat_id, chat_id, msg_id)
    examine(r, telepot.namedtuple.Message)

    ##### sendMessage

    r = bot.sendMessage(chat_id, 'Hello, I am going to send you a lot of things.', reply_to_message_id=msg_id)
    examine(r, telepot.namedtuple.Message)
    time.sleep(0.5)

    r = bot.sendMessage(chat_id, '中文')
    examine(r, telepot.namedtuple.Message)
    time.sleep(0.5)

    r = bot.sendMessage(chat_id, '*bold text*\n_italic text_\n[link](http://www.google.com)', parse_mode='Markdown')
    examine(r, telepot.namedtuple.Message)
    time.sleep(0.5)

    bot.sendMessage(chat_id, 'http://www.yahoo.com\nwith web page preview')
    time.sleep(0.5)

    bot.sendMessage(chat_id, 'http://www.yahoo.com\nno web page preview', disable_web_page_preview=True)
    time.sleep(0.5)

    show_keyboard = {'keyboard': [['Yes', 'No'], ['Maybe', 'Maybe not']]}
    remove_keyboard = {'remove_keyboard': True}
    force_reply = {'force_reply': True}

    nt_show_keyboard = telepot.namedtuple.ReplyKeyboardMarkup(**show_keyboard)
    nt_remove_keyboard = telepot.namedtuple.ReplyKeyboardRemove(**remove_keyboard)
    nt_force_reply = telepot.namedtuple.ForceReply(**force_reply)

    bot.sendMessage(chat_id, 'Here is a custom keyboard', reply_markup=show_keyboard)
    time.sleep(0.5)

    bot.sendMessage(chat_id, 'Hiding it now.', reply_markup=nt_remove_keyboard)
    time.sleep(0.5)

    bot.sendMessage(chat_id, 'Force reply', reply_markup=nt_force_reply)
    time.sleep(0.5)

    ##### sendPhoto

    bot.sendChatAction(chat_id, 'upload_photo')
    r = bot.sendPhoto(chat_id, open('lighthouse.jpg', 'rb'))
    examine(r, telepot.namedtuple.Message)
    time.sleep(0.5)

    file_id = r['photo'][0]['file_id']

    bot.sendPhoto(chat_id, file_id, caption='Show original message and keyboard', reply_to_message_id=msg_id, reply_markup=nt_show_keyboard)
    time.sleep(0.5)

    bot.sendPhoto(chat_id, file_id, caption='Hide keyboard', reply_markup=remove_keyboard)
    time.sleep(0.5)

    furl = urllib.request.urlopen('http://i.imgur.com/35HSRQ6.png')
    bot.sendPhoto(chat_id, ('abc.jpg', furl))
    time.sleep(0.5)

    bot.sendPhoto(chat_id, ('中文照片.jpg', open('lighthouse.jpg', 'rb')), caption='中文照片')
    time.sleep(0.5)

    ##### getFile

    f = bot.getFile(file_id)
    examine(f, telepot.namedtuple.File)

    ##### download_file, smaller than one chunk (65K)

    try:
        print('Downloading file to non-existent directory ...')
        bot.download_file(file_id, 'non-existent-dir/file')
    except:
        print('Error: as expected')

    print('Downloading file to down.1 ...')
    bot.download_file(file_id, 'down.1')

    print('Open down.2 and download to it ...')
    with open('down.2', 'wb') as down:
        bot.download_file(file_id, down)

    ##### sendAudio
    # Need one of `performer` or `title' for server to regard it as audio. Otherwise, server treats it as voice.

    bot.sendChatAction(chat_id, 'upload_audio')
    r = bot.sendAudio(chat_id, open('dgdg.mp3', 'rb'), title='Ringtone')
    examine(r, telepot.namedtuple.Message)
    time.sleep(0.5)

    file_id = r['audio']['file_id']

    bot.sendAudio(chat_id, file_id, duration=6, performer='Ding Dong', title='Ringtone', reply_to_message_id=msg_id, reply_markup=show_keyboard)
    time.sleep(0.5)

    bot.sendAudio(chat_id, file_id, performer='Ding Dong', reply_markup=nt_remove_keyboard)
    time.sleep(0.5)

    bot.sendAudio(chat_id, ('中文歌.mp3', open('dgdg.mp3', 'rb')), title='中文歌')
    time.sleep(0.5)

    ##### sendDocument

    bot.sendChatAction(chat_id, 'upload_document')
    r = bot.sendDocument(chat_id, open('document.txt', 'rb'))
    examine(r, telepot.namedtuple.Message)
    time.sleep(0.5)

    file_id = r['document']['file_id']

    bot.sendDocument(chat_id, file_id, reply_to_message_id=msg_id, reply_markup=nt_show_keyboard)
    time.sleep(0.5)

    bot.sendDocument(chat_id, file_id, reply_markup=remove_keyboard)
    time.sleep(0.5)

    bot.sendDocument(chat_id, ('中文文件.txt', open('document.txt', 'rb')))
    time.sleep(0.5)

    ##### sendSticker

    r = bot.sendSticker(chat_id, open('gandhi.png', 'rb'))
    examine(r, telepot.namedtuple.Message)
    time.sleep(0.5)

    file_id = r['sticker']['file_id']

    bot.sendSticker(chat_id, file_id, reply_to_message_id=msg_id, reply_markup=show_keyboard)
    time.sleep(0.5)

    bot.sendSticker(chat_id, file_id, reply_markup=nt_remove_keyboard)
    time.sleep(0.5)

    ##### sendVideo

    bot.sendChatAction(chat_id, 'upload_video')
    r = bot.sendVideo(chat_id, open('hktraffic.mp4', 'rb'))
    examine(r, telepot.namedtuple.Message)
    time.sleep(0.5)

    try:
        file_id = r['video']['file_id']

        bot.sendVideo(chat_id, file_id, duration=5, caption='Hong Kong traffic', reply_to_message_id=msg_id, reply_markup=nt_show_keyboard)
        time.sleep(0.5)
        bot.sendVideo(chat_id, file_id, reply_markup=remove_keyboard)
        time.sleep(0.5)

    except KeyError:
        # For some reason, Telegram servers may return a document.
        print('****** sendVideo returns a DOCUMENT !!!!!')

        file_id = r['document']['file_id']

        bot.sendDocument(chat_id, file_id, reply_to_message_id=msg_id, reply_markup=nt_show_keyboard)
        time.sleep(0.5)
        bot.sendDocument(chat_id, file_id, reply_markup=remove_keyboard)
        time.sleep(0.5)

    ##### download_file, multiple chunks

    print('Downloading file to down.3 ...')
    bot.download_file(file_id, 'down.3')

    ##### sendVoice

    r = bot.sendVoice(chat_id, open('example.ogg', 'rb'))
    examine(r, telepot.namedtuple.Message)
    time.sleep(0.5)

    file_id = r['voice']['file_id']

    bot.sendVoice(chat_id, file_id, duration=6, reply_to_message_id=msg_id, reply_markup=show_keyboard)
    time.sleep(0.5)

    bot.sendVoice(chat_id, file_id, reply_markup=nt_remove_keyboard)
    time.sleep(0.5)

    ##### sendVideoNote

    bot.sendVideoNote(chat_id, open('hktraffic.mp4', 'rb'), length=2)

    ##### sendMediaGroup

    with open('lighthouse.jpg', 'rb') as f1, open('gandhi.png', 'rb') as f2, open('bookshelf.jpg', 'rb') as f3, open('saturn.jpg', 'rb') as f4:
        ms = [
            telepot.namedtuple.InputMediaPhoto(media=f1),
            telepot.namedtuple.InputMediaPhoto(media=('media2', f2)),
            telepot.namedtuple.InputMediaPhoto(media='https://telegram.org/file/811140935/175c/FSf2aidnuaY.21715.gif/31dc2dbb6902dcef78'),
            {'type': 'photo', 'media': ('media3', ('books.jpg', f3))},
            {'type': 'photo', 'media': f4},
        ]
        bot.sendMediaGroup(chat_id, ms)

    ##### sendLocation

    bot.sendChatAction(chat_id, 'find_location')
    r = bot.sendLocation(chat_id, 22.33, 114.18)  # Hong Kong
    examine(r, telepot.namedtuple.Message)
    time.sleep(0.5)

    bot.sendLocation(chat_id, 49.25, -123.1, reply_to_message_id=msg_id, reply_markup=nt_show_keyboard)  # Vancouver
    time.sleep(0.5)

    bot.sendLocation(chat_id, -37.82, 144.97, reply_markup=remove_keyboard)  # Melbourne
    time.sleep(0.5)

    r = bot.sendLocation(chat_id, -37.82, 144.97, live_period=60)  # Melbourne
    time.sleep(3)

    mif = telepot.message_identifier(r)
    bot.editMessageLiveLocation(mif, -37.819, 144.97)
    time.sleep(1)

    bot.editMessageLiveLocation(mif, -37.818, 144.97)
    time.sleep(1)

    bot.stopMessageLiveLocation(mif)

    ##### sendGame

    bot.sendGame(chat_id, 'sunchaser')
    time.sleep(0.5)

    game_keyboard = telepot.namedtuple.InlineKeyboardMarkup(inline_keyboard=[[
                        telepot.namedtuple.InlineKeyboardButton(text='Play now', callback_game=True),
                        telepot.namedtuple.InlineKeyboardButton(text='How to play?', url='https://mygame.com/howto'),
                    ]])
    bot.sendGame(chat_id, 'sunchaser', reply_markup=game_keyboard)
    time.sleep(0.5)

    ##### Done sending messages

    bot.sendMessage(chat_id, 'I am done.')

def get_user_profile_photos():
    print('Getting user profile photos ...')

    r = bot.getUserProfilePhotos(USER_ID)
    examine(r, telepot.namedtuple.UserProfilePhotos)

expected_content_type = None
content_type_iterator = iter([
    'text', 'voice', 'sticker', 'photo', 'audio' ,'document', 'video', 'contact', 'location',
    'new_chat_member',  'new_chat_title', 'new_chat_photo',  'delete_chat_photo', 'left_chat_member'
])

def see_every_content_types(msg):
    global expected_content_type, content_type_iterator

    content_type, chat_type, chat_id = telepot.glance(msg)
    from_id = msg['from']['id']

    if chat_id != USER_ID and from_id != USER_ID:
        print('Unauthorized user:', chat_id, from_id)
        return

    examine(msg, telepot.namedtuple.Message)
    try:
        if content_type == expected_content_type:
            expected_content_type = next(content_type_iterator)
            bot.sendMessage(chat_id, 'Please give me a %s.' % expected_content_type)
        else:
            bot.sendMessage(chat_id, 'It is not a %s. Please give me a %s, please.' % (expected_content_type, expected_content_type))
    except StopIteration:
        # reply to sender because I am kicked from group already
        bot.sendMessage(from_id, 'Thank you. I am done.')

def ask_for_various_messages():
    bot.message_loop(see_every_content_types)

    global expected_content_type, content_type_iterator
    expected_content_type = next(content_type_iterator)

    bot.sendMessage(USER_ID, 'Please give me a %s.' % expected_content_type)

def test_webhook_getupdates_exclusive():
    bot.setWebhook('https://www.fake.com/fake', open('old.cert', 'rb'))
    print('Fake webhook set.')

    try:
        bot.getUpdates()
    except telepot.exception.TelegramError as e:
        print("%d: %s" % (e.error_code, e.description))
        print('As expected, getUpdates() produces an error.')

    bot.setWebhook()
    print('Fake webhook cancelled.')


TOKEN = sys.argv[1]
USER_ID = int(sys.argv[2])

bot = telepot.Bot(TOKEN)

test_webhook_getupdates_exclusive()
get_user_profile_photos()

print('Text me to start.')
bot.message_loop(send_everything_on_contact, run_forever=True)
