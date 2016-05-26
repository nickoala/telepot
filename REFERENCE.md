# telepot 8.0 reference

I am in the process of updating documentations. **Those on this page are not 100% up-to-date.** Long-time users should be able to discern the additions by looking at **[changelog](https://github.com/nickoala/telepot/blob/master/CHANGELOG.md)**. **For newcomers, all stuff on this page still applies**, although discussions on new features are lacking. Expect complete documentations in coming days.

----------------------------

**[telepot](#telepot)**
- [Bot](#telepot-Bot)
- [SpeakerBot](#telepot-SpeakerBot)
- [DelegatorBot](#telepot-DelegatorBot)
- [Functions](#telepot-functions)

**[telepot.namedtuple](#telepot-namedtuple)**
- [Convert dictionary to namedtuple](#telepot-namedtuple-convert)
- [Create namedtuples from scratch](#telepot-namedtuple-construct)

**[telepot.helper](#telepot-helper)**
- [Microphone](#telepot-helper-Microphone)
- [Listener](#telepot-helper-Listener)
- [Sender](#telepot-helper-Sender)
- [Administrator](#telepot-helper-Administrator)
- [Editor](#telepot-helper-Editor)
- [Answerer](#telepot-helper-Answerer)
- [Router](#telepot-helper-Router)
- [DefaultRouterMixin](#telepot-helper-DefaultRouterMixin)
- [ListenerContext](#telepot-helper-ListenerContext)
- [ChatContext](#telepot-helper-ChatContext)
- [UserContext](#telepot-helper-UserContext)
- [Monitor](#telepot-helper-Monitor)
- [ChatHandler](#telepot-helper-ChatHandler)
- [UserHandler](#telepot-helper-UserHandler)
- [InlineUserHandler](#telepot-helper-InlineUserHandler)
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
- [per_application](#telepot-delegate-per-application)
- [per_message](#telepot-delegate-per-message)
- [call](#telepot-delegate-call)
- [create_run](#telepot-delegate-create-run)
- [create_open](#telepot-delegate-create-open)

**[telepot.routing](#telepot-routing)**
- [by_content_type](#telepot-routing-by-content-type)
- [by_command](#telepot-routing-by-command)
- [by_chat_command](#telepot-routing-by-chat-command)
- [by_text](#telepot-routing-by-text)
- [by_data](#telepot-routing-by-data)
- [by_regex](#telepot-routing-by-regex)
- [process_key](#telepot-routing-process-key)
- [lower_key](#telepot-routing-lower-key)
- [upper_key](#telepot-routing-upper-key)
- [make_routing_table](#telepot-routing-make-routing-table)
- [make_content_type_routing_table](#telepot-routing-make-content-type-routing-table)

**[telepot.exception](#telepot-exception)**
- [TelepotException](#telepot-exception-TelepotException)
- [BadHTTPResponse](#telepot-exception-BadHTTPResponse)
- [TelegramError](#telepot-exception-TelegramError)

**[telepot.async](#telepot-async)** (Python 3.5+)
- [Bot](#telepot-async-Bot)
- [SpeakerBot](#telepot-async-SpeakerBot)
- [DelegatorBot](#telepot-async-DelegatorBot)
- [Functions](#telepot-async-functions)

**[telepot.async.helper](#telepot-async-helper)** (Python 3.5+)
- [Microphone](#telepot-async-helper-Microphone)
- [Listener](#telepot-async-helper-Listener)
- [Answerer](#telepot-async-helper-Answerer)
- [Router](#telepot-async-helper-Router)
- [DefaultRouterMixin](#telepot-async-helper-DefaultRouterMixin)
- [Monitor](#telepot-async-helper-Monitor)
- [ChatHandler](#telepot-async-helper-ChatHandler)
- [UserHandler](#telepot-async-helper-UserHandler)
- [InlineUserHandler](#telepot-async-helper-InlineUserHandler)
- [@openable](#telepot-async-helper-openable)

**[telepot.async.delegate](#telepot-async-delegate)** (Python 3.5+)
- [per_chat_id](#telepot-async-delegate-per-chat-id)
- [per_chat_id_in](#telepot-async-delegate-per-chat-id-in)
- [per_chat_id_except](#telepot-async-delegate-per-chat-id-except)
- [per_from_id](#telepot-async-delegate-per-from-id)
- [per_from_id_in](#telepot-async-delegate-per-from-id-in)
- [per_from_id_except](#telepot-async-delegate-per-from-id-except)
- [per_inline_from_id](#telepot-async-delegate-per-inline-from-id)
- [per_inline_from_id_in](#telepot-async-delegate-per-inline-from-id-in)
- [per_inline_from_id_except](#telepot-async-delegate-per-inline-from-id-except)
- [per_application](#telepot-async-delegate-per-application)
- [per_message](#telepot-async-delegate-per-message)
- [call](#telepot-async-delegate-call)
- [create_run](#telepot-async-delegate-create-run)
- [create_open](#telepot-async-delegate-create-open)

**[telepot.async.routing](#telepot-async-routing)** (Python 3.5+)

<a id="telepot"></a>
## `telepot` module

<a id="telepot-Bot"></a>
### `telepot.Bot`

*Subclass:* [`telepot.SpeakerBot`](#telepot-SpeakerBot)

This class is mostly a wrapper around Telegram Bot API methods, and is the most ancient part of telepot.

Most methods are straight mappings from **[Telegram Bot API](https://core.telegram.org/bots/api)**. No point to duplicate all the details here. I only give brief descriptions below, and encourage you to visit the underlying API's documentations. Full power of the Bot API can be exploited only by understanding the API itself.

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

**sendMessage(chat_id, text, parse_mode=None, disable_web_page_preview=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

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

**forwardMessage(chat_id, from_chat_id, message_id, disable_notification=None)**

Forward messages of any kind.

See: https://core.telegram.org/bots/api#forwardmessage

**sendPhoto(chat_id, photo, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

Send photos.

**photo**: May be one of the following:
- a *string*, indicating a `file_id` on the server
- a *file* object, as obtained by `open()`
- a tuple of *(filename, file-like object)*
    - filename: Telegram servers require to know the extension. So, the *name* doesn't really matter, as long as the extension is correct.
    - file-like object: as obtained by `urllib2.urlopen()` (Python 2.7) or `urllib.request.urlopen()` (Python 3)

**This works the same way with other `sendZZZ()` methods.**

See: https://core.telegram.org/bots/api#sendphoto

Examples:
```python
# Uploading a file may take a while. Let user know you are doing something.
bot.sendChatAction(chat_id, 'upload_photo')

# Send a file that is stored locally.
result = bot.sendPhoto(chat_id, open('lighthouse.jpg', 'rb'))

# Send a file from the web. You have to supply a filename with a correct extension.
f = urllib2.urlopen('http://i.imgur.com/B1fzGoh.jpg')
result = bot.sendPhoto(chat_id, ('abc.jpg', f))

# Get `file_id` from the Message object returned.
file_id = result['photo'][0]['file_id']

# Use `file_id` to resend the same photo, with a caption this time.
bot.sendPhoto(chat_id, file_id, caption='This is a lighthouse')
```

**sendAudio(chat_id, audio, duration=None, performer=None, title=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

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

**sendDocument(chat_id, document, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

Send general files.

See: https://core.telegram.org/bots/api#senddocument

Examples:
```python
bot.sendChatAction(chat_id, 'upload_document')
result = bot.sendDocument(chat_id, open('document.txt', 'rb'))

file_id = result['document']['file_id']
bot.sendDocument(chat_id, file_id)
```

**sendSticker(chat_id, sticker, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

Send .webp stickers.

See: https://core.telegram.org/bots/api#sendsticker

Examples:
```python
# I found .png files are also accepted. Other formats? You have to try it yourself.
result = bot.sendSticker(chat_id, open('gandhi.png', 'rb'))

file_id = result['sticker']['file_id']
bot.sendSticker(chat_id, file_id)
```

**sendVideo(chat_id, video, duration=None, width=None, height=None, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

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

**sendVoice(chat_id, audio, duration=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

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

**sendLocation(chat_id, latitude, longitude, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

Send point on the map.

See: https://core.telegram.org/bots/api#sendlocation

Examples:
```python
bot.sendChatAction(chat_id, 'find_location')
bot.sendLocation(chat_id, 22.33, 114.18)   # Hong Kong
bot.sendLocation(chat_id, 49.25, -123.1)   # Vancouver
bot.sendLocation(chat_id, -37.82, 144.97)  # Melbourne
```

**sendVenue(chat_id, latitude, longitude, title, address, foursquare_id=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

See: https://core.telegram.org/bots/api#sendvenue

**sendContact(chat_id, phone_number, first_name, last_name=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

See: https://core.telegram.org/bots/api#sendcontact

**sendChatAction(chat_id, action)**

Tell the user that something is happening on the bot's side. The status is set for 5 seconds or less (when a message arrives from your bot, Telegram clients clear its typing status).

See: https://core.telegram.org/bots/api#sendchataction

Examples: Please refer to examples for `sendPhoto()`, `sendVideo()`, `sendDocument()`, etc.

**getUserProfilePhotos(user_id, offset=None, limit=None)**

Get a list of profile pictures for a user.

See: https://core.telegram.org/bots/api#getuserprofilephotos

**getFile(file_id)**

Get a [File](https://core.telegram.org/bots/api#file) object, usually as a prelude to downloading a file. If you just want to download a file, call `download_file()` instead.

See: https://core.telegram.org/bots/api#getfile

**kickChatMember(chat_id, user_id)**

See: https://core.telegram.org/bots/api#kickchatmember

**unbanChatMember(chat_id, user_id)**

See: https://core.telegram.org/bots/api#unbanchatmember

**answerCallbackQuery(callback_query_id, text=None, show_alert=None)**

See: https://core.telegram.org/bots/api#answercallbackquery

**editMessageText(msg_identifier, text, parse_mode=None, disable_web_page_preview=None, reply_markup=None)**

**msg_identifier** can be:
- a tuple of *(chat_id, message_id)*
- a tuple of *(inline_message_id)*
- a single value - *inline_message_id*

See: https://core.telegram.org/bots/api#editmessagetext

**editMessageCaption(msg_identifier, caption=None, reply_markup=None)**

**msg_identifier** can be:
- a tuple of *(chat_id, message_id)*
- a tuple of *(inline_message_id)*
- a single value - *inline_message_id*

See: https://core.telegram.org/bots/api#editmessagecaption

**editMessageReplyMarkup(msg_identifier, reply_markup=None)**

**msg_identifier** can be:
- a tuple of *(chat_id, message_id)*
- a tuple of *(inline_message_id)*
- a single value - *inline_message_id*

See: https://core.telegram.org/bots/api#editmessagereplymarkup

**answerInlineQuery(inline_query_id, results, cache_time=None, is_personal=None, next_offset=None)**

Send answers to an inline query. `results` is a list of [InlineQueryResult](https://core.telegram.org/bots/api#inlinequeryresult).

See: https://core.telegram.org/bots/api#answerinlinequery

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

**download_file(file_id, dest)**

Download a file. `dest` can be a path (string) or a Python file object.

Examples:
```python
bot.download_file('ABcdEfGhijkLm_NopQRstuvxyZabcdEFgHIJ', 'save/to/path')

# If you open the file yourself, you are responsible for closing it.
with open('save/to/path', 'wb') as f:
    bot.download_file('ABcdEfGhijkLm_NopQRstuvxyZabcdEFgHIJ', f)
```

**message_loop(callback=None, relax=0.1, timeout=20, source=None, ordered=True, maxhold=3, run_forever=False)**

Spawn a thread to constantly check for updates. Apply `callback` to every message received. `callback` may be:

- a *function* that takes one argument, the message.
- a *dict* in the form: `{'chat': f1, 'callback_query': f2, 'inline_query': f3, 'chosen_inline_result': f4}`, where `f1`, `f2`, `f3`, `f4` are functions that take one argument, the message. Which function gets called is determined by the flavor of a message. You don't have to include all flavors in the dict, only the ones you need.
- `None` (default), in which case you have to define some instance methods for the bot to be used as callbacks. You have two options:
    - implement the bot's `handle(msg)` method.
    - implement one or more of `on_chat_message(msg)`, `on_inline_query(msg)`, and `on_chosen_inline_result(msg)`. Which gets called is determined by the flavor of a message.

If `source` is `None` (default), `getUpdates()` is used to obtain updates from Telegram servers. If `source` is a synchronized queue (`Queue.Queue` in Python 2.7 or `queue.Queue` in Python 3), updates are obtained from the queue. In normal scenarios, a web application implementing a webhook dumps updates into the queue, while the bot pulls updates from it. 

Parameters:
- callback (function): a function, a dict, or `None`, as described above.
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

Note:
- `relax` and `timeout` are relevant *only if you use `getUpdates()`*
- `source`, `ordered`, and `maxhold` are relevant *only if you use webhook*

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

This class implements the above logic in its `handle` method. Once you supply a list of *(seed_calculating_function, delegate_producing_function)* pairs to the constructor and invoke `message_loop()`, the above logic will be executed for every message received.

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
bot.message_loop(run_forever=True)
```

Thanks to **[Tornado](http://www.tornadoweb.org/)** for inspiration.

<a id="telepot-functions"></a>
### Functions in `telepot` module

**flavor(msg)**

Returns the flavor of a message, one of `chat`, `callback_query`, `inline_query`, `chosen_inline_result`.

**glance(msg, flavor='chat', long=False)**

Extracts "headline" information about a message.

When `flavor` is `chat`:
- returns a tuple of *(content_type, chat_type, msg['chat']['id'])*.
- if `long` is `True`, returns a tuple of *(content_type, chat_type, msg['chat']['id'], msg['date'], msg['message_id'])*.

*content_type* can be one of: `text`, `audio`, `document`, `photo`, `sticker`, `video`, `voice`, `contact`, `location`, `venue`, `new_chat_member`, `left_chat_member`, `new_chat_title`, `new_chat_photo`, `delete_chat_photo`, `group_chat_created`, `supergroup_chat_created`, `channel_chat_created`, `migrate_to_chat_id`, `migrate_from_chat_id`, `pinned_message`.

*chat_type* can be one of: `private`, `group`, `supergroup`, or `channel`.

When `flavor` is `callback_query`:
- returns a tuple of *(msg['id'], msg['from']['id'], msg['data'])*.
- parameter `long` has no effect in this case

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

if flavor == 'chat':
    content_type, chat_type, chat_id = telepot.glance(msg)
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)

    # Do you stuff according to `content_type`

elif flavor == 'callback_query':
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print ('Callback query:', query_id, from_id, query_data)

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

**flavor_router(routing_table)**

Returns a *function* that takes one argument (a message), and depending on the flavor, routes that message to another function according to the *routing_table*.

The *routing_table* is a dict of the form: `{'chat': f1, 'callback_query': f2, 'inline_query': f3, 'chosen_inline_result': f4}`, where `f1`, `f2`, `f3`, `f4` are functions that take one argument (the message). You don't have to include all flavors in the dict, only the ones you need.

**message_identifier(msg)**

If `msg` is a `chat` message, returns a tuple `(msg['chat']['id'], msg['message_id'])`.

if `msg` is a `choson_inline_result`, returns `msg['inline_message_id']`.

The returned value can be used in methods `editMessage*()` and `Editor`'s constructor to facilitate message editing.

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
- While you may construct `ReplyKeyboardMarkup`, `ReplyKeyboardHide`, `ForceReply`, and `InlineQueryResult*` using dictionaries, it may be easier to use the namedtuple constructors.

*Beware of a peculiarity.* Namedtuple field names cannot be Python keywords, but the [Message](https://core.telegram.org/bots/api#message) object and a few others have a `from` field, which is a Python keyword. I choose to append an underscore to it. That is, the dictionary value `dict['from']` becomes `namedtuple.from_` when converted to a namedtuple.

<a id="telepot-namedtuple-convert"></a>
### Convert dictionary to namedtuple

Suppose you have received a message in the form a dictionary, here is how to obtain its namedtuple:

```python
from telepot.namedtuple import Message

# Unpack dict into keyword arguments
ntuple = Message(**msg)

# `from` becomes `from_` due to keyword collision
print (ntuple.from_.id)  # == msg['from']['id']

# other field names unchanged
print (ntuple.chat.id)   # == msg['chat']['id']
```

You may also choose to convert only part of the message:

```python
from telepot.namedtuple import User, Chat

user = User(**msg['from'])
chat = Chat(**msg['chat'])
```

<a id="telepot-namedtuple-construct"></a>
### Create namedtuples from scratch

To create custom keyboards, inline keyboards, or inline query results, you may use the appropriate namedtuples or just a dict with the appropriate structures.

Examples:

```python
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

markup = ReplyKeyboardMarkup(keyboard=[
             ['Plain text', KeyboardButton(text='Text only')],
             [dict(text='Phone', request_contact=True), KeyboardButton(text='Location', request_location=True)],
         ])
bot.sendMessage(chat_id, 'Custom keyboard with various buttons', reply_markup=markup)
```
```python
from telepot.namedtuple import ReplyKeyboardHide

markup = ReplyKeyboardHide()
bot.sendMessage(chat_id, 'Hide custom keyboard', reply_markup=markup)
```
```python
from telepot.namedtuple import ForceReply

markup = ForceReply()
bot.sendMessage(chat_id, 'Force reply', reply_markup=markup)
```
```python
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

markup = InlineKeyboardMarkup(inline_keyboard=[
             [dict(text='Telegram URL', url='https://core.telegram.org/')],
             [InlineKeyboardButton(text='Callback - show notification', callback_data='notification')],
             [dict(text='Callback - show alert', callback_data='alert')],
             [InlineKeyboardButton(text='Callback - edit message', callback_data='edit')],
             [dict(text='Switch to using bot inline', switch_inline_query='initial query')],
         ])
bot.sendMessage(chat_id, 'Inline keyboard with various buttons', reply_markup=markup)
```
```python
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent

articles = [InlineQueryResultArticle(
                 id='abcde', title='Telegram', 
                 input_message_content=InputTextMessageContent(message_text='Telegram is a messaging app')),
            dict(type='article',
                 id='fghij', title='Google', 
                 input_message_content=dict(message_text='Google is a search engine'))]

bot.answerInlineQuery(query_id, articles)
```
```python
from telepot.namedtuple import InlineQueryResultPhoto

photo1_url = 'https://core.telegram.org/file/811140934/1/tbDSLHSaijc/fdcc7b6d5fb3354adf'
photo2_url = 'https://www.telegram.org/img/t_logo.png'
photos = [InlineQueryResultPhoto(
              id='12345', photo_url=photo1_url, thumb_url=photo1_url),
          dict(type='photo',
              id='67890', photo_url=photo2_url, thumb_url=photo2_url)]

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

**sendMessage(text, parse_mode=None, disable_web_page_preview=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

**forwardMessage(from_chat_id, message_id, disable_notification=None)**

**sendPhoto(photo, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

**sendAudio(audio, duration=None, performer=None, title=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

**sendDocument(document, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

**sendSticker(sticker, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

**sendVideo(video, duration=None, width=None, height=None, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

**sendVoice(audio, duration=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

**sendLocation(latitude, longitude, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

**sendVenue(latitude, longitude, title, address, foursquare_id=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

**sendContact(phone_number, first_name, last_name=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

**sendChatAction(action)**

<a id="telepot-helper-Administrator"></a>
### `telepot.helper.Administrator`

**kickChatMember(user_id)**

**unbanChatMember(user_id)**

<a id="telepot-helper-Editor"></a>
### `telepot.helper.Editor`

**editMessageText(text, parse_mode=None, disable_web_page_preview=None, reply_markup=None)**

**editMessageCaption(caption=None, reply_markup=None)**

**editMessageReplyMarkup(reply_markup=None)**

<a id="telepot-helper-Answerer"></a>
### `telepot.helper.Answerer`

On receiving an inline query, it spawns a thread to compute results and send them. If a preceding thread is already working for a user, it is cancelled. This ensures **at most one active thread** per user id.

**Answerer(bot)**

**answer(inline_query, compute_fn, \*compute_args, \*\*compute_kwargs)**

Spawns a thread that calls the *compute function* (along with additional arguments), then applies the returned value to `bot.answerInlineQuery()`, in effect answering the inline query. If a preceding thread is already working for a user, that thread is cancelled, thus ensuring at most one active thread per user id.

Parameters:
- **inline_query** - from which the `from` `id` and query `id` will be inferred
- **compute_fn** - an answer-computing function.
    - Its returned value is given to `bot.answerInlineQuery()` to send.
    - It may return one of the following:
        - a *list* of [InlineQueryResult](https://core.telegram.org/bots/api#inlinequeryresult)
        - a *tuple*, whose first element is a list of InlineQueryResult, followed by positional arguments to be supplied to `bot.answerInlineQuery()`
        - a *dict* representing keyword arguments to be supplied to `bot.answerInlineQuery()`
    - It must be **thread-safe**, because many threads may access it as the same time.
- **\*compute_args** - positional arguments to *compute_fn*
- **\*\*compute_kwargs** - keyword arguments to *compute_fn*

<a id="telepot-helper-Router"></a>
### `telepot.helper.Router`

Here is the idea. Every message can be digested down to a *key*, which is then used to look up a *routing table*, leading to a *function*, which is applied to the message. This essentially *routes* messages to a number of handler functions according to some predefined criteria.

*Subclass:* [`telepot.async.helper.Router`](#telepot-async-helper-Router)

**Router(key_function, routing_table)**

Parameters:
- **key_function** - a function that takes one argument (a message), and returns one of the following:
    - a key
    - a tuple of one element `(key,)`
    - a tuple of two elements `(key, (positional arguments, ...))`
    - a tuple of three elements `(key, (positional argument, ...), {keyword: argument, ...})`
- **routing_table** - a dict of the form: `{key1: f1, key2: f2, ..., None: fd}`, where `f1`, `f2` ... are functions that take a *message* as the first argument, followed by *positional arguments* (if any) and *keyword arguments* (if any) returned by `key_function`. Routing table may optionally contain a `None` key that leads to a "default" function, `fd`. If `key_function` returns a key that does not match any in the dict, the default function is used.

In the majority of cases, we would like to route messages by flavor. As a result, `key_function` often is `telepot.flavor`, and `routing_table` often looks like `{'chat': f1, 'callback_query': f2, 'inline_query': f3, 'chosen_inline_result': f4}`. But this routing mechanism is more general than that.

The instance variable `key_function` and `routing_table` may be changed on the fly to achieve flexible routing.

**route(msg, \*args, \*\*kwargs)**

Execute routing mechanism as described above. The only relevent parameter is the first one - `msg`. Whatever follow are just placeholders that make it easy to do router nesting (or chaining). For example, regardless of what extra arguments produced by `top_router.key_function`, you can chain routers like this to achieve multi-level routing:

```python
top_router.routing_table['key'] = sub_router.route
```

<a id="telepot-helper-DefaultRouterMixin"></a>
### `telepot.helper.DefaultRouterMixin`

The class introduces a `Router` member into subclasses. This `Router` uses `telepot.flavor` as the key function, and has a routing table similar to: `{'chat': self.on_chat_message, 'callback_query': self.on_callback_query, 'inline_query': self.on_inline_query, 'chosen_inline_result': self.on_chosen_inline_result}`. But you don't have to implement all of those `self.on_***()` method, only implement the ones you need.

*Subclass:* [`telepot.helper.Monitor`](#telepot-helper-Monitor) [`telepot.helper.ChatHandler`](#telepot-helper-ChatHandler) [`telepot.helper.UserHandler`](#telepot-helper-UserHandler) 

This object exposes these properties:
- **router**

This object implements these methods:
- **on_message(msg)**: relay the message to the underlying `router.route(msg)`

<a id="telepot-helper-ListenerContext"></a>
### `telepot.helper.ListenerContext`

*Subclass:* [`telepot.helper.ChatContext`](#telepot-helper-ChatContext) [`telepot.helper.UserContext`](#telepot-helper-UserContext) [`telepot.helper.Monitor`](#telepot-helper-Monitor) [`telepot.async.helper.Monitor`](#telepot-async-helper-Monitor)

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
*Subclass:* [`telepot.helper.ChatHandler`](#telepot-helper-ChatHandler) [`telepot.async.helper.ChatHandler`](#telepot-async-helper-ChatHandler)

**ChatContext(bot, context_id, chat_id)**

Parameters:
- **bot** - the parent bot. Should be a `SpeakerBot` or one of its subclasses.
- **context_id** - this ID's purpose and uniqueness to up to the user.
- **chat_id** - the target chat

This object exposes these properties:
- **chat_id**
- **sender** - a `Sender` object aimed at the target chat
- **administrator** - a `Administrator` object aimed at the target chat

<a id="telepot-helper-UserContext"></a>
### `telepot.helper.UserContext`

*Superclass:* [`telepot.helper.ListenerContext`](#telepot-helper-ListenerContext)  
*Subclass:* [`telepot.helper.UserHandler`](#telepot-helper-UserHandler) [`telepot.async.helper.UserHandler`](#telepot-async-helper-UserHandler)

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

*Superclass:* [`telepot.helper.ListenerContext`](#telepot-helper-ListenerContext) [`telepot.helper.DefaultRouterMixin`](#telepot-helper-DefaultRouterMixin)

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
bot.message_loop(run_forever=True)
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

*Superclass:* [`telepot.helper.ChatContext`](#telepot-helper-ChatContext) [`telepot.helper.DefaultRouterMixin`](#telepot-helper-DefaultRouterMixin)

How to use this class:

1. Extend this class
2. Implement `on_message()`, optionally override `open()` and `on_close()`
3. Use `telepot.delegate.create_open()` to plug it into a `DelegatorBot`

**ChatHandler(seed_tuple, timeout, callback_query=True)**

Parameters:
- **seed_tuple** - a tuple of (bot, message, seed) generated by the delegation mechanism
- **timeout** - timeout for this object's `listener`
- **callback_query** - whether to capture callback query from the same user

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
bot.message_loop(run_forever=True)
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

*Superclass:* [`telepot.helper.UserContext`](#telepot-helper-UserContext) [`telepot.helper.DefaultRouterMixin`](#telepot-helper-DefaultRouterMixin)

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

<a id="telepot-helper-InlineUserHandler"></a>
### `telepot.helper.InlineUserHandler`

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
class Monitor(ListenerContext, DefaultRouterMixin):
    def __init__(...):
        ...

@openable
class ChatHandler(ChatContext, DefaultRouterMixin):
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

<a id="telepot-delegate-per-application"></a>
**per_application()**

Returns a seed-calculating-function that always returns `1`, ensuring at most one delegate for the entire application.

<a id="telepot-delegate-per-message"></a>
**per_message(flavors='all')**

Returns a seed-calculating-function that returns `[]` if a message matches the specified `flavors`, causing one delegate to be spawned for each such message.

`flavors` may be the string `all` (default), or a list of flavors, e.g. `['inline_query', 'chosen_inline_result']`.

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

<a id="telepot-routing"></a>
## `telepot.routing` module

This module provides key-function generators and routing-table generators to be used with [`Router`](#telepot-helper-Router).

<a id="telepot-routing-by-content-type"></a>
**by_content_type()**

Example:
```python
# Note the extra argument produced by `by_content_type()`
def on_text(msg, text):
    ...

def on_photo(msg, photo):
    ...

def on_voice(msg, voice):
    ...

r = telepot.helper.Router(by_content_type(), {'text': on_text,
                                              'photo': on_photo,
                                              'voice': on_voice,
                                               .....   ........  })
```

<a id="telepot-routing-by-command"></a>
**by_command(extractor, prefix=('/',), separator=' ', pass_args=False)**

<a id="telepot-routing-by-chat-command"></a>
**by_chat_command(prefix=('/',), separator=' ', pass_args=False)**

Suppose a bot accepts two commands `/start` and `/cancel`:

```python
from telepot.routing import by_chat_command

def on_start(msg):
    ...

def on_cancel(msg):
    ...

r = telepot.helper.Router(by_chat_command(), {'start': on_start,
                                              'cancel': on_cancel})
```

To catch invalid inputs, you can specify a `None` entry in the routing table. But there are actually two kinds of invalid inputs: 

- Strings that start with `/` but are followed by an unexpected word, e.g. `/haha`. In this case, key function is able to parse the string and produces the key `haha`. You can catch this kind of invalid inputs with a `None` entry in routing table.
- Strings that don't start with `/`. In this case, key function is not able to parse the string and produces the key `(None,)` - a 1-tuple with a single entry `None`. You can catch this kind of invalid inputs with a `(None,)` entry in routing table.

```python
def no_command_at_all(msg):
    ...

def on_bad_command(msg):
    ...

r = telepot.helper.Router(by_chat_command(), {'start': on_start,
                                              'cancel': on_cancel,
                                              (None,): no_command_at_all,
                                              None: on_bad_command})
```

Of course, if you don't care about the difference, use a single `None` entry to catch both.

If you allow commands to be prefixed by more special characters, say `#`:

```python
r = telepot.helper.Router(by_chat_command(prefix=('/','#')), {'start': on_start,
                                                              'cancel': on_cancel})
```

If some commands expect arguments, e.g. `/add 1`, and you want those arguments passed to the handler:

```python
def on_start(msg, command_args):  # command_args is a *list*
    ...

def on_cancel(msg, command_args):
    ...

def on_add(msg, command_args):
    ...

r = telepot.helper.Router(by_chat_command(pass_args=True), {'start': on_start,
                                                            'cancel': on_cancel,
                                                            'add': on_add})
```

If you want to recognize commands regardless of their cases and standardize all keys to lowercase, then you have to further process the keys produced by the original key function:

```python
from telepot.routing import lower_key

r = telepot.helper.Router(lower_key(by_chat_command()), {'start': on_start,
                                                         'cancel': on_cancel})
```

<a id="telepot-routing-by-text"></a>
**by_text()**

The key function produced by this function just extracts the `text` field's value from a message. Useful when you expect one of a few answers, for example, from a custom keyboard:

```python
from telepot.routing import by_text

def yes(msg):
    ...

def no(msg):
    ...

r = telepot.helper.Router(by_text(), {'Yes': yes,
                                      'No': no})
```

If you want to recognize answers regardless of their cases and standardize all keys to lowercase, use `lower_key` to process the keys:

```python
from telepot.routing import lower_key

r = telepot.helper.Router(lower_key(by_text()), {'yes': yes,
                                                 'no': no})
```

<a id="telepot-routing-by-data"></a>
**by_data()**

The key function produced by this function just extracts the `data` field's value from a message. Useful when you expect callback queries with a few possible `data` values:

```python
from telepot.routing import by_data

def on_callback_action1(msg):
    ...

def on_callback_action2(msg):
    ...

r = telepot.helper.Router(by_data(), {'action1': on_callback_action1,
                                      'action2': on_callback_action2})
```

<a id="telepot-routing-by-regex"></a>
**by_regex(extractor, regex, key=1)**

Suppose you want to monitor whether some computer science courses are mentioned in the conversation, you may use the regular expression `CS[0-9]{3}` to check for their presence:

```python
from telepot.routing import by_regex

def on_CS101(msg, match):
    ...

def on_CS202(msg, match):
    ...

regex_router = telepot.helper.Router(
                   by_regex(lambda msg: msg['text'], '(CS[0-9]{3})'), {
                   'CS101': on_CS101,
                   'CS202': on_CS202,
               })
```

The parentheses `()` in the regular expression is necessary because the key function needs to extract the key after a match. By default, the first pair of parentheses encloses the key. If you have more than one pair of parentheses in the regular expression and want the key to be somewhere else, use the parameter `key` to specify.

The parameter `regex` can be a simple pattern (as above) or a regular expression object (as created by `re.compile`).

When a match occurs, the match object is passed to the handler, following the `msg` argument.

If no match occurs, the key returned is `(None,)`, a 1-tuple with a single element `None`. This is to allow distinction between two cases:

- No match, where the key is a 1-tuple `(None,)`.
- A match occurs, but no such key in routing table. Catch this case with a `None` entry in routing table.

```python
def no_cs_courses_mentioned(msg):  # Note the absence of `match` argument, because there is no match.
    ...

def no_such_course(msg, match):
    ...

regex_router = telepot.helper.Router(
                   by_regex(lambda msg: msg['text'], '(CS[0-9]{3})'), {
                   'CS101': on_CS101,
                   'CS202': on_CS202,
                   (None,): no_cs_courses_mentioned,
                   None: no_such_course,
               })
```

If you don't care about the difference, use a `None` entry to catch both. In this case, the handler has to be able to accept a variable-length arguments, one with `msg` only, the other with `msg` and `match`.

<a id="telepot-routing-process-key"></a>
**process_key(processor, fn)**

<a id="telepot-routing-lower-key"></a>
**lower_key(fn)**

<a id="telepot-routing-upper-key"></a>
**upper_key(fn)**

<a id="telepot-routing-make-routing-table"></a>
**make_routing_table(obj, keys, prefix='on_')**

Composing a routing table is tedious in that you often have to repeat the key in the function/method name, for example:

```python
r = telepot.helper.Router(by_content_type(), {'text': handler.on_text,
                                              'photo': handler.on_photo,
                                              'voice': handler.on_voice,
                                               .....   ........  })
```

It would be easier to do this:

```python
from telepot.routing import make_routing_table

r = telepot.helper.Router(by_content_type(),
                          make_routing_table(handler, ['text',
                                                       'photo',
                                                       'voice',
                                                        ..... ])
```

By default, `make_routing_table` automatically looks for `on_*` methods of the `handler` object. Use the parameter `prefix` to change this default prefix.

If some method names do not conform to the form `on_*`, or if you want to specify a `None` entry, use a 2-tuple to give the method explicitly:

```python
r = telepot.helper.Router(by_content_type(),
                          make_routing_table(handler, ['text',
                                                       'photo',
                                                       'voice',
                                                        ..... ,
                                                       (None, handler.on_default)])
```

<a id="telepot-routing-make-content-type-routing-table"></a>
**make_content_type_routing_table(obj, prefix='on_'))**

There are 20+ content types. It is unreasonable to require you to write them all out. Do this instead:

```python
from telepot.routing import by_content_type, make_content_type_routing_table

r = telepot.helper.Router(by_content_type(), make_content_type_routing_table(handler))
```

If you don't care about some content types and want to handle them collectively, just delete their keys from the routing table and add a `None` entry:

```python
r = telepot.helper.Router(by_content_type(), make_content_type_routing_table(handler))

# Remove content types that you don't care about ...
del r.routing_table['contact']
del r.routing_table['location']
del r.routing_table['venue']
# Let them fall to the default handler ...

r.routing_table[None] = handler.on_ignore
```

<a id="telepot-exception"></a>
## `telepot.exception` module

<a id="telepot-exception-TelepotException"></a>
### `TelepotException`

Superclass of all exceptions raised by telepot.

<a id="telepot-exception-BadHTTPResponse"></a>
### `BadHTTPResponse`

*property* **status**

*property* **text**

*property* **response** - the underlying [`requests.Response`](http://docs.python-requests.org/en/master/api/#requests.Response) object (traditional version) or [`aiohttp.ClientResponse`](http://aiohttp.readthedocs.org/en/stable/client_reference.html#response-object) object (async version)

All requests to Bot API should result in a JSON response. Otherwise, a `BadHTTPResponse` is raised. While it is hard to pinpoint exactly when this might happen, the following situations have been observed to give rise to a `BadHTTPResponse`:

- an unreasonable token, e.g. `abc`, `123`, anything that does not even remotely resemble a correct token.

- a bad gateway, e.g. when Telegram servers are down.

<a id="telepot-exception-TelegramError"></a>
### `TelegramError`

*property* **description**

*property* **error_code**

*property* **json** - the underlying JSON object

In response to erroneous situations, Telegram would return a JSON object containing an *error code* and a *description*, causing telepot to raise a `TelegramError`. Before raising a generic `TelegramError`, however, telepot would look at all `TelegramError`'s subclasses and check if the error "matches" any of them. If so, an exception of that specific subclass is raised. This allows developers the choice to either catch specific errors (one of the subclasses) or to cast a wide net (to catch a `TelegramError`).

This is how telepot finds out if an error "matches" a subclass:

1. A `TelegramError` subclass always has a class variable `DESCRIPTION_PATTERNS`, which is a list of regular expressions.

2. If an error's `description` matches any of a subclass's `DESCRIPTION_PATTERNS`, a match occurs.

Telepot has these built-in subclasses (and their `DESCRIPTION_PATTERNS`):

- `UnauthorizedError` - `['unauthorized']`
- `BotWasKickedError` - `['bot.*kicked']`
- `BotWasBlockedError` - `['bot.*blocked']`
- `TooManyRequestsError` - `['too *many *requests']`
- `MigratedToSupergroupChatError` - `['migrated.*supergroup *chat']`

Users may define his own if he wishes to isolate more errors. For example:

```python
class ParseMessageTextError(telepot.exception.TelegramError):
    DESCRIPTION_PATTERNS = ['parse message text']

try:
    bot.sendMessage(chat_id, '[wrong format)', parse_mode='Markdown')
except ParseMessageTextError as e:
    print (e)

class FileTypeMismatchError(telepot.exception.TelegramError):
    DESCRIPTION_PATTERNS = ['file.*type.*mismatch', 'type.*file.*mismatch']

try:
    bot.sendPhoto(chat_id, 'NON-photo file_id')
except FileTypeMismatchError as e:
    print (e)
```

<a id="telepot-async"></a>
## `telepot.async` module (Python 3.5+)

This package mirrors the traditional version of telepot to make use of the `asyncio` module of Python 3.5. Nearly all methods share identical signatures with their traditional siblings, except that blocking methods now become **coroutines** and are often called with `yield from`.

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

*coroutine* **sendMessage(chat_id, text, parse_mode=None, disable_web_page_preview=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

Send text messages.

See: https://core.telegram.org/bots/api#sendmessage

*coroutine* **forwardMessage(chat_id, from_chat_id, message_id)**

Forward messages of any kind.

See: https://core.telegram.org/bots/api#forwardmessage

*coroutine* **sendPhoto(chat_id, photo, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

Send photos.

**photo**: May be one of the following:
- a *string*, indicating a `file_id` on the server
- a *file* object, as obtained by `open()`
- a tuple of *(filename, file-like object)*
    - filename: Telegram servers require to know the extension. So, the *name* doesn't really matter, as long as the extension is correct.
    - file-like object: as obtained by `urllib.request.urlopen()`
- a tuple of *(filename, bytes)*
    - filename: same as above
    - bytes: for example:

```python
response = yield from aiohttp.get('http://i.imgur.com/B1fzGoh.jpg')
content = yield from response.read()

yield from bot.sendPhoto(chat_id, ('abc.jpg', content))
```

**This works the same way with other `sendZZZ()` methods.**

See: https://core.telegram.org/bots/api#sendphoto

*coroutine* **sendAudio(chat_id, audio, duration=None, performer=None, title=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

Send audio files, if you want Telegram clients to display them in the music player. Your audio must be in the .mp3 format. For sending voice messages, use `sendVoice()` instead. 

See: https://core.telegram.org/bots/api#sendaudio

*coroutine* **sendDocument(chat_id, document, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

Send general files.

See: https://core.telegram.org/bots/api#senddocument

*coroutine* **sendSticker(chat_id, sticker, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

Send .webp stickers.

See: https://core.telegram.org/bots/api#sendsticker

*coroutine* **sendVideo(chat_id, video, duration=None, width=None, height=None, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

Send video files. Telegram clients support mp4 videos. Other formats may be sent using `sendDocument()`.

See: https://core.telegram.org/bots/api#sendvideo

*coroutine* **sendVoice(chat_id, audio, duration=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

Send audio files, if you want Telegram clients to display the file as a playable voice message. For this to work, your audio must be in an .ogg file encoded with OPUS. Other formats may be sent using `sendAudio()` or `sendDocument()`.

See: https://core.telegram.org/bots/api#sendvoice

*coroutine* **sendLocation(chat_id, latitude, longitude, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

Send point on the map.

See: https://core.telegram.org/bots/api#sendlocation

*coroutine* **sendVenue(chat_id, latitude, longitude, title, address, foursquare_id=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

See: https://core.telegram.org/bots/api#sendvenue

*coroutine* **sendContact(chat_id, phone_number, first_name, last_name=None, disable_notification=None, reply_to_message_id=None, reply_markup=None)**

See: https://core.telegram.org/bots/api#sendcontact

*coroutine* **sendChatAction(chat_id, action)**

Tell the user that something is happening on the bot's side. The status is set for 5 seconds or less (when a message arrives from your bot, Telegram clients clear its typing status).

See: https://core.telegram.org/bots/api#sendchataction

*coroutine* **getUserProfilePhotos(user_id, offset=None, limit=None)**

Get a list of profile pictures for a user.

See: https://core.telegram.org/bots/api#getuserprofilephotos

*coroutine* **getFile(file_id)**

Get a [File](https://core.telegram.org/bots/api#file) object, usually as a prelude to downloading a file. If you just want to download a file, call `download_file()` instead.

See: https://core.telegram.org/bots/api#getfile

*coroutine* **kickChatMember(chat_id, user_id)**

See: https://core.telegram.org/bots/api#kickchatmember

*coroutine* **unbanChatMember(chat_id, user_id)**

See: https://core.telegram.org/bots/api#unbanchatmember

*coroutine* **answerCallbackQuery(callback_query_id, text=None, show_alert=None)**

See: https://core.telegram.org/bots/api#answercallbackquery

*coroutine* **editMessageText(msgid_form, text, parse_mode=None, disable_web_page_preview=None, reply_markup=None)**

**msgid_form** can be:
- a tuple of *(chat_id, message_id)*
- a tuple of *(inline_message_id)*
- a single value - *inline_message_id*

See: https://core.telegram.org/bots/api#editmessagetext

*coroutine* **editMessageCaption(msgid_form, caption=None, reply_markup=None)**

**msgid_form** can be:
- a tuple of *(chat_id, message_id)*
- a tuple of *(inline_message_id)*
- a single value - *inline_message_id*

See: https://core.telegram.org/bots/api#editmessagecaption

*coroutine* **editMessageReplyMarkup(msgid_form, reply_markup=None)**

**msgid_form** can be:
- a tuple of *(chat_id, message_id)*
- a tuple of *(inline_message_id)*
- a single value - *inline_message_id*

See: https://core.telegram.org/bots/api#editmessagereplymarkup

*coroutine* **answerInlineQuery(inline_query_id, results, cache_time=None, is_personal=None, next_offset=None)**

Send answers to an inline query. `results` is a list of [InlineQueryResult](https://core.telegram.org/bots/api#inlinequeryresult).

See: https://core.telegram.org/bots/api#answerinlinequery

*coroutine* **getUpdates(offset=None, limit=None, timeout=None)**

Receive incoming updates.

See: https://core.telegram.org/bots/api#getupdates

*coroutine* **setWebhook(url=None, certificate=None)**

Specify a url and receive incoming updates via an outgoing webhook.

See: https://core.telegram.org/bots/api#setwebhook

*coroutine* **download_file(file_id, dest)**

Download a file. `dest` can be a path (string) or a Python file object.

*coroutine* **message_loop(handler=None, source=None, ordered=True, maxhold=3)**

Constantly checks for updates and applies `handler` to each message received. `handler` may be:

- a regular *function* that takes one argument, the message. It will be called directly, like all regular functions.
- a *coroutine* that takes one argument, the message. It will be allocated a task using `BaseEventLoop.create_task()`.
- a *dict* in the form: `{'chat': f1, 'callback_query': f2, 'inline_query': f3, 'chosen_inline_result': f4}`, where `f1`, `f2`, `f3`, `f4` may be regular functions or coroutines that take one argument, the message. Which gets called is determined by the flavor of a message. You don't have to include all flavors in the dict, only the ones you need.
- `None` (default), in which case you have to define some instance methods for the bot to be used as callbacks. You have two options:
    - implement the bot's `handle(msg)` method.
    - implement one or more of `on_chat_message(msg)`, `on_inline_query(msg)`, and `on_chosen_inline_result(msg)`. Which gets called is determined by the flavor of a message.

If `source` is `None` (default), `getUpdates()` is used to obtain updates from Telegram servers. If `source` is an `asyncio.Queue`, updates are obtained from the queue. In normal scenarios, a web application implementing a webhook dumps updates into the queue, while the bot pulls updates from it. 

Parameters:
- handler: as describe above.
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

Note:
- `relax` and `timeout` are relevant *only if you use `getUpdates()`*
- `source`, `ordered`, and `maxhold` are relevant *only if you use webhook*.

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

loop.create_task(bot.message_loop())
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

loop.create_task(bot.message_loop(handle))
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

This class implements the above logic in its `handle` method. Once you supply a list of *(seed_calculating_function, coroutine_producing_function)* pairs to the constructor and invoke `message_loop()`, the above logic will be executed for every message received.

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
loop.create_task(bot.message_loop())
print('Listening ...')

loop.run_forever()
```

<a id="telepot-async-functions"></a>
### Functions in `telepot.async` module

**flavor_router(routing_table)**

Returns a *coroutine* that takes one argument (a message), and depending on the flavor, routes that message to another function/coroutine according to the *routing_table*.

The *routing_table* is a dict of the form: `{'chat': f1, 'callback_query': f2, 'inline_query': f3, 'chosen_inline_result': f4}`, where `f1`, `f2`, `f3`, `f4` are functions/coroutines that take one argument (the message). You don't have to include all flavors in the dict, only the ones you need.

<a id="telepot-async-helper"></a>
## `telepot.async.helper` module (Python 3.5+)

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

**Answerer(bot, loop=None)**

**answer(inline_query, compute_fn, \*compute_args, \*\*compute_kwargs)**

Creates a task that calls the *compute function* (along with additional arguments), then applies the returned value to `bot.answerInlineQuery()`, in effect answering the inline query. If a preceding task is already working for a user, that task is cancelled, thus ensuring at most one active task per user id.

Parameters:
- **inline_query** - from which the `from` `id` and query `id` will be inferred
- **compute_fn** - an answer-computing function. May be coroutine.
    - Its returned value is given to `bot.answerInlineQuery()` to send.
    - It may return one of the following:
        - a *list* of [InlineQueryResult](https://core.telegram.org/bots/api#inlinequeryresult)
        - a *tuple*, whose first element is a list of InlineQueryResult, followed by positional arguments to be supplied to `bot.answerInlineQuery()`
        - a *dict* representing keyword arguments to be supplied to `bot.answerInlineQuery()`
- **\*compute_args** - positional arguments to *compute_fn*
- **\*\*compute_kwargs** - keyword arguments to *compute_fn*

<a id="telepot-async-helper-Router"></a>
### `telepot.async.helper.Router`

*Superclass:* [`telepot.helper.Router`](#telepot-helper-Router)

This class is basically identical to its superclass, except that it overrides the method `route` to deal with handler functions possibly being coroutines. As a result, the method `route` also becomes a coroutine.

*coroutine* **route(msg, \*args, \*\*kwargs)**

<a id="telepot-async-helper-DefaultRouterMixin"></a>
### `telepot.async.helper.DefaultRouterMixin`

The class introduces a `Router` member into subclasses. This `Router` uses `telepot.flavor` as the key function, and has a routing table similar to: `{'chat': self.on_chat_message, 'callback_query': self.on_callback_query, 'inline_query': self.on_inline_query, 'chosen_inline_result': self.on_chosen_inline_result}`. But you don't have to implement all of those `self.on_***()` method, only implement the ones you need.

*Subclass:* [`telepot.async.helper.Monitor`](#telepot-async-helper-Monitor) [`telepot.async.helper.ChatHandler`](#telepot-async-helper-ChatHandler) [`telepot.async.helper.UserHandler`](#telepot-async-helper-UserHandler) 

This object exposes these properties:
- **router**

This object implements these methods:
- *coroutine* **on_message(msg)**: relay the message to the underlying `router.route(msg)`

<a id="telepot-async-helper-Monitor"></a>
### `telepot.async.helper.Monitor`

*Superclass:* [`telepot.helper.ListenerContext`](#telepot-helper-ListenerContext) [`telepot.async.helper.DefaultRouterMixin`](#telepot-async-helper-DefaultRouterMixin)

<a id="telepot-async-helper-ChatHandler"></a>
### `telepot.async.helper.ChatHandler`

*Superclass:* [`telepot.helper.ChatContext`](#telepot-helper-ChatContext) [`telepot.async.helper.DefaultRouterMixin`](#telepot-async-helper-DefaultRouterMixin)

<a id="telepot-async-helper-UserHandler"></a>
### `telepot.async.helper.UserHandler`

*Superclass:* [`telepot.helper.UserContext`](#telepot-helper-UserContext) [`telepot.async.helper.DefaultRouterMixin`](#telepot-async-helper-DefaultRouterMixin)

<a id="telepot-async-helper-InlineUserHandler"></a>
### `telepot.async.helper.InlineUserHandler`

<a id="telepot-async-helper-openable"></a>
### `telepot.async.helper.openable` class decorator

This is an alias to [telepot.helper.openable](#telepot-helper-openable).

<a id="telepot-async-delegate"></a>
## `telepot.async.delegate` module (Python 3.5+)

This module provides functions used in conjunction with `telepot.async.DelegatorBot` to specify delegation patterns. See `telepot.async.DelegatorBot` for more details.

<a id="telepot-async-delegate-per-chat-id"></a>
**per_chat_id()** - alias to [telepot.delegate.per_chat_id()](#telepot-delegate-per-chat-id)  
<a id="telepot-async-delegate-per-chat-id-in"></a>
**per_chat_id_in(set)** - alias to [telepot.delegate.per_chat_id_in(set)](#telepot-delegate-per-chat-id-in)  
<a id="telepot-async-delegate-per-chat-id-except"></a>
**per_chat_id_except(set)** - alias to [telepot.delegate.per_chat_id_except(set)](#telepot-delegate-per-chat-id-except)  
<a id="telepot-async-delegate-per-from-id"></a>
**per_from_id()** - alias to [telepot.delegate.per_from_id()](#telepot-delegate-per-from-id)  
<a id="telepot-async-delegate-per-from-id-in"></a>
**per_from_id_in(set)** - alias to [telepot.delegate.per_from_id_in(set)](#telepot-delegate-per-from-id-in)  
<a id="telepot-async-delegate-per-from-id-except"></a>
**per_from_id_except(set)** - alias to [telepot.delegate.per_from_id_except(set)](#telepot-delegate-per-from-id-except)  
<a id="telepot-async-delegate-per-inline-from-id"></a>
**per_inline_from_id()** - alias to [telepot.delegate.per_inline_from_id()](#telepot-delegate-per-inline-from-id)  
<a id="telepot-async-delegate-per-inline-from-id-in"></a>
**per_inline_from_id_in(set)** - alias to [telepot.delegate.per_inline_from_id_in(set)](#telepot-delegate-per-inline-from-id-in)  
<a id="telepot-async-delegate-per-inline-from-id-except"></a>
**per_inline_from_id_except(set)** - alias to [telepot.delegate.per_inline_from_id_except(set)](#telepot-delegate-per-inline-from-id-except)  
<a id="telepot-async-delegate-per-application"></a>
**per_application()** - alias to [telepot.delegate.per_application()](#telepot-delegate-per-application)  
<a id="telepot-async-delegate-per-message"></a>
**per_message(flavors='all')** - alias to [telepot.delegate.per_message(flavors='all')](#telepot-delegate-per-message)

<a id="telepot-async-delegate-call"></a>
**call(func, \*args, \*\*kwargs)**

Returns a coroutine-producing-function. `func` can be a regular function or a coroutine function, that takes a *seed_tuple* as the first argument, followed by those explicitly supplied.

<a id="telepot-async-delegate-create-run"></a>
**create_run(cls, \*args, \*\*kwargs)**

Returns a coroutine-producing-function that creates an object of `cls` and returns a coroutine object by calling its `run()` method. The `cls` constructor should take a *seed_tuple* as the first argument, followed by those explicitly supplied. The `run` method requires no argument, can be a regular function or a coroutine function.

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

An easy way to fulfilled these requirements is to extend from [`Monitor`](#telepot-async-helper-Monitor), [`ChatHandler`](#telepot-async-helper-ChatHandler), [`UserHandler`](#telepot-async-helper-UserHandler), or decorating a class with the [`@openable`](#telepot-async-helper-openable) class decorator.

<a id="telepot-async-routing"></a>
## `telepot.async.routing` module (Python 3.5+)

Identical to module [`telepot.routing`](#telepot-routing).
