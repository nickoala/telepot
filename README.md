# telepot

**P**ython wrapper for **Tele**gram B**ot** API

To use the [Telegram Bot API](https://core.telegram.org/bots/api), you first have to get a **bot account** by [chatting with the BotFather](https://core.telegram.org/bots).

He will then give you a **token**, something like `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`. With the token in hand, you can start using telepot to access the bot account.

Telepot works with **Python 2.7 & 3**, although instructions below are presented with Python 2.7. They are based on **Raspbian**, the only platform I have tested on.

#### Installation

`sudo apt-get install python-pip` to install the Python package manager.

`sudo pip install telepot` to install the telepot library.

#### Test the account

```python
>>> import telepot
>>> bot = telepot.Bot('***** PUT YOUR TOKEN HERE *****')
>>> bot.getMe()
{u'username': u'YourBot', u'first_name': u'Your Bot', u'id': 123456789}
```

#### Receive messages

Bots cannot initiate conversations with users. You have to send it a message first. It gets the message by calling `getUpdates()`.

```python
>>> from pprint import pprint
>>> response = bot.getUpdates()
>>> pprint(response)
[{u'message': {u'chat': {u'first_name': u'Nick',
                         u'id': 999999999,
                         u'last_name': u'Lee'},
               u'date': 1436423831,
               u'from': {u'first_name': u'Nick',
                         u'id': 999999999,
                         u'last_name': u'Lee'},
               u'message_id': 106,
               u'text': u'Hi, how are you?'},
  u'update_id': 100000000}]
```

`999999999` is obviously a fake ID. `Nick` `Lee` is my real name, though.

Also note the `update_id`. It is an ever-increasing number. Next time you should use `getUpdates(offset=100000001)` to avoid getting the same old messages over and over. Giving an `offset` essentially acknowledges to the server that you have received all `update_id`s lower than `offset`.

```python
>>> bot.getUpdates(offset=100000001)
[]
```

#### An easier way to receive messages

It is kind of troublesome to keep checking messages. Fortunately, telepot can take care of the checking for you, and notify you whenever new messages arrive.

```python
>>> from pprint import pprint
>>> def handle_message(msg):
...     pprint(msg)
...
>>>  bot.notifyOnMessage(handle_message)
```

After setting up this callback, you may send various messages to the bot, and inspect their message structures.

#### Send messages

Use a proper ID in place of `999999999`.

```python
>>> bot.sendMessage(999999999, 'I am fine')
```

#### Send a custom keyboard

This is Telegram's Great Feature! A custom keyboard presents custom buttons for users to tab. Check it out.

```python
>>> show_keyboard = {'keyboard': [['Yes','No'], ['Maybe','Maybe not']]}
>>> bot.sendMessage(999999999, 'This is a custom keyboard', reply_markup=show_keyboard)
```

#### Hide the custom keyboard

```python
>>> hide_keyboard = {'hide_keyboard': True}
>>> bot.sendMessage(999999999, 'I am hiding it', reply_markup=hide_keyboard)
```

#### Send files

You may also send photos, videos, audios, documents, and stickers.

```python
>>> f = open('zzzzzzzz.png', 'rb')  # this is some file on local disk
>>> response = bot.sendPhoto(999999999, f)
>>> pprint(response)
{u'chat': {u'first_name': u'Nick', u'id': 999999999, u'last_name': u'Lee'},
 u'date': 1436428640,
 u'from': {u'first_name': u'Your Bot',
           u'id': 123456789,
           u'username': u'YourBot'},
 u'message_id': 117,
 u'photo': [{u'file_id': u'APNpmPKVulsdkIFAILMDmhTAADmdcmdsdfaldalk',
             u'file_size': 2030,
             u'height': 64,
             u'width': 64},
            {u'file_id': u'VgbD_v___6AInvuOAlPldf',
             u'file_size': 7987,
             u'height': 0,
             u'width': 0}]}
```

Note that the server returns a number of `file_id`s, with various file sizes. These are thumbnails of the uploaded image. If you want to resend the same file, just give one of the `file_id`s.

```python
>>> bot.sendPhoto(999999999, 'APNpmPKVulsdkIFAILMDmhTAADmdcmdsdfaldalk')
```

---------

Aside from the `Bot` constructor and `notifyOnMessage()`, all methods are straight mappings from **[Telegram Bot API](https://core.telegram.org/bots/api)**. No point to duplicate all the details here. I will only give brief descriptions below, and encourage you to visit the underlying API's documentations. Full power of the Bot API can be exploited only by understanding the API itself.

Just remember one thing: all Bot API's **objects** are nothing more than Python **dicts**.

**Bot(token)**

Use the token to specify the bot.

Examples:
```python
import telepot
bot = telepot.Bot('123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ')
```

**getMe()**

Returns basic information about the bot in form of a [User](https://core.telegram.org/bots/api#user) object.

See: https://core.telegram.org/bots/api#getme

**sendMessage(chat_id, text, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None)**

Send text messages.

See: https://core.telegram.org/bots/api#sendmessage

Examples:
```python
# Assuming you have got `chat_id` and `msg_id` from a previously received message by doing:
#     msg_id = msg['message_id']
#     chat_id = msg['from']['id']
# or
#     chat_id = msg['chat']['id']

bot.sendMessage(chat_id, 'A short sentence.')

bot.sendMessage(chat_id, 'I do not understand your last message.', reply_to_message_id=msg_id)

bot.sendMessage(chat_id, 'http://www.yahoo.com \n no web page preview', disable_web_page_preview=True)

# Show a custom keyboard
show_keyboard = {'keyboard': [['Yes', 'No'], ['Maybe', 'Maybe not']]}
bot.sendMessage(chat_id, 'Here is a custom keyboard', reply_markup=show_keyboard)

# Hide custom keyboard
hide_keyboard = {'hide_keyboard': True}
bot.sendMessage(chat_id, 'Hiding it now.', reply_markup=hide_keyboard)

# Force reply
force_reply = {'force_reply': True}
bot.sendMessage(chat_id, 'Force reply', reply_markup=force_reply)
```

**forwardMessage(chat_id, from_chat_id, message_id)**

Forward messages of any kind.

See: https://core.telegram.org/bots/api#forwardmessage

**sendPhoto(chat_id, photo, caption=None, reply_to_message_id=None, reply_markup=None)**

Send photos.

See: https://core.telegram.org/bots/api#sendphoto

Examples:
```python
# Uploading a file may take a while. Let user know you are doing something.
bot.sendChatAction(chat_id, 'upload_photo')

# Send a file that is stored locally.
result = bot.sendPhoto(chat_id, open('lighthouse.jpg', 'rb'))

# Get `file_id` from the Message object returned.
file_id = result['photo'][0]['file_id']

# Use `file_id` to resend the same photo, with a caption this time.
bot.sendPhoto(chat_id, file_id, caption='This is a lighthouse')
```

**sendAudio(chat_id, audio, duration=None, performer=None, title=None, reply_to_message_id=None, reply_markup=None)**

Send audio files, if you want Telegram clients to display them in the music player. Your audio must be in the .mp3 format. For sending voice messages, use `sendVoice()` instead. 

See: https://core.telegram.org/bots/api#sendaudio

Examples:
```python
# Uploading a file may take a while. Let user know you are doing something.
bot.sendChatAction(chat_id, 'upload_audio')

# Send an audio file that is stored locally.
# Parameter `performer` or `title` has to be set for Telegram to regard it as an audio.
# Otherwise, it will be treated as voice.
result = bot.sendAudio(chat_id, open('dgdg.mp3', 'rb'), title='Ringtone')

# Get `file_id` from the Message object returned.
file_id = result['audio']['file_id']

# Use `file_id` to resend the same audio file.
# Remember to include either `performer` or `title` (or both).
bot.sendAudio(chat_id, file_id, duration=6, performer='Ding Dong')
```

**sendDocument(chat_id, document, reply_to_message_id=None, reply_markup=None)**

Send general files.

See: https://core.telegram.org/bots/api#senddocument

Examples:
```python
bot.sendChatAction(chat_id, 'upload_document')
result = bot.sendDocument(chat_id, open('document.txt', 'rb'))

file_id = result['document']['file_id']
bot.sendDocument(chat_id, file_id)
```

**sendSticker(chat_id, sticker, reply_to_message_id=None, reply_markup=None)**

Send .webp stickers.

See: https://core.telegram.org/bots/api#sendsticker

Examples:
```python
# I found .png files are also accepted. Other formats? You have to try it yourself.
result = bot.sendSticker(chat_id, open('gandhi.png', 'rb'))

file_id = result['sticker']['file_id']
bot.sendSticker(chat_id, file_id)
```

**sendVideo(chat_id, video, duration=None, caption=None, reply_to_message_id=None, reply_markup=None)**

Send video files. Telegram clients support mp4 videos. Other formats may be sent using `sendDocument()`.

See: https://core.telegram.org/bots/api#sendvideo

Examples:
```python
bot.sendChatAction(chat_id, 'upload_video')

# Send a video file that is stored locally, with a caption.
result = bot.sendVideo(chat_id, open('hktraffic.mp4', 'rb'), caption='Hong Kong traffic')

file_id = result['video']['file_id']

# Use `file_id` to resend a video file, with a duration stated this time.
bot.sendVideo(chat_id, file_id, duration=5)
```

**sendVoice(chat_id, audio, duration=None, reply_to_message_id=None, reply_markup=None)**

Send audio files, if you want Telegram clients to display the file as a playable voice message. For this to work, your audio must be in an .ogg file encoded with OPUS. Other formats may be sent using `sendAudio()` or `sendDocument()`.

See: https://core.telegram.org/bots/api#sendvoice

Examples:
```python
# Send a voice message that is stored locally.
result = bot.sendVoice(chat_id, open('example.ogg', 'rb'))

file_id = result['voice']['file_id']

# Use `file_id` to resend the voice message, with a duration stated this time.
bot.sendVoice(chat_id, file_id, duration=6)
```

**sendLocation(chat_id, latitude, longitude, reply_to_message_id=None, reply_markup=None)**

Send point on the map.

See: https://core.telegram.org/bots/api#sendlocation

Examples:
```python
bot.sendChatAction(chat_id, 'find_location')
bot.sendLocation(chat_id, 22.33, 114.18)   # Hong Kong
bot.sendLocation(chat_id, 49.25, -123.1)   # Vancouver
bot.sendLocation(chat_id, -37.82, 144.97)  # Melbourne
```

**sendChatAction(chat_id, action)**

Tell the user that something is happening on the bot's side. The status is set for 5 seconds or less (when a message arrives from your bot, Telegram clients clear its typing status).

See: https://core.telegram.org/bots/api#sendchataction

Examples: Please refer to examples for `sendPhoto()`, `sendVideo()`, `sendDocument()`, etc.

**getUserProfilePhotos(user_id, offset=None, limit=None)**

Get a list of profile pictures for a user.

See: https://core.telegram.org/bots/api#getuserprofilephotos

**getUpdates(offset=None, limit=None, timeout=None)**

Receive incoming updates.

See: https://core.telegram.org/bots/api#getupdates

**setWebhook(url=None)**

Specify a url and receive incoming updates via an outgoing webhook.

See: https://core.telegram.org/bots/api#setwebhook

**notifyOnMessage(callback, relax=1, timeout=20)**

Spawn a thread to constantly `getUpdates()`. Apply `callback` to every message received. `callback` must take one argument, which is the message.

Parameters:
- callback (function): a function to apply to every message received
- relax (integer): seconds between each `getUpdates()`
- timeout (integer): timeout supplied to `getUpdates()`, controlling how long to poll.

This method allows you to change the callback function by `notifyOnMessage(new_callback)`. 
If you don't want to receive messages anymore, cancel the callback by `notifyOnMessage(None)`. 
After the callback is cancelled, the message-checking thread will terminate. 
If a new callback is set later, a new thread will be spawned again.

Examples:
```python
import time
import pprint
import telepot

def handle(msg):
    pprint.pprint(msg)

bot = telepot.Bot('***** TOKEN *****')
bot.notifyOnMessage(handle)

# Keep the program running.
while 1:
    time.sleep(10)
```
