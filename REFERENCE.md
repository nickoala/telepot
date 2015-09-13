# telepot reference

## Functions

**glance(msg, long=False)**

If `long` is `False`, extract a tuple of `(type, msg['from']['id'], msg['chat']['id'])`.

If `long` is `True`, extract a tuple of `(type, msg['from']['id'], msg['chat']['id'], msg['date'], msg['message_id'])`.

`type` indicates the content type of the message, can be one of:  `text`, `voice`, `sticker`, `photo`, `audio`, `document`, `video`, `contact`, `location`, `new_chat_participant`, `left_chat_participant`, `new_chat_title`, `new_chat_photo`, `delete_chat_photo`, `group_chat_created`.

Examples:

```python
# Suppose `msg` is a message previously received.

msg_type, from_id, chat_id = telepot.glance(msg)
msg_type, from_id, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
```

**namedtuple(data, type)**

Convert a dictionary to a namedtuple of a given object type.

`type` can be: `Audio`, `Contact`, `Document`, `GroupChat`, `Location`, `Message`, `PhotoSize`, `PhotoSize[]`, `PhotoSize[][]`, `Sticker`, `Update`, `Update[]`, `User`, `User/GroupChat`, `UserProfilePhotos`, `Video`, `Voice`.

Examples:

```python
# Suppose `msg` is a message (dict) previously received.

# Turn the entire message to a namedtuple
m = telepot.namedtuple(msg, 'Message')

# Turn only the 'from' field to a User namedtuple
u = telepot.namedtuple(msg['from'], 'User')

# 'chat' field can be either a User or GroupChat
chat = telepot.namedtuple(msg['chat'], 'User/GroupChat')

if type(chat) == telepot.User:
    print 'A private conversation'
elif type(chat) == telepot.GroupChat:
    print 'An open discussion'
else:
    print 'Impossible!'

# Actually, you can check more efficiently by looking at the chat ID.
# A negative ID indicates a GroupChat; a positive ID indicates a User.
```

`namedtuple()` is just a convenience function. *Frankly, you can do without it.*

## telepot.Bot

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

**setWebhook(url=None, certificate=None)**

Specify a url and receive incoming updates via an outgoing webhook.

*Since 1.2*, you may upload your public key certificate with the `certificate` argument.

See: https://core.telegram.org/bots/api#setwebhook

Examples:
```python
# Webhook without a certificate
bot.setWebhook('https://www.domain.com/webhook')

# Webhook with a certificate
bot.setWebhook('https://www.domain.com/webhook', open('domain.cert', 'rb'))

# Cancel webhook
bot.setWebhook()
```

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

This can be a skeleton for a lot of telepot programs:

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
