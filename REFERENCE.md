# telepot 6.3 reference

**[telepot](#telepot)**
- [Bot](#telepot-Bot)
- [SpeakerBot](#telepot-SpeakerBot)
- [DelegatorBot](#telepot-DelegatorBot)
- [Functions](#telepot-functions)

**[telepot.namedtuple](#telepot-namedtuple)**
- [Convert dictionary to namedtuple](#telepot-namedtuple-convert)
- [Use namedtuple constructors](#telepot-namedtuple-construct)

**[telepot.helper](#telepot-helper)**
- [Microphone](#telepot-helper-Microphone)
- [Listener](#telepot-helper-Listener)
- [Sender](#telepot-helper-Sender)
- [Answerer](#telepot-helper-Answerer)
- [ListenerContext](#telepot-helper-ListenerContext)
- [ChatContext](#telepot-helper-ChatContext)
- [UserContext](#telepot-helper-UserContext)
- [Monitor](#telepot-helper-Monitor)
- [ChatHandler](#telepot-helper-ChatHandler)
- [UserHandler](#telepot-helper-UserHandler)
- [@openable](#telepot-helper-openable)

**[telepot.delegate](#telepot-delegate)**
- [per_chat_id](#telepot-delegate-per-chat-id)
- [per_chat_id_in](#telepot-delegate-per-chat-id-in)
- [per_chat_id_except](#telepot-delegate-per-chat-id-except)
- [per_from_id](#telepot-delegate-per-from-id)
- [per_from_id_in](#telepot-delegate-per-from-id-in)
- [per_from_id_except](#telepot-delegate-per-from-id-except)
- [per_inline_from_id](#telepot-delegate-per-inline-from-id)
- [per_inline_from_id_in](#telepot-delegate-per-inline-from-id-in)
- [per_inline_from_id_except](#telepot-delegate-per-inline-from-id-except)
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
- [Answerer](#telepot-async-helper-Answerer)

**[telepot.async.delegate](#telepot-async-delegate)**  (Python 3.4.3 or newer)
- [call](#telepot-async-delegate-call)
- [create_run](#telepot-async-delegate-create-run)
- [create_open](#telepot-async-delegate-create-open)

<a id="telepot"></a>
## `telepot` module

<a id="telepot-Bot"></a>
### `telepot.Bot`

*Subclass:* [`telepot.SpeakerBot`](#telepot-SpeakerBot)

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

# Markdown
bot.sendMessage(chat_id, '*bold text*\n_italic text_\n[link](http://www.google.com)', parse_mode='Markdown')

# HTML
bot.sendMessage(chat_id, '<i>italic</i> <code>inline fixed-width code</code>', parse_mode='HTML')

# Show a custom keyboard
show_keyboard = {'keyboard': [['Yes', 'No'], ['Maybe', 'Maybe not']]}
bot.sendMessage(chat_id, 'Here is a custom keyboard', reply_markup=show_keyboard)

# Hide custom keyboard
hide_keyboard = {'hide_keyboard': True}
bot.sendMessage(chat_id, 'Hiding it now.', reply_markup=hide_keyboard)

# Force reply
force_reply = {'force_reply': True}
bot.sendMessage(chat_id, 'Force reply', reply_markup=force_reply)

# `reply_markup` also accepts namedtuples
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply

bot.sendMessage(chat_id, 'Show keyboard', reply_markup=ReplyKeyboardMarkup(keyboard=[['Yes', 'No']]))

bot.sendMessage(chat_id, 'Hide keyboard', reply_markup=ReplyKeyboardHide())

bot.sendMessage(chat_id, 'Force reply', reply_markup=ForceReply())
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

Specify a url and receive incoming updates via an outgoing webhook. Optionally, you may upload your public key certificate with the `certificate` argument.

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

**answerInlineQuery(inline_query_id, results, cache_time=None, is_personal=None, next_offset=None)**

Send answers to an inline query. `results` is a list of [InlineQueryResult](https://core.telegram.org/bots/api#inlinequeryresult). As is the custom in telepot, you may construct those objects as **dictionaries**. A potentially easier alternative is to use the namedtuple classes provided by `telepot.namedtuple` module.

See: https://core.telegram.org/bots/api#answerinlinequery

Examples:

```python
from telepot.namedtuple import InlineQueryResultArticle

articles = [{'type': 'article',
                'id': 'abc', 'title': 'ABC', 'message_text': 'Good morning'},
            InlineQueryResultArticle(
                id='xyz', title='ZZZZZ', message_text='Good night')]

bot.answerInlineQuery(query_id, articles)
```

```python
from telepot.namedtuple import InlineQueryResultPhoto

photos = [{'type': 'photo',
              'id': '123', 'photo_url': '...', 'thumb_url': '...'},
          InlineQueryResultPhoto(
              id='999', photo_url='...', thumb_url='...')]

bot.answerInlineQuery(query_id, photos)
```

**notifyOnMessage(callback=None, relax=0.1, timeout=20, source=None, ordered=True, maxhold=3, run_forever=False)**

Spawn a thread to constantly check for updates. Apply `callback` to every message received. `callback` must take one argument, which is the message.

If `callback` is not supplied, `self.handle` is assumed. In other words, a bot must have the method, `handle(msg)`, defined if `notifyOnMessage()` is called without the `callback` argument.

If `source` is `None` (default), `getUpdates()` is used to obtain updates from Telegram servers. If `source` is a synchronized queue (`Queue.Queue` in Python 2.7 or `queue.Queue` in Python 3), updates are obtained from the queue. In normal scenarios, a web application implementing a webhook dumps updates into the queue, while the bot pulls updates from it. 

Parameters:
- callback (function): a function to apply to every message received. If `None`, `self.handle` is assumed. 
- relax (float): seconds between each `getUpdates()`. Applies only when `source` is `None`.
- timeout (integer): timeout supplied to `getUpdates()`, controlling how long to poll. Applies only when `source` is `None`.
- source (Queue): source of updates
    - If `None`, use `getUpdates()` to obtain updates from Telegram servers.
    - If a `Queue` (`Queue.Queue` in Python 2.7 or `queue.Queue` in Python 3), updates are pulled from the queue.
    - Acceptable contents in queue:
        - `str`, `unicode` (Python 2.7), or `bytes` (Python 3, decoded using UTF-8) representing a JSON-serialized Update object.
        - `dict` representing an Update object.
- ordered (boolean): applied only when `source` is a `Queue`
    - If `True`, ensure in-order delivery of updates to `callback` (i.e. updates with a smaller `update_id` always come before those with a larger `update_id`). 
    - If `False`, no re-ordering is done. `callback` is applied to messages as soon as they are pulled from queue.
- maxhold (float): applied only when `source` is a `Queue` and `ordered` is `True`
    - the maximum number of seconds an update is held waiting for a not-yet-arrived smaller `update_id`. When this number of seconds is up, the update is delivered to `callback` even if some smaller `update_id`s have not yet arrived. If those smaller `update_id`s arrive at some later time, they are discarded.
- run_forever (boolean): append an infinite loop at the end and never returns. Useful as the very last line in a program.

Note: `source`, `ordered`, and `maxhold` are relevant *only if you use webhook*.

This can be a skeleton for a lot of telepot programs:

```python
import sys
import telepot

class YourBot(telepot.Bot):
    def handle(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
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
    content_type, chat_type, chat_id = telepot.glance(msg)
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

*Superclass:* [`telepot.Bot`](#telepot-Bot)  
*Subclass:* [`telepot.DelegatorBot`](#telepot-DelegatorBot)

Exposes a `Microphone` and lets you create `Listener`s who listen to that microphone. You don't have to deal with this class directly, if `DelegateBot` satisfies your needs.

**SpeakerBot(token)**

**mic**

A `Microphone` object. Used to broadcast messages to listeners obtained by `create_listener()`.

**create_listener()**

Returns a `Listener` object that listens to the `mic`.

<a id="telepot-DelegatorBot"></a>
### `telepot.DelegatorBot`

*Superclass:* [`telepot.SpeakerBot`](#telepot-SpeakerBot)

Can spawn delegates according to *delegation patterns* specified in the constructor.

**DelegatorBot(token, delegation_patterns)**

Parameters:

- **token**: the bot's token
- **delegation_patterns**: a list of *(seed_calculating_function, delegate_producing_function)* tuples

*seed_calculating_function* is a function that takes one argument - the message being processed - and returns a *seed*. The seed determines whether the following *delegate_producing_function* is called.

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

**Even if you use a webhook** and don't need `notifyOnMessage()`, you may always call `bot.handle(msg)` directly to take advantage of the above logic, if you find it useful.

The power of delegation is most easily exploited when used in combination with the `telepot.delegate` module (which contains a number of ready-made *seed_calculating_functions* and *delegate_producing_functions*) and the `ChatHandler` class (which provides a connection-like interface to deal with individual chats).

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

Thanks to **[Tornado](http://www.tornadoweb.org/)** for inspiration.

<a id="telepot-functions"></a>
### Functions in `telepot` module

**flavor(msg)**

Returns the flavor of a message:

- a normal message is `normal`
- an inline query is `inline_query`
- a chosen inline result is `chosen_inline_result`

If the bot can receive inline queries and/or chosen inline results, you should always check the flavor before further processing. See `glance()` below for an example.

**glance(msg, flavor='normal', long=False)**

*This function has an alias, `glance2()`, for backward compatibility. Developers are encouraged to use `glance()` from now on.*

Extracts "headline" information about a message.

When `flavor` is `normal`:
- returns a tuple of *(content_type, chat_type, msg['chat']['id'])*.
- if `long` is `True`, returns a tuple of *(content_type, chat_type, msg['chat']['id'], msg['date'], msg['message_id'])*.

*content_type* can be one of: `text`, `voice`, `sticker`, `photo`, `audio`, `document`, `video`, `contact`, `location`, `new_chat_participant`, `left_chat_participant`, `new_chat_title`, `new_chat_photo`, `delete_chat_photo`, `group_chat_created`, `supergroup_chat_created`, `migrate_to_chat_id`, `migrate_from_chat_id`, or `channel_chat_created`.

*chat_type* can be one of: `private`, `group`, `supergroup`, or `channel`.

When `flavor` is `inline_query`:
- returns a tuple of *(msg['id'], msg['from']['id'], msg['query'])*.
- if `long` is `True`, returns a tuple of *(msg['id'], msg['from']['id'], msg['query'], msg['offset'])*.

When `flavor` is `chosen_inline_result`:
- returns a tuple of *(msg['result_id'], msg['from']['id'], msg['query'])*
- parameter `long` has no effect in this case

Examples:

```python
import telepot

# Suppose `msg` is a message previously received.

flavor = telepot.flavor(msg)

if flavor == 'message':
    content_type, chat_type, chat_id = telepot.glance(msg)
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)

    # Do you stuff according to `content_type`

elif flavor == 'inline_query':
    query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
    query_id, from_id, query_string, offset = telepot.glance(msg, flavor='inline_query', long=True)

    # bot.answerInlineQuery(...)

elif flavor == 'chosen_inline_result':
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')

    # remember the chosen result, hopefully do better next time
```

**flance(msg, long=False)**

A combination of `flavor()` and `glance()`, it returns a tuple of two elements: *(flavor of message, tuple as returned by `glance()` of the same message)*. The `long` parameter is passed to `glance()`, controlling how much info is extracted.

<a id="telepot-namedtuple"></a>
## `telepot.namedtuple` module

**Telepot's custom is to represent Bot API objects as dictionaries.** On the other hand, we also have namedtuple classes mirroring all Bot API object types:

- [User](https://core.telegram.org/bots/api#user)
- [Chat](https://core.telegram.org/bots/api#chat)
- [Message](https://core.telegram.org/bots/api#message)
- [PhotoSize](https://core.telegram.org/bots/api#photosize)
- [Audio](https://core.telegram.org/bots/api#audio)
- [Document](https://core.telegram.org/bots/api#document)
- [Sticker](https://core.telegram.org/bots/api#sticker)
- [Video](https://core.telegram.org/bots/api#video)
- [Voice](https://core.telegram.org/bots/api#voice)
- [Contact](https://core.telegram.org/bots/api#contact)
- [Location](https://core.telegram.org/bots/api#location)
- [Update](https://core.telegram.org/bots/api#update)
- [UserProfilePhotos](https://core.telegram.org/bots/api#userprofilephotos)
- [File](https://core.telegram.org/bots/api#file)
- [ReplyKeyboardMarkup](https://core.telegram.org/bots/api#replykeyboardmarkup)
- [ReplyKeyboardHide](https://core.telegram.org/bots/api#replykeyboardhide)
- [ForceReply](https://core.telegram.org/bots/api#forcereply)
- [InlineQuery](https://core.telegram.org/bots/api#inlinequery)
- [InlineQueryResultArticle](https://core.telegram.org/bots/api#inlinequeryresultarticle)
- [InlineQueryResultPhoto](https://core.telegram.org/bots/api#inlinequeryresultphoto)
- [InlineQueryResultGif](https://core.telegram.org/bots/api#inlinequeryresultgif)
- [InlineQueryResultMpeg4Gif](https://core.telegram.org/bots/api#inlinequeryresultmpeg4gif)
- [InlineQueryResultVideo](https://core.telegram.org/bots/api#inlinequeryresultvideo)

The reasons for having namedtuple classes are twofold:

- Under some situations, you may want an object with a complete set of fields, including those whose values are `None`. A dictionary, as translated from Bot API's response, would have those `None` fields absent. By converting such a dictionary to a namedtuple, all fields are guaranteed to be present, even if their values are `None`.
- While you may construct `ReplyKeyboardMarkup`, `ReplyKeyboardHide`, `ForceReply`, and `InlineQueryResultZZZ` using dictionaries, it may be easier to use the namedtuple constructors.

*Beware of a peculiarity.* Namedtuple field names cannot be Python keywords, but the [Message](https://core.telegram.org/bots/api#message) object and a few others have a `from` field, which is a Python keyword. I choose to append an underscore to it. That is, the dictionary value `dict['from']` becomes `namedtuple.from_` when converted to a namedtuple.

<a id="telepot-namedtuple-convert"></a>
### Convert dictionary to namedtuple

Suppose you have received a message in the form a dictionary, here are two ways to obtain its namedtuple:

```python
from telepot.namedtuple import namedtuple, Message

# Unpack dict, give it to constructor
ntuple1 = Message(**msg)

# Use namedtuple() function, give it the class name
ntuple2 = namedtuple(msg, 'Message')

# ntuple1 == ntuple2

# `from` becomes `from_` due to keyword collision
print ntuple1.from_.id  # == msg['from']['id']

# other field names unchanged
print ntuple2.chat.id   # == msg['chat']['id']
```

You may also choose to convert only part of the message:

```python
from telepot.namedtuple import namedtuple, User, Chat

ntuple3 = User(**msg['from'])              # these two lines
ntuple4 = namedtuple(msg['from'], 'User')  # are equivalent

ntuple5 = Chat(**msg['chat'])              # these two lines
ntuple6 = namedtuple(msg['chat'], 'Chat')  # are equivalent
```

**namedtuple(dict, type)**

Convert a dictionary to a namedtuple of a given object type.

**type** can be one of the Bot API object types listed above.

<a id="telepot-namedtuple-construct"></a>
### Use namedtuple constructors

When creating reply markup (for `sendZZZ()`) or inline query results (for `answerInlineQuery()`), telepot's custom is to use dictionaries. An alternative is to use namedtuples.

Examples:

```python
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply

bot.sendMessage(chat_id, 'Show keyboard', reply_markup=ReplyKeyboardMarkup(keyboard=[['Yes', 'No']]))
bot.sendMessage(chat_id, 'Hide keyboard', reply_markup=ReplyKeyboardHide())
bot.sendMessage(chat_id, 'Force reply', reply_markup=ForceReply())
```
```python
from telepot.namedtuple import InlineQueryResultArticle

articles = [{'type': 'article',
                'id': 'abc', 'title': 'ABC', 'message_text': 'Good morning'},
            InlineQueryResultArticle(
                id='xyz', title='ZZZZZ', message_text='Good night')]

bot.answerInlineQuery(query_id, articles)
```
```python
from telepot.namedtuple import InlineQueryResultPhoto

photos = [{'type': 'photo',
              'id': '123', 'photo_url': '...', 'thumb_url': '...'},
          InlineQueryResultPhoto(
              id='999', photo_url='...', thumb_url='...')]

bot.answerInlineQuery(query_id, photos)
```

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

*Subclass:* [`telepot.async.helper.Listener`](#telepot-async-helper-Listener)

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

<a id="telepot-helper-Answerer"></a>
### `telepot.helper.Answerer`

On receiving an inline query, it spawns a thread to compute results and send them. If a preceding thread is already working for a user, it is cancelled. This ensures **at most one active thread** per user id.

**Answerer(bot, compute_function)**

Parameters:
- **bot** - the parent bot.
- **compute_function** - an answer-computing function.
    - It must take one argument, the *inline query*.
    - Its returned value is given to `bot.answerInlineQuery()` to send.
    - It may return one of the following:
        - a *list* of [InlineQueryResult](https://core.telegram.org/bots/api#inlinequeryresult)
        - a *tuple*, whose first element is a list of InlineQueryResult, followed by positional arguments to be supplied to `bot.answerInlineQuery()`
        - a *dict* representing keyword arguments to be supplied to `bot.answerInlineQuery()`
    - It must be **thread-safe**, because many threads may access it as the same time.

**answer(inline_query)**

Spawns a thread that calls the `compute_function` (specified in constructor), then applies the returned value to `bot.answerInlineQuery()`, in effect answering the inline query. If a preceding thread is already working for a user, that thread is cancelled, thus ensuring at most one active thread per user id.

<a id="telepot-helper-ListenerContext"></a>
### `telepot.helper.ListenerContext`

*Subclass:* [`telepot.helper.ChatContext`](#telepot-helper-ChatContext) [`telepot.helper.UserContext`](#telepot-helper-UserContext) [`telepot.helper.Monitor`](#telepot-helper-Monitor)

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

*Superclass:* [`telepot.helper.ListenerContext`](#telepot-helper-ListenerContext)  
*Subclass:* [`telepot.helper.ChatHandler`](#telepot-helper-ChatHandler)

**ChatContext(bot, context_id, chat_id)**

Parameters:
- **bot** - the parent bot. Should be a `SpeakerBot` or one of its subclasses.
- **context_id** - this ID's purpose and uniqueness to up to the user.
- **chat_id** - the target chat

This object exposes these properties:
- **chat_id**
- **sender** - a `Sender` object aimed at the target chat

<a id="telepot-helper-UserContext"></a>
### `telepot.helper.UserContext`

*Superclass:* [`telepot.helper.ListenerContext`](#telepot-helper-ListenerContext)  
*Subclass:* [`telepot.helper.UserHandler`](#telepot-helper-UserHandler)

**UserContext(bot, context_id, user_id)**

Parameters:
- **bot** - the parent bot. Should be a `SpeakerBot` or one of its subclasses.
- **context_id** - this ID's purpose and uniqueness to up to the user.
- **user_id** - the target user's id

This object exposes these properties:
- **user_id**
- **sender** - a `Sender` object aimed at the target user

<a id="telepot-helper-Monitor"></a>
### `telepot.helper.Monitor`

*Superclass:* [`telepot.helper.ListenerContext`](#telepot-helper-ListenerContext)

How to use this class:

1. Extend this class
2. Implement `on_message()`, optionally override `open()` and `on_close()`
3. Use `telepot.delegate.create_open()` to plug it into a `DelegatorBot`

**Monitor(seed_tuple, capture)**

Parameters:
- **seed_tuple** - a tuple of (bot, message, seed) generated by the delegation mechanism
- **capture** - a list of capture criteria for this object's `listener`. See `Listener` for syntax of how to compose criteria.

In the following example:
- a `MessagePrinter` (subclass of `Monitor`) is set up to capture all messages
- a bot is set up to spawn one and only one `MessagePrinter`

```python
import sys
import telepot
from telepot.delegate import create_open

class MessagePrinter(telepot.helper.Monitor):
    def __init__(self, seed_tuple):
        # Returns true for every message, meaning all are captured.
        capture_criteria = {'_': lambda msg: True}
        super(MessagePrinter, self).__init__(seed_tuple, [capture_criteria])

    def on_message(self, msg):
        print('Message received:')
        print(msg)

TOKEN = sys.argv[1]

bot = telepot.DelegatorBot(TOKEN, [
    # Seed is always the same, meaning only one MessagePrinter is ever spawned.
    (lambda msg: 1, create_open(MessagePrinter)),
])
bot.notifyOnMessage(run_forever=True)
```

**open(initial_msg, seed)**

Called when initially spawned.

**on_message(msg)**

Called when a message is captured by this object's `listener`. Subclass must implement.

**on_close(exception)**

Called just before this object is about to exit.

**close(code=None, reason=None)**

Raises a `StopListening` exception, causing this object to exit.

<a id="telepot-helper-ChatHandler"></a>
### `telepot.helper.ChatHandler`

*Superclass:* [`telepot.helper.ChatContext`](#telepot-helper-ChatContext)

How to use this class:

1. Extend this class
2. Implement `on_message()`, optionally override `open()` and `on_close()`
3. Use `telepot.delegate.create_open()` to plug it into a `DelegatorBot`

**ChatHandler(seed_tuple, timeout)**

Parameters:
- **seed_tuple** - a tuple of (bot, message, seed) generated by the delegation mechanism
- **timeout** - timeout for this object's `listener`

This object's `listener` is automatically set up to capture messages from the same chat id as the initial message, contained in the *seed_tuple* parameter.

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

**open(initial_msg, seed)**

Called when initially spawned.

**on_message(msg)**

Called when a message is captured by this object's `listener`. Subclass must implement.

**on_close(exception)**

Called just before this object is about to exit.

**close(code=None, reason=None)**

Raises a `StopListening` exception, causing this object to exit.

<a id="telepot-helper-UserHandler"></a>
### `telepot.helper.UserHandler`

*Superclass:* [`telepot.helper.UserContext`](#telepot-helper-UserContext)

How to use this class:

1. Extend this class
2. Implement `on_message()`, optionally override `open()` and `on_close()`
3. Use `telepot.delegate.create_open()` to plug it into a `DelegatorBot`

**UserHandler(seed_tuple, timeout, flavors='all')**

Parameters:
- **seed_tuple** - a tuple of (bot, message, seed) generated by the delegation mechanism
- **timeout** - timeout for this object's `listener`
- **flavors** - which flavors of messages to listen for. May be `all` (default), or a list of flavors.

This object's `listener` is automatically set up to capture messages of the specified `flavors` and from the same user as the initial message's, contained in the *seed_tuple* parameter.

**open(initial_msg, seed)**

Called when initially spawned.

**on_message(msg)**

Called when a message is captured by this object's `listener`. Subclass must implement.

**on_close(exception)**

Called just before this object is about to exit.

**close(code=None, reason=None)**

Raises a `StopListening` exception, causing this object to exit.

<a id="telepot-helper-openable"></a>
### `telepot.helper.openable` class decorator

This class decorator supplies methods required by [`create_open()`](#telepot-delegate-create-open), if they are not defined by the class. It simplifies efforts to create a class to be used with `create_open()`.

The following methods (and their contents) are supplied, if they are not defined by the class already:

- method **open(initial_msg, seed)** - empty
- method **on_message(msg)** - raise a `NotImplementedError`
- method **on_close(exception)** - log the exception (default: print to `stderr`), better for development because the exception would not be swallowed silently.
- method **close(code=None, reason=None)** - raise a `StopListening` exception, causing exit.
- property **listener** - raise a `NotImplementedError`

In other words, a class decorated by `@openable` still has to implement the method `on_message(msg)` and the property `listener`.

The best demonstration of using `@openable` is actually the `Monitor` and `ChatHandler` class themselves. They inherit a `listener` property from their superclasses; the use of `@openable` fills in other methods, but leaves the `listener` property untouched. Defining the class is only a matter of giving it a constructor.

```python
@openable
class Monitor(ListenerContext):
    def __init__(...):
        ...

@openable
class ChatHandler(ChatContext):
    def __init__(...):
        ...
```

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

<a id="telepot-delegate-per-from-id"></a>
**per_from_id()**

Returns a seed-calculating-function that returns `from` field's user id as the seed, equivalent to:
```python
lambda msg: msg['from']['id']
```

<a id="telepot-delegate-per-from-id-in"></a>
**per_from_id_in(set)**

Returns a seed-calculating-function that returns `from` field's user id as the seed, if that user id is in the `set`, equivalent to:
```python
lambda msg: msg['from']['id'] if msg['from']['id'] in set else None
```

<a id="telepot-delegate-per-from-id-except"></a>
**per_from_id_except(set)**

Returns a seed-calculating-function that returns `from` field's user id as the seed, if that user id is *not* in the `set`, equivalent to:
```python
lambda msg: msg['from']['id'] if msg['from']['id'] not in set else None
```

<a id="telepot-delegate-per-inline-from-id"></a>
**per_inline_from_id()**

Returns a seed-calculating-function that returns `from` field's user id as the seed, only for inline queries and chosen inline results.

<a id="telepot-delegate-per-inline-from-id-in"></a>
**per_inline_from_id_in(set)**

Returns a seed-calculating-function that returns `from` field's user id as the seed, if that user id is in the `set`, only for inline queries and chosen inline results.

<a id="telepot-delegate-per-inline-from-id-except"></a>
**per_inline_from_id_except(set)**

Returns a seed-calculating-function that returns `from` field's user id as the seed, if that user id is *not* in the `set`, only for inline queries and chosen inline results.

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

Returns a delegate-producing-function that creates an object of `cls`, then engages it in the following manner:
- call its `open(initial_msg, seed)` method
- in an infinite loop:
  - call its `listener.wait()`, blocking until the next message captured
  - call its `on_message(msg)` method
- if any exception is raised, call its `close(exception)` method, then exit

The object of `cls` must have these defined:
- a constructor that takes a *seed_tuple* as the first argument, followed by those explicitly supplied in the `create_open()` call
- method `open(initial_msg, seed)`
- method `on_message(msg)`
- method `on_close(exception)`
- property `listener` which returns a `Listener` object

An easy way to fulfilled these requirements is to extend from [`Monitor`](#telepot-helper-Monitor) or [`ChatHandler`](#telepot-helper-ChatHandler), or decorating a class with the [`@openable`](#telepot-helper-openable) class decorator.

Here is the source for reference:

```python
def create_open(cls, *args, **kwargs):
    def f(seed_tuple):
        j = cls(seed_tuple, *args, **kwargs)

        def wait_loop():
            bot, msg, seed = seed_tuple
            try:
                handled = j.open(msg, seed)
                if not handled:
                    j.on_message(msg)

                while 1:
                    msg = j.listener.wait()
                    j.on_message(msg)

            except Exception as e:
                j.on_close(e)

        return wait_loop
    return f
```

<a id="telepot-async"></a>
## `telepot.async` module (Python 3.4.3 or newer)

This package mirrors the traditional version of telepot to make use of the `asyncio` module of Python 3.4. Nearly all methods share identical signatures with their traditional siblings, except that blocking methods now become **coroutines** and are often called with `yield from`.

If you find this part of documentations wanting, always refer back to the traditional counterparts. It is easy to adapt examples from there to here - just remember to `yield from` coroutines.

<a id="telepot-async-Bot"></a>
### `telepot.async.Bot`

*Subclass:* [`telepot.async.SpeakerBot`](#telepot-async-SpeakerBot)

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

*coroutine* **answerInlineQuery(self, inline_query_id, results, cache_time=None, is_personal=None, next_offset=None)**

*To be filled in ...*

*coroutine* **messageLoop(handler=None, source=None, ordered=True, maxhold=3)**

Functionally equivalent to `notifyOnMessage()`, this method constantly checks for updates and applies `handler` to each message received. `handler` must take one argument, which is the message.

If `handler` is `None`, `self.handle` is assumed to be the handler function. In other words, a bot must have the method, `handle(msg)`, defined if `messageLoop()` is called without the `handler` argument.

If `source` is `None` (default), `getUpdates()` is used to obtain updates from Telegram servers. If `source` is an `asyncio.Queue`, updates are obtained from the queue. In normal scenarios, a web application implementing a webhook dumps updates into the queue, while the bot pulls updates from it. 

Parameters:
- handler: a function or coroutine to apply to every message received. If `None`, `self.handle` is assumed.
    - If a regular function, it is called directly.
    - If a coroutine, it is allocated a task using `BaseEventLoop.create_task()`.
- source (Queue): source of updates
    - If `None`, use `getUpdates()` to obtain updates from Telegram servers.
    - If an `asyncio.Queue`, updates are pulled from the queue.
    - Acceptable contents in queue:
        - `str` or `bytes` (decoded using UTF-8) representing a JSON-serialized Update object.
        - `dict` representing an Update object.
- ordered (boolean): applied only when `source` is a queue
    - If `True`, ensure in-order delivery of updates to `handler` (i.e. updates with a smaller `update_id` always come before those with a larger `update_id`). 
    - If `False`, no re-ordering is done. `handler` is applied to messages as soon as they are pulled from queue.
- maxhold (float): applied only when `source` is a queue and `ordered` is `True`
    - the maximum number of seconds an update is held waiting for a not-yet-arrived smaller `update_id`. When this number of seconds is up, the update is delivered to `handler` even if some smaller `update_id`s have not yet arrived. If those smaller `update_id`s arrive at some later time, they are discarded.

Note: `source`, `ordered`, and `maxhold` are relevant *only if you use webhook*.

This can be a skeleton for a lot of telepot programs:

```python
import sys
import asyncio
import telepot
import telepot.async

class YourBot(telepot.async.Bot):
    @asyncio.coroutine
    def handle(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
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
    content_type, chat_type, chat_id = telepot.glance(msg)
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

*Superclass:* [`telepot.async.Bot`](#telepot-async-Bot)  
*Subclass:* [`telepot.async.DelegatorBot`](#telepot-async-DelegatorBot)

Exposes a `Microphone` and lets you create `Listener`s who listen to that microphone. You don't have to deal with this class directly, if `DelegateBot` and `ChatHandler` satisfy your needs.

**SpeakerBot(token, loop=None)**

**mic**

A `Microphone` object. Used to broadcast messages to listeners obtained by `create_listener()`.

**create_listener()**

Returns a `Listener` object that listens to the `mic`.

<a id="telepot-async-DelegatorBot"></a>
### `telepot.async.DelegatorBot`

*Superclass:* [`telepot.async.SpeakerBot`](#telepot-async-SpeakerBot)

Can create tasks according to *delegation patterns* specified in the constructor.

Unlike its traditional counterpart, this class uses **coroutine** and **task** to achieve delegation. To understand the remaining discussions, you have to understand asyncio's [tasks and coroutines](https://docs.python.org/3/library/asyncio-task.html), especially the difference between a coroutine *function* and a coroutine *object*.

**DelegatorBot(token, delegation_patterns, loop=None)**

Parameters:

- **token**: the bot's token
- **delegation_patterns**: a list of *(seed_calculating_function, coroutine_producing_function)* tuples
- **loop**: the event loop

*seed_calculating_function* is a function that takes one argument - the message being processed - and returns a *seed*. The seed determines whether the following *coroutine_producing_function* is called.

- If the seed is a *hashable* (e.g. number, string, tuple), the bot looks for a task associated with the seed.
  - If such a task exists and is not done, it is assumed that the message will be picked up by the task. The bot does nothing.
  - If no task exists or that task is done, the bot calls *coroutine_producing_function*, use the returned coroutine object to create a task, and associates the new task with the seed.

- If the seed is a *non-hashable* (e.g. list), the bot always calls *coroutine_producing_function*, and use the returned coroutine object to create a task. No seed-task association occurs.

- If the seed is `None`, nothing is done.

**In essence, only one task is running for a given seed, if that seed is a hashable.**

*coroutine_producing_function* is a function that takes one argument - a tuple of *(bot, message, seed)* - and returns a coroutine *object*, which will be used to create a task.

All *seed_calculating_functions* are evaluated in order. One message may cause multiple tasks to be created.

This class implements the above logic in its `handle` method. Once you supply a list of *(seed_calculating_function, coroutine_producing_function)* pairs to the constructor and invoke `messageLoop()`, the above logic will be executed for every message received.

**Even if you use a webhook** and don't need `messageLoop()`, you may always call `bot.handle(msg)` directly to take advantage of the above logic, if you find it useful.

The power of delegation is most easily exploited when used in combination with the `telepot.delegate` module (which contains a number of ready-made *seed_calculating_functions*), the `telepot.async.delegate` module (which contains a number of ready-made *coroutine_producing_functions*), and the `ChatHandler` class (which provides a connection-like interface to deal with individual chats).

Here is a bot that counts how many messages it has received in a chat. If no message is received after 10 seconds, it starts over. The counting is done *per chat* - that's the important point.

```python
import sys
import asyncio
import telepot
from telepot.delegate import per_chat_id
from telepot.async.delegate import create_open

class MessageCounter(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(MessageCounter, self).__init__(seed_tuple, timeout)
        self._count = 0

    @asyncio.coroutine
    def on_message(self, msg):
        self._count += 1
        yield from self.sender.sendMessage(self._count)

TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.async.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(MessageCounter, timeout=10)),
])

loop = asyncio.get_event_loop()
loop.create_task(bot.messageLoop())
print('Listening ...')

loop.run_forever()
```

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

*Superclass:* [`telepot.helper.Listener`](#telepot-helper-Listener)

Used to suspend execution until a certain message appears. Users can specify how to "match" for messages in the `capture()` method. See `telepot.helper.Listener` for details.

Normally, you should not need to create this object, but obtain it using `SpeakerBot.create_listener()` or access it with `ChatHandler.listener`.

The only difference with traditional `telepot.helper.Listener` is that it uses `asyncio.Queue` instead of the concurrent `Queue`, and the `wait` method becomes a coroutine.

**Listener(microphone, queue)**

*coroutine* **wait()**

<a id="telepot-async-helper-Answerer"></a>
### `telepot.async.helper.Answerer`

On receiving an inline query, it creates a new task to compute results and send them. If a preceding task is already working for a user, it is cancelled. This ensures **at most one active task** per user id.

**Answerer(bot, compute_function, loop=None)**

Parameters:
- **bot** - the parent bot.
- **compute_function** - an answer-computing function.
    - It may be a regular function or a coroutine.
    - It must take one argument, the *inline query*.
    - Its returned value is given to `bot.answerInlineQuery()` to send.
    - It may return one of the following:
        - a *list* of [InlineQueryResult](https://core.telegram.org/bots/api#inlinequeryresult)
        - a *tuple*, whose first element is a list of InlineQueryResult, followed by positional arguments to be supplied to `bot.answerInlineQuery()`
        - a *dict* representing keyword arguments to be supplied to `bot.answerInlineQuery()`
- **loop** - the event loop. If `None`, use `asyncio`'s default event loop.

**answer(inline_query)**

Creates a task that calls the `compute_function` (specified in constructor), then applies the returned value to `bot.answerInlineQuery()`, in effect answering the inline query. If a preceding task is already working for a user, that task is cancelled, thus ensuring at most one active task per user id.

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

<a id="telepot-async-delegate-create-open"></a>
**create_open(cls, \*args, \*\*kwargs)**

Returns a coroutine-producing-function that creates an object of `cls`, then engages it in the following manner:
- call its `open(initial_msg, seed)` method
- in an infinite loop:
  - call its `listener.wait()`, suspended until the next message captured
  - call its `on_message(msg)` method
- if any exception is raised, call its `close(exception)` method, then exit

The object of `cls` must have these defined:
- a constructor that takes a *seed_tuple* as the first argument, followed by those explicitly supplied in the `create_open()` call
- method (regular or coroutine) `open(initial_msg, seed)`
- method (regular or coroutine) `on_message(msg)`
- method (regular or coroutine) `on_close(exception)`
- property `listener` which returns a `Listener` object

An easy way to fulfilled these requirements is to extend from [`Monitor`](#telepot-helper-Monitor) or [`ChatHandler`](#telepot-helper-ChatHandler), or decorating a class with the [`@openable`](#telepot-helper-openable) class decorator.
