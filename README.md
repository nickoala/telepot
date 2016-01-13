# telepot - Python framework for Telegram Bot API

**[Installation](#installation)**  
**[The Basics](#basics)**  
**[Dealing with Inline Query](#inline-query)**  
**[The Intermediate](#intermediate)**  
**[The Advanced](#advanced)**  
**[Async Version](#async)** (Python 3.4.3 or newer)  
**[Webhook Interface](#webhook)**  
**[Reference](https://github.com/nickoala/telepot/blob/master/REFERENCE.md)**  
**[Mailing List](https://groups.google.com/forum/#!forum/telepot)**  
**[Examples](#examples)**  
- [Dicey Clock](#examples-dicey-clock)
- [Skeletons](#examples-skeletons)
- [Indoor climate monitor](#examples-indoor)
- [IP Cam using Telegram as DDNS](#examples-ipcam)
- [Emodi - an Emoji Unicode Decoder](#examples-emodi)
- [Message Counter](#examples-message-counter)
- [Guess-a-number](#examples-guess-a-number)
- [Chatbox - a Mailbox for Chats](#examples-chatbox)
- [Webhooks](#examples-webhooks)

### Recent changes

**6.1 (2016-01-13)**

- Changed normal message's flavor to `normal`

**6.0 (2016-01-13)**

- Moved all namedtuple-related stuff to a new module `telepot.namedtuple`. All calls to the function `telepot.namedtuple()` should be changed to `telepot.namedtuple.namedtuple()`
- Added a function `telepot.flavor()` to differentiate between a normal message and an inline query
- Added `flavor` parameter to `telepot.glance2()` to extract info according to message flavor
- `notifyOnMessage()` and `messageLoop()` can handle inline query as well as normal chat messages
- Added a few `per_XXX_id()` functions useful for spawning delegates for inline queries
- Added `UserHandler`
- `reply_markup` parameter can accept namedtuples `ReplyKeyboardMarkup`, `ReplyKeyboardHide`, `ForceReply` as values

**As you can see, 6.0 has just come out. Below documentations are not entirely up-to-date, although most of the stuff still applies. I will update them as soon as I can.**

**5.0 (2015-12-28)**

- Added webhook interface
- Added `supergroup_chat_created`, `migrate_to_chat_id`, `migrate_from_chat_id`, and `channel_chat_created` fields to Message

**4.1 (2015-11-03)**

- Added `openable()` class decorator
- Default `on_close()` prints out exception
- Async `SpeakerBot` and `DelegatorBot` constructor accepts `loop` parameter

**[Go to full changelog »](https://github.com/nickoala/telepot/blob/master/CHANGELOG.md)**

------

Telepot has been tested on **Raspbian** and **CentOS**, using **Python 2.7 - 3.4**. Below discussions are based on Raspbian and Python 2.7, except noted otherwise.

<a id="installation"></a>
## Installation

pip:
```
$ sudo apt-get install python-pip
$ sudo pip install telepot

$ sudo pip install telepot --upgrade  # UPGRADE
```

easy_install:

```
$ easy_install telepot
$ easy_install --upgrade telepot  # UPGRADE
```

Download manually:

```
$ wget https://pypi.python.org/packages/source/t/telepot/telepot-6.1.zip
$ unzip telepot-6.1.zip
$ cd telepot-6.1
$ python setup.py install
```

<a id="basics"></a>
## The Basics

To use the [Telegram Bot API](https://core.telegram.org/bots/api), you first have to [get a **bot account**](http://www.instructables.com/id/Set-up-Telegram-Bot-on-Raspberry-Pi/) by [chatting with the BotFather](https://core.telegram.org/bots).

BotFather will give you a **token**, something like `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`. With the token in hand, you can start using telepot to access the bot account.

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
                         u'last_name': u'Lee',
                         u'type': u'private'},
               u'date': 1444723969,
               u'from': {u'first_name': u'Nick',
                         u'id': 999999999,
                         u'last_name': u'Lee'},
               u'message_id': 4015,
               u'text': u'Hello'},
  u'update_id': 100000000}]
```

`999999999` is obviously a fake ID. `Nick` `Lee` is my real name, though.

The `chat` field indicates the source of the message. Its `type` can be `private`, `group`, or `channel` (whose meanings should be obvious, I hope). In the above example, `Nick` `Lee` just sent a `private` message to the bot.

I encourage you to experiment sending various types of messages (e.g. voice, photo, sticker, etc) to the bot, via different sources (e.g. private chat, group chat, channel), to see the varying structures of messages. Consult the [Bot API documentations](https://core.telegram.org/bots/api#available-types) to learn what fields may be present under what circumstances. **Bot API's [object](https://core.telegram.org/bots/api#available-types) translates directly to Python dict.** In the above example, `getUpdates()` just returns an array of `Update` objects represented as Python dicts.

Note the `update_id`. It is an ever-increasing number. Next time you should use `getUpdates(offset=100000001)` to avoid getting the same old messages over and over. Giving an `offset` essentially acknowledges to the server that you have received all `update_id`s lower than `offset`.

```python
>>> bot.getUpdates(offset=100000001)
[]
```

#### An easier way to receive messages

It is troublesome to keep checking messages and managing `offset`. Fortunately, telepot can take care of that for you, and notify you whenever new messages arrive.

```python
>>> from pprint import pprint
>>> def handle_message(msg):
...     pprint(msg)
...
>>> bot.notifyOnMessage(handle_message)
```

After setting up this callback, sit back and monitor the arriving messages.

Below can be a skeleton for simple telepot programs:

```python
import sys
import time
import pprint
import telepot

def handle(msg):
    pprint.pprint(msg)
    # Do your stuff here ...


# Getting the token from command-line is better than embedding it in code,
# because tokens are supposed to be kept secret.
TOKEN = sys.argv[1]

bot = telepot.Bot(TOKEN)
bot.notifyOnMessage(handle)
print 'Listening ...'

# Keep the program running.
while 1:
    time.sleep(10)
```

#### Quickly `glance2()` a message

When processing a message, a few pieces of information are so central that you almost always have to extract them. Use `glance2()` to extract a tuple of *(content_type, chat_type, chat_id)* from a message.

*content_type* can be: `text`, `voice`, `sticker`, `photo`, `audio`, `document`, `video`, `contact`, `location`, `new_chat_participant`, `left_chat_participant`, `new_chat_title`, `new_chat_photo`, `delete_chat_photo`, or `group_chat_created`.

*chat_type* can be: `private`, `group`, or `channel`.

It is a good habit to always check the *content_type* before further processing. Do not assume every message is a `text`.

A better skeleton would look like:

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

#### Download files

For a `voice`, `sticker`, `photo`, `audio`, `document`, or `video` message, look for the `file_id` to download the file. For example, a `photo` may look like:

```python
{u'chat': {u'first_name': u'Nick', u'id': 999999999, u'type': u'private'},
 u'date': 1444727788,
 u'from': {u'first_name': u'Nick', u'id': 999999999},
 u'message_id': 4017,
 u'photo': [{u'file_id': u'JiLOABNODdbdP_q2vwXLtLxHFnUxNq2zszIABM4s1rQm6sTYG3QAAgI',
             u'file_size': 734,
             u'height': 67,
             u'width': 90},
            {u'file_id': u'JiLOABNODdbdP_q2vwXLtLxHFnUxNq2zszIABJDUyXzQs-kJGnQAAgI',
             u'file_size': 4568,
             u'height': 240,
             u'width': 320},
            {u'file_id': u'JiLOABNODdbdP_q2vwXLtLxHFnUxNq2zszIABHWm5IQnJk-EGXQAAgI',
             u'file_size': 20480,
             u'height': 600,
             u'width': 800},
            {u'file_id': u'JiLOABNODdbdP_q2vwXLtLxHFnUxNq2zszIABEn8PaFUzRhBGHQAAgI',
             u'file_size': 39463,
             u'height': 960,
             u'width': 1280}]}
```

It has a number of `file_id`s, with various file sizes. These are thumbnails of the same image. Download one of them by:

```python
>>> bot.downloadFile(u'JiLOABNODdbdP_q2vwXLtLxHFnUxNq2zszIABEn8PaFUzRhBGHQAAgI', 'save/to/path')
```

#### Send messages

Enough about receiving messages. Sooner or later, your bot will want to send *you* messages. You should have discovered your own user ID from above interactions. I will keeping using my fake ID of `999999999`. Remember to substitute your own (real) user ID.

```python
>>> bot.sendMessage(999999999, 'Good morning!')
```

After being added as an **administrator** to a channel, the bot can send messages to the channel:

```python
>>> bot.sendMessage('@channelusername', 'Hi, everybody!')
```

#### Send a custom keyboard

A custom keyboard presents custom buttons for users to tab. Check it out.

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

```python
>>> f = open('zzzzzzzz.jpg', 'rb')  # some file on local disk
>>> response = bot.sendPhoto(999999999, f)
>>> pprint(response)
{u'chat': {u'first_name': u'Nick', u'id': 999999999, u'type': u'private'},
 u'date': 1444728667,
 u'from': {u'first_name': u'Your Bot',
           u'id': 123456789,
           u'username': u'YourBot'},
 u'message_id': 4022,
 u'photo': [{u'file_id': u'JiLOABNODdbdPyNZjwa-sKYQW6TBqrWfsztABO2NukbYlhLYlREBAAEC',
             u'file_size': 887,
             u'height': 29,
             u'width': 90},
            {u'file_id': u'JiLOABNODdbdPyNZjwa-sKYQW6TBqrWfsztABHKq66Hh0YDrlBEBAAEC',
             u'file_size': 9971,
             u'height': 102,
             u'width': 320},
            {u'file_id': u'JiLOABNODdbdPyNZjwa-sKYQW6TBqrWfsztABNBLmxkkiqKikxEBAAEC',
             u'file_size': 14218,
             u'height': 128,
             u'width': 400}]}
```

The server returns a number of `file_id`s, with various file sizes. These are thumbnails of the uploaded image. If you want to resend the same file, just give one of the `file_id`s.

```python
>>> bot.sendPhoto(999999999, u'JiLOABNODdbdPyNZjwa-sKYQW6TBqrWfsztABO2NukbYlhLYlREBAAEC')
```

Besides sending photos, you may also `sendAudio()`, `sendDocument()`, `sendSticker()`, `sendVideo()`, and `sendVoice()`.

**[Read the reference »](https://github.com/nickoala/telepot/blob/master/REFERENCE.md)**

<a id="inline-query"></a>
## Dealing with Inline Query

By default, a bot only receives messages through a private chat, a group, or a channel. These are what I call *normal messages*.

By sending a `/setinline` command to BotFather, you enable the bot to receive *[inline queries](https://core.telegram.org/bots/inline)* as well. Inline query is a way for users to ask your bot questions, even if they have not opened a chat with your bot, nor in the same group with your bot.

If you don't understand or don't care about inline query, you may skip this section. All your bot receives will be normal messages. All remaining discussions still work for you. You can even safely ignore code blocks that deal with inline queries.

If you do care about inline query, the important thing to note is that your bot will now receive two **flavors** of messages: normal messages and inline queries. A normal message has the flavor `normal`; an inline query has the flavor `inline_query`.

#### Use `flavor()` to differentiate the flavor

```python
flavor = telepot.flavor(msg)

if flavor == 'normal':
    print 'Normal message'
elif flavor == 'inline_query':
    print 'Inline query'
```

#### You may `glance2()` an inline query too

Supply the correct `flavor`, and it gives you some "headline" info about the inline query:

```python
query_id, from_user_id, query_string = telepot.glance2(msg, flavor='inline_query')
```

#### `answerInlineQuery()`

Coming soon ...

#### A skeleton that deals with inline query

Coming soon ...

<a id="intermediate"></a>
## The Intermediate

Defining a global message handler may lead to the proliferation of global variables quickly. Encapsulation may be achieved by extending the `Bot` class, defining a `handle` method, then calling `notifyOnMessage()` with no callback function. This way, the object's `handle` method will be used as the callback.

Here is a skeleton using this strategy:

```python
import sys
import time
import telepot

class YourBot(telepot.Bot):
    def handle(self, msg):
        content_type, chat_type, chat_id = telepot.glance2(msg)
        print content_type, chat_type, chat_id
        # Do your stuff according to `content_type` ...


TOKEN = sys.argv[1] # get token from command-line

bot = YourBot(TOKEN)
bot.notifyOnMessage()
print 'Listening ...'

# Keep the program running.
while 1:
    time.sleep(10)
```

**[Read the reference »](https://github.com/nickoala/telepot/blob/master/REFERENCE.md)**

<a id="advanced"></a>
## The Advanced

Having a single message handler is adequate for simple programs. For more sophisticated programs where states need to be maintained across messages, a better approach is needed.

Consider this scenario. A bot wants to have an intelligent conversation with a lot of users, and if we could only use a single message-handling function, we would have to maintain some state variables about each conversation *outside* the function. On receiving each message, we first have to check whether the user already has a conversation started, and if so, what we have been talking about. There has to be a better way.

Let's look at my solution. Here, I implement a bot that counts how many messages have been sent by an individual user. If no message is received after 10 seconds, it starts over (timeout). The counting is done *per chat* - that's the important point.

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

Noteworthy are two classes: `DelegatorBot` and `MessageCounter`. Let me explain one by one.

#### `DelegatorBot`

It is a `Bot` with the newfound ability to spawn *delegates*. Its constructor takes a list of tuples telling it when and how to spawn delegates. In the example above, it is spawning one `MessageCounter` *per chat id*.

Technically, `per_chat_id()` returns a *seed-calculating-function*, and `create_open()` returns a *delegate-producing-function*. I won't get into details here. You can [read the reference](https://github.com/nickoala/telepot/blob/master/REFERENCE.md#telepot-DelegatorBot) for that.

Simply put, a *seed-calculating-function* determines **when** to spawn a delegate, while a *delegate-producing-function* determines **how** to spawn one. The default manifestation of a delegate is a thread, although you can override that.

#### `MessageCounter`, extending from `ChatHandler`

This is the class that deals with an individual chat. Being a subclass of `ChatHandler` offers a few benefits:

- inherits utilities for dealing with a chat, e.g. a `sender` object that makes it easy to send messages to a chat (as demonstrated above), a `listener` object that waits for messages from the chat (implicitly done, not shown above).
- inherits most methods and attributes required by `create_open()`. Just implement `on_message()` and you are done.

`on_message()` is called whenever a chat message arrives. How messages are distributed to the correct object is done by the library. You don't have to worry about it.

**[Read the reference »](https://github.com/nickoala/telepot/blob/master/REFERENCE.md)**

<a id="async"></a>
## Async Version (Python 3.4.3 or newer)

Everything discussed so far assumes traditional Python. That is, network operations are blocking; if you want to serve many users at the same time, some kind of threads are usually needed. Another option is to use an asynchronous or event-driven framework, such as [Twisted](http://twistedmatrix.com/).

Python 3.4 introduces its own asynchronous architecture, the `asyncio` module. Telepot supports that, too. If your bot is to serve many people, I strongly recommend doing it asynchronously. Threads, in my opinion, is a thing of yesteryears.

Raspbian does not come with Python 3.4. You have to compile it yourself.

```
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get install libssl-dev openssl libreadline-dev
$ cd ~
$ wget https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tgz
$ tar zxf Python-3.4.3.tgz
$ cd Python-3.4.3
$ ./configure
$ make
$ sudo make install
```

Finally:

```
$ sudo pip3.4 install telepot
```

In case you are not familiar with asynchronous programming, let's start by learning about generators and coroutines:

- ['yield' and Generators Explained](https://www.jeffknupp.com/blog/2013/04/07/improve-your-python-yield-and-generators-explained/)
- [Sequences and Coroutines](http://wla.berkeley.edu/~cs61a/fa11/lectures/streams.html)

... why we want asynchronous programming:

- [Problem: Threads Are Bad](https://glyph.twistedmatrix.com/2014/02/unyielding.html)

... how generators and coroutines are applied to asynchronous programming:

- [Understanding Asynchronous IO](http://sahandsaba.com/understanding-asyncio-node-js-python-3-4.html)
- [What are the main uses of `yield from`?](http://stackoverflow.com/questions/9708902/in-practice-what-are-the-main-uses-for-the-new-yield-from-syntax-in-python-3)
- [A Curious Course on Coroutines and Concurrency](http://www.dabeaz.com/coroutines/)

... and how an asyncio program is generally structured:

- [The New asyncio Module in Python 3.4](http://www.drdobbs.com/open-source/the-new-asyncio-module-in-python-34-even/240168401)
- [Event loop examples](https://docs.python.org/3/library/asyncio-eventloop.html#event-loop-examples)
- [HTTP server and client](http://aiohttp.readthedocs.org/en/stable/)

#### Very similar to the traditional, but different

The async version of `Bot`, `SpeakerBot`, and `DelegatorBot` basically mirror the traditional version's. Main differences are:
- blocking methods (e.g. `sendMessage()`) are now coroutines, and should be called with `yield from`
- delegation is achieved by coroutine and task

Because of that (and this is true of asynchronous Python in general), a lot of methods will not work in the interactive Python interpreter like regular functions would. They will have to be driven by an event loop.

#### Skeleton, by extending the basic `Bot`

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

#### Skeleton, by defining a global hander

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

#### Skeleton for `DelegatorBot`

I have re-done the `MessageCounter` example here. Again, it is very similar to the [traditional version](#advanced).

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

**[Read the reference »](https://github.com/nickoala/telepot/blob/master/REFERENCE.md)**

<a id="webhook"></a>
## Webhook Interface

So far, we have been using `getUpdates()` to obtain new messages from Telegram servers - both `notifyOnMessage()` and `messageLoop()` call `getUpdates()` constantly under the hood. Another way to obtain new messages is through **[webhooks](https://core.telegram.org/bots/api#setwebhook)**, in which case Telegram servers will send an HTTPS POST request to an URL you specify, containing a JSON-serialized [Update](https://core.telegram.org/bots/api#update) object, whenever there is an update for the bot.

Setting up a webhook is more complicated than using `getUpdates()` because:

1. You have to obtain an URL
2. You have to obtain and set up an SSL certificate for the URL
3. You have to set up a web server to handle the POST requests coming from Telegram servers

For a simple bot application, it is easy to use telepot directly from the web application. To make a smarter bot where you want to leverage telepot's more advanced features (e.g. to maintain separate "threads" of conversation using `DelegatorBot` and `ChatHandler`), we need a structured way to bring the web application and telepot together.

Webhook also presents a subtle problem: closely bunched updates may arrive out of order. That is, update_id `1000` may arrive ahead of update_id `999`, if the two are issued by Telegram servers very closely. Unless a bot absolutely doesn't care about update order, it will have to re-order them in some way.

*Since 5.0*, telepot has a mechanism for web applications to interface with easily, and it takes care of re-ordering for you. The mechanism is simple: you call `notifyOnMessage()` or `messageLoop()` to initiate the bot's message handling as usual, but with an additional parameter `source`, which is a queue. 

```python
# for Python 2 and 3
try:
    from Queue import Queue
except ImportError:
    from queue import Queue

def handle(msg):
    ......

bot = telepot.Bot(TOKEN)
update_queue = Queue()

# get updates from queue, not from Telegram servers
bot.notifyOnMessage(handle, source=update_queue)
```

The web application, upon receiving a POST request, dumps the data onto the queue, for the bot to retrieve at the other end. The bot will re-order the updates if necessary. Assuming [Flask](http://flask.pocoo.org/) as the web application framework:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook_path', methods=['GET', 'POST'])
def pass_update():
    update_queue.put(request.data)  # dump data to queue
    return 'OK'
```

It is beyond the scope of this document to detail the usage of web frameworks. Please look at the **[webhook examples](#examples-webhooks)** for full demonstrations. Remember, you will have to set up the webhook URL, SSL certificate, and web server on your own.

**[Read the reference »](https://github.com/nickoala/telepot/blob/master/REFERENCE.md)**

<a id="examples"></a>
## Examples

<a id="examples-dicey-clock"></a>
#### Dicey Clock

[Here is a tutorial](http://www.instructables.com/id/Set-up-Telegram-Bot-on-Raspberry-Pi/) teaching you how to setup a bot on Raspberry Pi. This simple bot does nothing much but accepts two commands:

- `/roll` - reply with a random integer between 1 and 6, like rolling a dice.
- `/time` - reply with the current time, like a clock.

**[Source »](https://github.com/nickoala/telepot/blob/master/examples/diceyclock.py)**

<a id="examples-skeletons"></a>
#### Skeletons

A starting point for your telepot programs.

**[Traditional version 1 »](https://github.com/nickoala/telepot/blob/master/examples/skeleton.py)**   
**[Traditional version 2 »](https://github.com/nickoala/telepot/blob/master/examples/skeleton_extend.py)**   
**[Async version 1 »](https://github.com/nickoala/telepot/blob/master/examples/skeletona.py)**  
**[Async version 2 »](https://github.com/nickoala/telepot/blob/master/examples/skeletona_extend.py)**

<a id="examples-indoor"></a>
#### Indoor climate monitor

Running on a Raspberry Pi with a few sensors attached, this bot accepts these commands:

- `/now` - Report current temperature, humidity, and pressure
- `/1m` - Report every 1 minute
- `/1h` - Report every 1 hour
- `/cancel` - Cancel reporting

**[Source »](https://github.com/nickoala/sensor/blob/master/examples/indoor.py)**

<a id="examples-ipcam"></a>
#### IP Cam using Telegram as DDNS

Running on a Raspberry Pi with a camera module attached, this bot accepts these commands:

- `/open` - Open a port through the router to make the video stream accessible, and send you the URL (which includes the router's public IP address)
- `/close` - Close the port

**[Project page »](https://github.com/nickoala/ipcam)**

<a id="examples-emodi"></a>
#### Emodi - an Emoji Unicode Decoder

Sooner or later, you want your bots to be able to send emoji. You may look up the unicode on the web, or from now on, you may just fire up Telegram and ask **[Emodi :blush:](https://telegram.me/emodibot)**

**[Traditional version »](https://github.com/nickoala/telepot/blob/master/examples/emodi.py)**  
**[Async version »](https://github.com/nickoala/telepot/blob/master/examples/emodia.py)**

I am running this bot on a CentOS server. You should be able to talk to it 24/7. Intended for multiple users, the async version is being run.

By the way, I just discovered a Python **[emoji](https://pypi.python.org/pypi/emoji/)** package. Use it.

<a id="examples-message-counter"></a>
#### Message Counter

Counts number of messages a user has sent. Illustrates the basic usage of `DelegateBot` and `ChatHandler`.

**[Traditional version »](https://github.com/nickoala/telepot/blob/master/examples/counter.py)**  
**[Async version »](https://github.com/nickoala/telepot/blob/master/examples/countera.py)**

<a id="examples-guess-a-number"></a>
#### Guess-a-number

1. Send the bot anything to start a game.
2. The bot randomly picks an integer between 0-99.
3. You make a guess.
4. The bot tells you to go higher or lower.
5. Repeat step 3 and 4, until guess is correct.

This example is able to serve many players at once. It illustrates the usage of `DelegateBot` and `ChatHandler`.

**[Traditional version »](https://github.com/nickoala/telepot/blob/master/examples/guess.py)**  
**[Async version »](https://github.com/nickoala/telepot/blob/master/examples/guessa.py)**

<a id="examples-chatbox"></a>
#### Chatbox - a Mailbox for Chats

1. People send messages to your bot.
2. Your bot remembers the messages.
3. You read the messages later.

It accepts the following commands from you, the owner, only:

- `/unread` - tells you who has sent you messages and how many
- `/next` - read next sender's messages

This example can be a starting point for **customer support** type of bot accounts. For example, customers send questions to a bot account; staff answers the questions behind the scene, makes it look like the bot is answering questions.

It further illustrates the use of `DelegateBot` and `ChatHandler`, and how to spawn delegates differently according to the role of users.

This example only handles text messages and stores messages in memory. If the bot is killed, all messages are lost. It is an *example* after all.

**[Traditional version »](https://github.com/nickoala/telepot/blob/master/examples/chatbox_nodb.py)**  
**[Async version »](https://github.com/nickoala/telepot/blob/master/examples/chatboxa_nodb.py)**

<a id="examples-webhooks"></a>
#### Webhooks

A few examples from above are duplicated, by using webhooks. For traditional Python, the web frontend used is **[Flask](http://flask.pocoo.org/)**. For asynchronous Python, **[aiohttp](http://aiohttp.readthedocs.org/en/stable/)**.

**[Skeleton + Flask](https://github.com/nickoala/telepot/blob/master/examples/webhook_flask_skeleton.py)**  
**[Message Counter + Flask](https://github.com/nickoala/telepot/blob/master/examples/webhook_flask_counter.py)**  
**[Async Skeleton + aiohttp](https://github.com/nickoala/telepot/blob/master/examples/webhook_aiohttp_skeletona.py)**  
**[Async Message Counter + aiohttp](https://github.com/nickoala/telepot/blob/master/examples/webhook_aiohttp_countera.py)**  
