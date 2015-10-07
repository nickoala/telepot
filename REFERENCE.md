# telepot reference

## Modules

**[telepot](#telepot)**  
**[telepot.helper](#telepot-helper)**  
**[telepot.delegate](#telepot-delegate)**  
**[telepot.async](#telepot-async)**  
**[telepot.async.helper](#telepot-async-helper)**  
**[telepot.async.delegate](#telepot-async-delegate)**  

<a id="telepot"></a>
## telepot

### `telepot.Bot`

Aside from `downloadFile()` and `notifyOnMessage()`, all methods are straight mappings from **[Telegram Bot API](https://core.telegram.org/bots/api)**. No point to duplicate all the details here. I only give brief descriptions below, and encourage you to visit the underlying API's documentations. Full power of the Bot API can be exploited only by understanding the API itself.

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

**sendMessage(chat_id, text, parse_mode=None, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None)**

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

# Support very basic markdown since 2.0
bot.sendMessage(chat_id, '*bold text*\n_italic text_\n[link](http://www.google.com)', parse_mode='Markdown')

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

**getFile(file_id)**

Get a [File](https://core.telegram.org/bots/api#file) object, usually as a prelude to downloading a file. If you just want to download a file, call `downloadFile()` instead.

See: https://core.telegram.org/bots/api#getfile

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

**downloadFile(file_id, dest)**

Download a file. `dest` can be a path (string) or a Python file object.

Examples:
```python
bot.downloadFile('ABcdEfGhijkLm_NopQRstuvxyZabcdEFgHIJ', 'save/to/path')

# If you open the file yourself, you are responsible for closing it.
with open('save/to/path', 'wb') as f:
    bot.downloadFile('ABcdEfGhijkLm_NopQRstuvxyZabcdEFgHIJ', f)
```

**notifyOnMessage(callback=None, relax=0.1, timeout=20, run_forever=False)**

Spawn a thread to constantly `getUpdates()`. Apply `callback` to every message received. `callback` must take one argument, which is the message.

If `callback` is not supplied, `self.handle` is assumed. In other words, a bot must have the method, `handle(msg)`, defined if `notifyOnMessage()` is called without the `callback` argument.

Parameters:
- callback (function): a function to apply to every message received. If `None`, `self.handle` is assumed. 
- relax (integer): seconds between each `getUpdates()`
- timeout (integer): timeout supplied to `getUpdates()`, controlling how long to poll.
- run_forever (boolean): append an infinite loop at the end, so this function never returns. Useful as the very last line in a program.

This method allows you to change the callback function by `notifyOnMessage(new_callback)`. 
If you don't want to receive messages anymore, cancel the callback by `notifyOnMessage(None)`. 
After the callback is cancelled, the message-checking thread will terminate. 
If a new callback is set later, a new thread will be spawned again.

This can be a skeleton for a lot of telepot programs:

```python
import sys
import telepot

class YourBot(telepot.Bot):
    def handle(self, msg):
        msg_type, from_id, chat_id = telepot.glance(msg)
        print msg_type, from_id, chat_id
        # Do your stuff according to `msg_type` ...


TOKEN = sys.argv[1]  # get token from command-line

bot = YourBot(TOKEN)
bot.notifyOnMessage(run_forever=True)
```

If you prefer defining a `handle(msg)` function externally, or want to have a custom infinite loop at the end, this skeleton may be for you:

```python
import sys
import time
import telepot

def handle(msg):
    msg_type, from_id, chat_id = telepot.glance(msg)
    print msg_type, from_id, chat_id
    # Do your stuff according to `msg_type` ...


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.Bot(TOKEN)
bot.notifyOnMessage(handle)
print 'Listening ...'

# Keep the program running.
while 1:
    time.sleep(10)
```

### `telepot.SpeakerBot`

Subclass of `telepot.Bot`

**SpeakerBot(token)**

**create_listener()**

Returns a `telepot.helper.Listener` object, which you may use to listen for messages broadcast by `mic.send(msg)`.

**mic**

A `telepot.helper.Microphone` object. Used to broadcast messages to listeners obtained by `create_listener()`.

### `telepot.DelegatorBot`

Subclass of `telepot.SpeakerBot`

**DelegatorBot(token, seed_delegates)**

Parameters:

- token: self-explanatory
- seed_delegates: a list of `(seed_calculating_func, delegate_producing_func)` tuples

`seed_calculating_func` is a function that takes one argument - the message being processed - and returns a *seed*. The **type** and **value** of a seed determine whether and when the associated `delegate_producing_func` is called.

- If the seed is a *hashable* (e.g. number, string, tuple), the bot looks for a *delegate* associated with the seed.
  - If such a delegate exists and is alive, it is assumed that the message will be picked up by the delegate. The bot does nothing.
  - If no delegate exists or that delegate is no longer alive, the bot spawns a new delegate by calling `delegate_producing_func` and associates the seed with the new delegate.

- If the seed is a *non-hashable* (e.g. list), the bot always spawns a new delegate by calling `delegate_producing_func`. No seed-delegate association occurs.

- If the seed is `None`, nothing is done.

`delegate_producing_func` is a function that takes one argument - a tuple of `(bot, msg, seed)` - and returns a *delegate*. A delegate can be one of the following:

- an object that has a `start()` and `is_alive()` method. Therefore, a `threading.Thread` object is a natural delegate. Once the `object` is obtained, `object.start()` is called.
- a `function`. In this case, it is wrapped by a `Thread(target=function)` and started.
- a tuple of `(func, args, kwargs)`. In this case, it is wrapped by a `Thread(target=func, args=args, kwargs=kwargs)` and started.

All `seed_calculating_func`s are evaluated in order. One message may cause multiple delegates to be spawned.

This class implements the above logic in its `handle(msg)` method. Once you supply a list of `(seed_calculating_func, delegate_producing_func)` pairs to the constructor and invoke `notifyOnMessage()`, the above logic will be executed for each message received.

Even if you use a webhook and don't need `notifyOnMessage()`, you may always call `bot.handle(msg)` directly to take advantage of the above logic, if you find it useful.

The `telepot.delegate` module has a number of functions that make it very convenient to define `seed_calculating_func` and `delegate_producing_func`, as illustrated by the example below:

```python
import sys
import telepot
from telepot.delegate import per_chat_id, per_chat_id_in, call, create_run

class Handler(object):
    # a tuple of `(bot, msg, seed)` is always the first argument
    def __init__(self, seed_tuple):
        print('In Handler constructor ...')
        print(seed_tuple)

    def run(self):
        print('In Handler.run() ...')

# a tuple of `(bot, msg, seed)` is always the first argument
def delegate_func(seed_tuple):
    print('In delegate_func() ...')
    print(seed_tuple)

TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.DelegatorBot(TOKEN, [

# Per each chat id --> spawn a thread around `delegate_func` and supplied arguments
(lambda msg: msg['chat']['id'], lambda seed_tuple: (delegate_func, [seed_tuple], {})),

# Achieve exactly the same thing as above, but easier to understand
(per_chat_id(), call(delegate_func)),

# Per each chat id --> create a `Handler` object and spawn a thread around its `run()` method
(per_chat_id(), create_run(Handler)),

# Spawn only per selected chat id
(per_chat_id_in([12345678, 999999999]), create_run(Handler)),
      ])

bot.notifyOnMessage(run_forever=True)
```

### Functions in `telepot` module

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

`type` can be: `Audio`, `Contact`, `Document`, `GroupChat`, `Location`, `Message`, `PhotoSize`, `PhotoSize[]`, `PhotoSize[][]`, `Sticker`, `Update`, `Update[]`, `User`, `User/GroupChat`, `UserProfilePhotos`, `Video`, `Voice`, `File`.

Namedtuple field names cannot be Python keywords, but the **[Message](https://core.telegram.org/bots/api#message)** object has a `from` field, which is a Python keyword. I choose to append an underscore to it. That is, the dictionary value `dict['from']` becomes `namedtuple.from_` when converted to a namedtuple.

Examples:

```python
# Suppose `msg` is a message (dict) previously received.

# Turn the entire message to a namedtuple
m = telepot.namedtuple(msg, 'Message')

print m.from_.id  # == msg['from']['id']
print m.chat.id   # == msg['chat']['id']

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

<a id="telepot-helper"></a>
## telepot.helper

### `telepot.helper.Microphone`

One `Microphone` broadcasts to many `Listener`s. Each listener has a queue. Microphone puts messages into the queues, listeners get from them. Adding a queue to a microphone essentially adds a listener to its audience.

**Microphone()**

**add(queue)**

Add a listener's queue.

**remove(queue)**

Remove a listener's queue.

**send(msg)**

Broadcast to all listeners by putting `msg` to each queue.

### `telepot.helper.Listener`

**Listener(microphone, queue)**

**wait(\*\*kwargs)**

Coming soon ......

### `telepot.helper.Sender`

### `telepot.helper.ChatHandler`

<a id="telepot-delegate"></a>
## telepot.delegate

Coming soon ...

<a id="telepot-async"></a>
## telepot.async (Python 3.4.3 or newer)

### `telepot.async.Bot`

This class makes use of the `asyncio` module of Python 3.4.3. Nearly all methods share identical signatures with its traditional sibling, `telepot.Bot`, with one important difference - they are **coroutines** and are often "called" with `yield from`.

Notable differences are given below.

**Bot(token, loop=None)**

Use the token to specify the bot. If no `loop` is given, it uses `asyncio.get_event_loop()` to get the default event loop.

Examples:
```python
import telepot.async
bot = telepot.async.Bot('123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ')
```

**messageLoop(handler)**

Functionally equivalent to `notifyOnMessage()`, this method constantly `getUpdates()` and applies `handler` to each message received.

`handler` must take one argument, which is the message.

If `handler` is a regular function, it is called directly from within `messageLoop()`.

If `handler` is a coroutine, it is allocated a task using `BaseEventLoop.create_task()`.

An async skeleton:

```python
import sys
import asyncio
import telepot
import telepot.async

# Add this decorator if you have `yield from` inside the function.
# @asyncio.coroutine
def handle(msg):
    msg_type, from_id, chat_id = telepot.glance(msg)
    print(msg_type, from_id, chat_id)
    # Do your stuff according to `msg_type` ...


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.async.Bot(TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop(handle))
print('Listening ...')

loop.run_forever()
```

<a id="telepot-async-helper"></a>
## telepot.async.helper (Python 3.4.3 or newer)

Coming soon ...

<a id="telepot-async-delegate"></a>
## telepot.async.delegate (Python 3.4.3 or newer)

Coming soon ...
