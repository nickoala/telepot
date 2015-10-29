# telepot reference

**[telepot](#telepot)**
- [Bot](#telepot-Bot)
- [SpeakerBot](#telepot-SpeakerBot)
- [DelegatorBot](#telepot-DelegatorBot)
- [Functions](#telepot-functions)

**[telepot.helper](#telepot-helper)**
- [Microphone](#telepot-helper-Microphone)
- [Listener](#telepot-helper-Listener)
- [Sender](#telepot-helper-Sender)
- [ListenerContext](#telepot-helper-ListenerContext)
- [ChatContext](#telepot-helper-ChatContext)
- [Monitor](#telepot-helper-Monitor)
- [ChatHandler](#telepot-helper-ChatHandler)

**[telepot.delegate](#telepot-delegate)**
- [per_chat_id](#telepot-delegate-per-chat-id)
- [per_chat_id_in](#telepot-delegate-per-chat-id-in)
- [per_chat_id_except](#telepot-delegate-per-chat-id-except)
- [call](#telepot-delegate-call)
- [create_run](#telepot-delegate-create-run)
- [create_open](#telepot-delegate-create-open)

**[telepot.async](#telepot-async)** (Python 3.4.3 or newer)
- [Bot](#telepot-async-Bot)
- [SpeakerBot](#telepot-async-SpeakerBot)
- [DelegatorBot](#telepot-async-DelegatorBot)

**[telepot.async.helper](#telepot-async-helper)** (Python 3.4.3 or newer)
- [Microphone](#telepot-async-helper-Microphone)
- [Listener](#telepot-async-helper-Listener)

**[telepot.async.delegate](#telepot-async-delegate)**  (Python 3.4.3 or newer)
- [call](#telepot-async-delegate-call)
- [create_run](#telepot-async-delegate-create-run)
- [create_open](#telepot-async-delegate-create-open)

<a id="telepot"></a>
## `telepot` module

<a id="telepot-Bot"></a>
### `telepot.Bot`

This class is mostly a wrapper around Telegram Bot API methods, and is the most ancient part of telepot.

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
- run_forever (boolean): append an infinite loop at the end and never returns. Useful as the very last line in a program.

This can be a skeleton for a lot of telepot programs:

```python
import sys
import telepot

class YourBot(telepot.Bot):
    def handle(self, msg):
        content_type, chat_type, chat_id = telepot.glance2(msg)
        print content_type, chat_type, chat_id
        # Do your stuff according to `content_type` ...


TOKEN = sys.argv[1]  # get token from command-line

bot = YourBot(TOKEN)
bot.notifyOnMessage(run_forever=True)
```

If you prefer defining a global handler, or want to have a custom infinite loop at the end, this skeleton may be for you:

```python
import sys
import time
import telepot

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance2(msg)
    print content_type, chat_type, chat_id
    # Do your stuff according to `content_type` ...


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.Bot(TOKEN)
bot.notifyOnMessage(handle)
print 'Listening ...'

# Keep the program running.
while 1:
    time.sleep(10)
```

<a id="telepot-SpeakerBot"></a>
### `telepot.SpeakerBot`

Subclass of `Bot`. Exposes a `Microphone` and lets you create `Listener`s who listen to that microphone. You don't have to deal with this class directly, if `DelegateBot` and `ChatHandler` satisfy your needs.

**SpeakerBot(token)**

**mic**

A `Microphone` object. Used to broadcast messages to listeners obtained by `create_listener()`.

**create_listener()**

Returns a `Listener` object that listens to the `mic`.

<a id="telepot-DelegatorBot"></a>
### `telepot.DelegatorBot`

Subclass of `SpeakerBot`. Can spawn delegates according to *delegation patterns* specified in the constructor.

**DelegatorBot(token, delegation_patterns)**

Parameters:

- **token**: the bot's token
- **delegation_patterns**: a list of *(seed_calculating_function, delegate_producing_function)* tuples

*seed_calculating_function* is a function that takes one argument - the message being processed - and returns a *seed*. The seed determines whether and when the following *delegate_producing_function* is called.

- If the seed is a *hashable* (e.g. number, string, tuple), the bot looks for a *delegate* associated with the seed.
  - If such a delegate exists and is alive, it is assumed that the message will be picked up by the delegate. The bot does nothing.
  - If no delegate exists or that delegate is no longer alive, the bot spawns a new delegate by calling *delegate_producing_function* and associates the new delegate with the seed.

- If the seed is a *non-hashable* (e.g. list), the bot always spawns a new delegate by calling *delegate_producing_function*. No seed-delegate association occurs.

- If the seed is `None`, nothing is done.

**In essence, only one delegate is running for a given seed, if that seed is a hashable.**

*delegate_producing_function* is a function that takes one argument - a tuple of *(bot, message, seed)* - and returns a *delegate*. A delegate can be one of the following:

- an object that has a `start()` and `is_alive()` method. Therefore, a `threading.Thread` object is a natural delegate. Once the `object` is obtained, `object.start()` is called.
- a `function`, in which case it is wrapped by a `Thread(target=function)` and started.
- a tuple of `(function, args, kwargs)`, in which case it is wrapped by a `Thread(target=function, args=args, kwargs=kwargs)` and started.

All *seed_calculating_functions* are evaluated in order. One message may cause multiple delegates to be spawned.

This class implements the above logic in its `handle` method. Once you supply a list of *(seed_calculating_function, delegate_producing_function)* pairs to the constructor and invoke `notifyOnMessage()`, the above logic will be executed for every message received.

Even if you use a webhook and don't need `notifyOnMessage()`, you may always call `bot.handle(msg)` directly to take advantage of the above logic, if you find it useful.

The power of delegation is most easily exploited when used in combination with the `telepot.delegate` module (which contains a number of ready-made *seed_calculating_functions* and *delegate_producing_functions*) and the `ChatHandler` class (which provides a connection-like interface to deal with an individual chat).

Here is a bot that counts how many messages it has received in a chat. If no message is received after 10 seconds, it starts over. The counting is done *per chat* - that's the important point.

```python
import sys
import telepot
from telepot.delegate import per_chat_id, create_open

class MessageCounter(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(MessageCounter, self).__init__(seed_tuple, timeout)
        self._count = 0

    def on_message(self, msg):
        self._count += 1
        self.sender.sendMessage(self._count)

TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(MessageCounter, timeout=10)),
])
bot.notifyOnMessage(run_forever=True)
```

<a id="telepot-functions"></a>
### Functions in `telepot` module

**glance2(msg, long=False)**

If `long` is `False`, extract a tuple of *(content_type, chat_type, msg['chat']['id'])*.

If `long` is `True`, extract a tuple of *(content_type, chat_type, msg['chat']['id'], msg['date'], msg['message_id'])*.

*content_type* can be one of: `text`, `voice`, `sticker`, `photo`, `audio`, `document`, `video`, `contact`, `location`, `new_chat_participant`, `left_chat_participant`, `new_chat_title`, `new_chat_photo`, `delete_chat_photo`, or  `group_chat_created`.

*chat_type* can be one of: `private`, `group`, or `channel`.

*`glance2()` supercedes the old `glance()`, and will replace it eventually. You should not use `glance()` anymore.*

Examples:

```python
# Suppose `msg` is a message previously received.

content_type, chat_type, chat_id = telepot.glance2(msg)
content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance2(msg, long=True)
```

**namedtuple(dictionary, type)**

Convert a dictionary to a namedtuple of a given object type.

**type** can be: `Audio`, `Chat`, `Contact`, `Document`, `File`, `Location`, `Message`, `PhotoSize`, `PhotoSize[]`, `PhotoSize[][]`, `Sticker`, `Update`, `Update[]`, `User`, `UserProfilePhotos`, `Video`, `Voice`.

The returned namedtuples mirror the corresponding [Bot API objects](https://core.telegram.org/bots/api#available-types).

The source dictionary may not contain all necessary fields. Absent fields are set to `None`.

Namedtuple field names cannot be Python keywords, but the [Message](https://core.telegram.org/bots/api#message) object has a `from` field, which is a Python keyword. I choose to append an underscore to it. That is, the dictionary value `dict['from']` becomes `namedtuple.from_` when converted to a namedtuple.

Examples:

```python
# Suppose `msg` is a message (dict) previously received.

# Turn the entire message to a namedtuple
m = telepot.namedtuple(msg, 'Message')

print m.from_.id  # == msg['from']['id']
print m.chat.id   # == msg['chat']['id']

# Convert only part of the message
user = telepot.namedtuple(msg['from'], 'User')
chat = telepot.namedtuple(msg['chat'], 'Chat')
```

`namedtuple()` is just a convenience function. *Frankly, you can do without it.*

<a id="telepot-helper"></a>
## `telepot.helper` module

<a id="telepot-helper-Microphone"></a>
### `telepot.helper.Microphone`

A `Microphone`, when the `send()` method is called, puts messages into each `Listener`'s message queue.

Normally, you should not need to create this object, but obtain it using `SpeakerBot.mic`.

**Microphone()**

**add(queue)**

Add a listener's message queue.

**remove(queue)**

Remove a listener's message queue.

**send(msg)**

Puts `msg` into each listener's message queue.

<a id="telepot-helper-Listener"></a>
### `telepot.helper.Listener`

Used to suspend execution until a certain message appears. Users can specify how to "match" for messages in the `capture()` method.

Normally, you should not need to create this object, but obtain it using `SpeakerBot.create_listener()` or access it with `ChatHandler.listener`.

**Listener(microphone, queue)**

**wait()**

Blocks until a "matched" message appears, and returns that message. See `capture()` for how to specify match conditions.

If the *timeout* option is set, it will raise a `WaitTooLong` exception after that many seconds.

If the *timeout* option is not set or is `None` (default), it will wait forever.

**set_options(\*\*name_values)**

Available options:
- timeout - how many seconds to `wait` for a matched message

Example:
```python
listener.set_options(timeout=10)
```

**get_options(\*names)**

Returns a tuple of values of those option names.

Example:
```python
timeout, = listener.get_options('timeout')
```

**capture(\*\*criteria)**

Add a capture criteria.

When the `wait()` method sees a message that matches the *criteria*, it returns that message.

The `capture()` method may be called multiple times, resulting in a *list of criteria*. A message is considered a match if **any one of the those criteria** is satisfied.

The format of *criteria* is best illustrated with some examples:

```python
# look for messages whose `message['chat']['id']` equals `12345678`
listener.capture(chat__id=12345678)

# equivalent to above
listener.capture(chat={'id': 12345678})

def looks_like_integer(s):
    try:
        int(s)
        return True
    except:
        return False

# look for messages where `looks_like_integer(message['text'])` returns true
listener.capture(text=looks_like_integer)

# could be done more simply as ...
listener.capture(text=lambda s: s.isdigit())

# look for messages that satisfy BOTH conditions
listener.capture(text=lambda s: s.isdigit(), chat__id=12345678)

def sender_sounds_like_me(msg):
    return msg['from']['first_name'].startswith('Nick') and msg['from']['last_name'].startswith('Lee')

# looks for messages where `sender_sounds_like_me(message)` returns true
# use '_' to select the entire message
listener.capture(_=sender_sounds_like_me)
```

For each keyword arguments:

- the **key** is used to select a part of message
  - use a double__underscore to "get down a level", e.g. `from` selects `msg['from']`, `chat__id` selects `msg['chat']['id']`
  - use a `_` to select the entire message

- the **value** is a "template", may be one of the following:
  - a simple value
  - a function that checks the match
    - takes one argument - the part of message selected by the key
    - returns `True` to indicate a match
  - a dictionary to further select parts of message

When more than one keyword argument are given, all conditions have to be satisfied.

Thanks to **[Django](https://www.djangoproject.com/)** for inspiration.

**cancel_capture(\*\*criteria)**

Remove a capture criteria. To remove a previously added criteria, the form of *criteria* given here must be exactly the same as that given to `capture()` previously.

**clear_captures()**

Remove all capture criteria.

**list_captures()**

List all capture criteria.

<a id="telepot-helper-Sender"></a>
### `telepot.helper.Sender`

A proxy to a bot's `sendZZZ()` and `forwardMessage()` methods, with a fixed `chat_id` to save having to supply it every time.

Normally, you should not need to create this object, but access it with `ChatHandler.sender`.

**Sender(bot, chat_id)**

Parameters:
- **bot** - the parent bot
- **chat_id** - the default chat id. All messages will be aimed at this chat id.

**sendMessage(text, parse_mode=None, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None)**

**forwardMessage(from_chat_id, message_id)**

**sendPhoto(photo, caption=None, reply_to_message_id=None, reply_markup=None)**

**sendAudio(audio, duration=None, performer=None, title=None, reply_to_message_id=None, reply_markup=None)**

**sendDocument(document, reply_to_message_id=None, reply_markup=None)**

**sendSticker(sticker, reply_to_message_id=None, reply_markup=None)**

**sendVideo(video, duration=None, caption=None, reply_to_message_id=None, reply_markup=None)**

**sendVoice(audio, duration=None, reply_to_message_id=None, reply_markup=None)**

**sendLocation(latitude, longitude, reply_to_message_id=None, reply_markup=None)**

**sendChatAction(action)**

<a id="telepot-helper-ListenerContext"></a>
### `telepot.helper.ListenerContext`

**ListenerContext(bot, context_id)**

Parameters:
- **bot** - the parent bot. Should be a `SpeakerBot` or one of its subclasses.
- **context_id** - this ID's purpose and uniqueness to up to the user.

This object exposes these properties:
- **bot**
- **id** - the context ID
- **listener** - a `Listener` object

<a id="telepot-helper-ChatContext"></a>
### `telepot.helper.ChatContext`

**ChatContext(bot, context_id, chat_id)**

Parameters:
- **bot** - the parent bot. Should be a `SpeakerBot` or one of its subclasses.
- **context_id** - this ID's purpose and uniqueness to up to the user.
- **chat_id** - the target chat

This object exposes these properties:
- **chat_id**
- **sender** - a `Sender` object aimed at the target chat

<a id="telepot-helper-Monitor"></a>
### `telepot.helper.Monitor`

Coming ...

<a id="telepot-helper-ChatHandler"></a>
### `telepot.helper.ChatHandler`

Coming ...

<a id="telepot-delegate"></a>
## `telepot.delegate` module

This module provides functions used in conjunction with `DelegatorBot` to specify delegation patterns. See `DelegatorBot` for more details.

<a id="telepot-delegate-per-chat-id"></a>
**per_chat_id()**

Returns a seed-calculating-function that returns the chat id as the seed, equivalent to:
```python
lambda msg: msg['chat']['id']
```

<a id="telepot-delegate-per-chat-id-in"></a>
**per_chat_id_in(set)**

Returns a seed-calculating-function that returns the chat id as the seed if the chat id is in the `set`, equivalent to:
```python
lambda msg: msg['chat']['id'] if msg['chat']['id'] in set else None
```

<a id="telepot-delegate-per-chat-id-except"></a>
**per_chat_id_except(set)**

Returns a seed-calculating-function that returns the chat id as the seed if the chat id is *not* in the `set`, equivalent to:
```python
lambda msg: msg['chat']['id'] if msg['chat']['id'] not in set else None
```

<a id="telepot-delegate-call"></a>
**call(func, \*args, \*\*kwargs)**

Returns a delegate-producing-function that returns a tuple of `(func, (seed_tuple,)+args, kwargs)`, causing `DelegatorBot` to spawn a thread around that function and those arguments. `func` should take a *seed_tuple* as the first argument, followed by those explicitly supplied. Here is the source:

```python
def call(func, *args, **kwargs):
    def f(seed_tuple):
        return func, (seed_tuple,)+args, kwargs
    return f
```

<a id="telepot-delegate-create-run"></a>
**create_run(cls, \*args, \*\*kwargs)**

Returns a delegate-producing-function that creates an object of `cls` and returns its `run` method, causing `DelegatorBot` to spawn a thread around its `run` method. The `cls` constructor should take a *seed_tuple* as the first argument, followed by those explicitly supplied. The `run` method should take no argument. Here is the source:

```python
def create_run(cls, *args, **kwargs):
    def f(seed_tuple):
        j = cls(seed_tuple, *args, **kwargs)
        return j.run
    return f
```

<a id="telepot-delegate-create-open"></a>
**create_open(cls, \*args, \*\*kwargs)**

Coming ...

<a id="telepot-async"></a>
## `telepot.async` module (Python 3.4.3 or newer)

This package mirrors the traditional version of telepot to make use of the `asyncio` module of Python 3.4. Nearly all methods share identical signatures with their traditional siblings, except that blocking methods now become **coroutines** and are often called with `yield from`.

If you find this part of documentations wanting, always refer back to the traditional counterparts. It is easy to adapt examples from there to here - just remember to `yield from` coroutines.

<a id="telepot-async-Bot"></a>
### `telepot.async.Bot`

**Bot(token, loop=None)**

Use the token to specify the bot. If no `loop` is given, it uses `asyncio.get_event_loop()` to get the default event loop.

**loop**

This bot's event loop.

*coroutine* **getMe()**

Returns basic information about the bot in form of a [User](https://core.telegram.org/bots/api#user) object.

See: https://core.telegram.org/bots/api#getme

*coroutine* **sendMessage(chat_id, text, parse_mode=None, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None)**

Send text messages.

See: https://core.telegram.org/bots/api#sendmessage

*coroutine* **forwardMessage(chat_id, from_chat_id, message_id)**

Forward messages of any kind.

See: https://core.telegram.org/bots/api#forwardmessage

*coroutine* **sendPhoto(chat_id, photo, caption=None, reply_to_message_id=None, reply_markup=None)**

Send photos.

See: https://core.telegram.org/bots/api#sendphoto

*coroutine* **sendAudio(chat_id, audio, duration=None, performer=None, title=None, reply_to_message_id=None, reply_markup=None)**

Send audio files, if you want Telegram clients to display them in the music player. Your audio must be in the .mp3 format. For sending voice messages, use `sendVoice()` instead. 

See: https://core.telegram.org/bots/api#sendaudio

*coroutine* **sendDocument(chat_id, document, reply_to_message_id=None, reply_markup=None)**

Send general files.

See: https://core.telegram.org/bots/api#senddocument

*coroutine* **sendSticker(chat_id, sticker, reply_to_message_id=None, reply_markup=None)**

Send .webp stickers.

See: https://core.telegram.org/bots/api#sendsticker

*coroutine* **sendVideo(chat_id, video, duration=None, caption=None, reply_to_message_id=None, reply_markup=None)**

Send video files. Telegram clients support mp4 videos. Other formats may be sent using `sendDocument()`.

See: https://core.telegram.org/bots/api#sendvideo

*coroutine* **sendVoice(chat_id, audio, duration=None, reply_to_message_id=None, reply_markup=None)**

Send audio files, if you want Telegram clients to display the file as a playable voice message. For this to work, your audio must be in an .ogg file encoded with OPUS. Other formats may be sent using `sendAudio()` or `sendDocument()`.

See: https://core.telegram.org/bots/api#sendvoice

*coroutine* **sendLocation(chat_id, latitude, longitude, reply_to_message_id=None, reply_markup=None)**

Send point on the map.

See: https://core.telegram.org/bots/api#sendlocation

*coroutine* **sendChatAction(chat_id, action)**

Tell the user that something is happening on the bot's side. The status is set for 5 seconds or less (when a message arrives from your bot, Telegram clients clear its typing status).

See: https://core.telegram.org/bots/api#sendchataction

*coroutine* **getUserProfilePhotos(user_id, offset=None, limit=None)**

Get a list of profile pictures for a user.

See: https://core.telegram.org/bots/api#getuserprofilephotos

*coroutine* **getFile(file_id)**

Get a [File](https://core.telegram.org/bots/api#file) object, usually as a prelude to downloading a file. If you just want to download a file, call `downloadFile()` instead.

See: https://core.telegram.org/bots/api#getfile

*coroutine* **getUpdates(offset=None, limit=None, timeout=None)**

Receive incoming updates.

See: https://core.telegram.org/bots/api#getupdates

*coroutine* **setWebhook(url=None, certificate=None)**

Specify a url and receive incoming updates via an outgoing webhook.

See: https://core.telegram.org/bots/api#setwebhook

*coroutine* **downloadFile(file_id, dest)**

Download a file. `dest` can be a path (string) or a Python file object.

*coroutine* **messageLoop(handler=None)**

Functionally equivalent to `notifyOnMessage()`, this method constantly `getUpdates()` and applies `handler` to each message received.

`handler` must take one argument, which is the message.

If `handler` is a regular function, it is called directly from within `messageLoop()`.

If `handler` is a coroutine, it is allocated a task using `BaseEventLoop.create_task()`.

If `handler` is `None`, `self.handle` is assumed to be the handler function. In other words, a bot must have the method, `handle(msg)`, defined if `messageLoop()` is called without the `handler` argument.

This can be a skeleton for a lot of telepot programs:

```python
import sys
import asyncio
import telepot
import telepot.async

class YourBot(telepot.async.Bot):
    @asyncio.coroutine
    def handle(self, msg):
        content_type, chat_type, chat_id = telepot.glance2(msg)
        print(content_type, chat_type, chat_id)
        # Do your stuff according to `content_type` ...


TOKEN = sys.argv[1]  # get token from command-line

bot = YourBot(TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop())
print('Listening ...')

loop.run_forever()
```

Or, if you prefer a global handler:

```python
import sys
import asyncio
import telepot
import telepot.async

@asyncio.coroutine
def handle(msg):
    content_type, chat_type, chat_id = telepot.glance2(msg)
    print(content_type, chat_type, chat_id)
    # Do your stuff according to `content_type` ...


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.async.Bot(TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop(handle))
print('Listening ...')

loop.run_forever()
```

<a id="telepot-async-SpeakerBot"></a>
### `telepot.async.SpeakerBot`

Subclass of `telepot.async.Bot`. Exposes a `Microphone` and lets you create `Listener`s who listen to that microphone. You don't have to deal with this class directly, if `DelegateBot` and `ChatHandler` satisfy your needs.

**SpeakerBot(token)**

**mic**

A `Microphone` object. Used to broadcast messages to listeners obtained by `create_listener()`.

**create_listener()**

Returns a `Listener` object that listens to the `mic`.

<a id="telepot-async-DelegatorBot"></a>
### `telepot.async.DelegatorBot`

Subclass of `telepot.async.SpeakerBot`. Can create tasks according to *delegation patterns* specified in the constructor.

Unlike its traditional counterpart, this class uses **coroutine** and **task** to achieve delegation. To understand the remaining discussions, you have to understand asyncio's [tasks and coroutines](https://docs.python.org/3/library/asyncio-task.html), especially the difference between a *coroutine function* and a *coroutine object*.

**DelegatorBot(token, delegation_patterns)**

Parameters:

- **token**: the bot's token
- **delegation_patterns**: a list of *(seed_calculating_function, coroutine_producing_function)* tuples

*seed_calculating_function* is a function that takes one argument - the message being processed - and returns a *seed*. The seed determines whether and when the following *coroutine_producing_function* is called.

- If the seed is a *hashable* (e.g. number, string, tuple), the bot looks for a task associated with the seed.
  - If such a task exists and is not done, it is assumed that the message will be picked up by the task. The bot does nothing.
  - If no task exists or that task is done, the bot calls *coroutine_producing_function*, use the returned coroutine object to create a task, and associates the new task with the seed.

- If the seed is a *non-hashable* (e.g. list), the bot always calls *coroutine_producing_function*, and use the returned coroutine object to create a task. No seed-task association occurs.

- If the seed is `None`, nothing is done.

*coroutine_producing_function* is a function that takes one argument - a tuple of *(bot, message, seed)* - and returns a *coroutine object*, which will be used to create a task.

All *seed_calculating_functions* are evaluated in order. One message may cause multiple tasks to be created.

This class implements the above logic in its `handle` method. Once you supply a list of *(seed_calculating_function, coroutine_producing_function)* pairs to the constructor and invoke `messageLoop()`, the above logic will be executed for every message received.

Even if you use a webhook and don't need `messageLoop()`, you may always call `bot.handle(msg)` directly to take advantage of the above logic, if you find it useful.

The `telepot.delegate` module has a number of functions that help you define *seed_calculating_functions*.

The `telepot.async.delegate` module has a number of functions that help you define *coroutine_producing_functions*.

<a id="telepot-async-helper"></a>
## `telepot.async.helper` module (Python 3.4.3 or newer)

<a id="telepot-async-helper-Microphone"></a>
### `telepot.async.helper.Microphone`

A `Microphone`, when the `send()` method is called, puts messages into each `Listener`'s message queue.

Normally, you should not need to create this object, but access it using `SpeakerBot.mic`.

The only difference with traditional `telepot.helper.Microphone` is that it uses `asyncio.Queue` instead of the concurrent `Queue`.

**Microphone()**

**add(queue)**

Add a listener's message queue.

**remove(queue)**

Remove a listener's message queue.

**send(msg)**

Puts `msg` into each listener's message queue.

<a id="telepot-async-helper-Listener"></a>
### `telepot.async.helper.Listener`

Used to suspend execution until a certain message appears.

Normally, you should not need to create this object, but obtain it using `SpeakerBot.create_listener()` or access it with `ChatHandler.listener`.

The only difference with traditional `telepot.helper.Listener` is that it uses `asyncio.Queue` instead of the concurrent `Queue`, and the `wait` method becomes a coroutine.

**Listener(microphone, queue)**

*coroutine* **wait(\*\*kwargs)**

Wait for a "matched" message, and returns that message.

**kwargs** is used to select parts of message to match against. See `telepot.helper.Listener` for syntax.

<a id="telepot-async-delegate"></a>
## `telepot.async.delegate` module (Python 3.4.3 or newer)

This module provides functions used in conjunction with `telepot.async.DelegatorBot` to specify delegation patterns. See `telepot.async.DelegatorBot` for more details.

<a id="telepot-async-delegate-call"></a>
**call(corofunc, \*args, \*\*kwargs)**

Returns a coroutine-producing-function. `corofunc` should be a coroutine function that takes a *seed_tuple* as the first argument, followed by those explicitly supplied. Here is the source:

```python
def call(corofunc, *args, **kwargs):
    def f(seed_tuple):
        return corofunc(seed_tuple, *args, **kwargs)
    return f
```

<a id="telepot-async-delegate-create-run"></a>
**create_run(cls, \*args, \*\*kwargs)**

Returns a coroutine-producing-function that creates an object of `cls` and returns a coroutine object by calling its `run()` method. The `cls` constructor should take a *seed_tuple* as the first argument, followed by those explicitly supplied. The `run` method should be a coroutine function that takes no argument. Here is the source:

```python
def create_run(cls, *args, **kwargs):
    def f(seed_tuple):
        j = cls(seed_tuple, *args, **kwargs)
        return j.run()
    return f
```
