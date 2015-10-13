# telepot

**P**ython framework for **Tele**gram B**ot** API

**[What's New in 3.0?](#whatsnew)**  
**[Installation](#installation)**  
**[The Basics](#basics)**  
**[The Advanced](#advanced)**  
**[The Async Stuff](#async)** (Python 3.4.3 or newer)  
**[Reference](https://github.com/nickoala/telepot/blob/master/REFERENCE.md)**  
**[Examples](#examples)**  
**[Mailing List](https://groups.google.com/forum/#!forum/telepot)**

### Recent changes

**3.2 (2015-10-13)**

- Conforms to latest Telegram Bot API as of [October 8, 2015](https://core.telegram.org/bots/api-changelog)
- Added `Chat` class, removed `GroupChat`
- Added `glance2()`

**3.1 (2015-10-08)**

- Added `per_chat_id_except()`
- Added lock to `Microphone`, make it thread-safe

**3.0 (2015-10-05)**

- Added listener and delegation mechanism

**[Go to full changelog »](https://github.com/nickoala/telepot/blob/master/CHANGELOG.md)**

<a id="whatsnew"></a>
## What's New in 3.0?

The job done by telepot so far has been quite trivial, nothing more than adding a thin layer of Python on top of the Bot API. I have been calling it a *wrapper*.

In 3.0, telepot has grown up to be more appropriately called a *framework*. I have introduced some useful features that support writing more sophisticated programs. While I don't have time to say more right now, **more documentations are definitely coming**.

The code has been uploaded. Feel free to look at the [guess-a-number](https://github.com/nickoala/telepot/blob/master/examples/guess.py) and [chatbox](https://github.com/nickoala/telepot/blob/master/examples/chatbox_nodb.py) examples, both of which make use of the new features.

<a id="installation"></a>
## Installation

Telepot has been tested on **Python 2.7 - 3.4**, running **Raspbian**.

`sudo apt-get install python-pip` to install the Python package manager.

`sudo pip install telepot` to install the telepot library.

`sudo pip install telepot --upgrade` to upgrade.

<a id="basics"></a>
## The Basics

To use the [Telegram Bot API](https://core.telegram.org/bots/api), you first have to [get a **bot account**](http://www.instructables.com/id/Set-up-Telegram-Bot-on-Raspberry-Pi/) by [chatting with the BotFather](https://core.telegram.org/bots).

He will then give you a **token**, something like `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`. With the token in hand, you can start using telepot to access the bot account.

Instructions below are presented in Python 2.7

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

If the message is from a private chat, `from` and `chat` are the same party (like above). If the message is from a group chat, `from` means the original sender and `chat` means the group. (Bots do not receive all messages in a group chat; see [Privacy mode](https://core.telegram.org/bots#privacy-mode) for details) **A negative `chat` `id` indicates a group; a positive `chat` `id` indicates a user (that is, a private chat).**

Note the `update_id`. It is an ever-increasing number. Next time you should use `getUpdates(offset=100000001)` to avoid getting the same old messages over and over. Giving an `offset` essentially acknowledges to the server that you have received all `update_id`s lower than `offset`.

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

In fact, below can be a skeleton for a lot of telepot programs:

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

#### Quickly `glance()` a message

When processing a message, a few pieces of information are so central that you almost always have to extract them.

*Since 1.2*, you may extract a tuple of `(type, message['from']['id'], message['chat']['id'])` of a `message` by calling `telepot.glance(message)`.

The `type` of a message can be: `text`, `voice`, `sticker`, `photo`, `audio`, `document`, `video`, `contact`, `location`, `new_chat_participant`, `left_chat_participant`, `new_chat_title`, `new_chat_photo`, `delete_chat_photo`, `group_chat_created`.

It is a good habit to always check the `type` before further processing. Do not assume every message is a `text` message.

A better skeleton would look like:

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

#### Download files

For a `voice`, `sticker`, `photo`, `audio`, `document`, or `video` message, look for the `file_id` and you may download the file. For example, a `photo` may look like this:

```python
{u'chat': {u'first_name': u'Nick', u'id': 999999999},
 u'date': 1442905828,
 u'from': {u'first_name': u'Nick', u'id': 999999999},
 u'message_id': 2007,
 u'photo': [{u'file_id': u'ABcdEfGhijkLm_NopQRstuvxyZabcdEFgHIJklJAkimnoPQrsTuvWxyz',
             u'file_size': 615,
             u'height': 67,
             u'width': 90},
            {u'file_id': u'ABcdEfGhijkLm_NopQRstuvxyZabcdEFgHIJklkodamnoPQrsTuvWxyz',
             u'file_size': 4990,
             u'height': 240,
             u'width': 320},
            {u'file_id': u'ABcdEfGhijkLm_NopQRstuvxyZabcdEFgHIJklYAGAmnoPQrsTuvWxyz',
             u'file_size': 34506,
             u'height': 600,
             u'width': 800},
            {u'file_id': u'ABcdEfGhijkLm_NopQRstuvxyZabcdEFgHIJklujGamnoPQrsTuvWxyz',
             u'file_size': 73196,
             u'height': 960,
             u'width': 1280}]}
```

It has a number of `file_id`s, with various file sizes. These are thumbnails of the same image. Download one of them by:

```python
>>> bot.downloadFile(u'ABcdEfGhijkLm_NopQRstuvxyZabcdEFgHIJklJAkimnoPQrsTuvWxyz', 'save/to/path')
```

#### Turn dictionary into namedtuple, if you like

In telepot, everything is a dict. For example, a `message` is a dict whose **keys** are just **field names** specified in Bot API's **[Message](https://core.telegram.org/bots/api#message)** object. Accessing `message['from']`, you get another dict whose **keys** are just **field names** specified in Bot API's **[User](https://core.telegram.org/bots/api#user)** object. In fact, all objects returned by Bot API are serialized as JSON associative arrays. Turning those into Python dicts is not just easy, but natural. I like the transparency.

However, accessing them "like an object" does have some benefits:

- It is easier to write `msg.chat.id` than to write `msg['chat']['id']`
- If you want to read an optional `field` in a `dict`, since it may be absent, you always have to check whether `'field' in dict` before accessing `dict['field']` (unless you don't mind catching an exception). Using an "object", you can access `object.field` regardless, because an absent field will just give a value of `None`.

To implement object-like behaviours, I use **namedtuple**. *Since 1.2*, you may convert a dict into a namedtuple of a given object type by calling `telepot.namedtuple(dict, object)`.

For example, to convert a `message` dict into a namedtuple, you do:

```python
m = telepot.namedtuple(message, 'Message')

print m.chat.id  # == message['chat']['id']
print m.text   # just print 'None' if no text
```

There is one annoyance, though. Namedtuple field names cannot be Python keywords, but the **[Message](https://core.telegram.org/bots/api#message)** object has a `from` field, which is a Python keyword. I choose to append an underscore to it. That is, the dictionary value `message['from']` becomes `m.from_` when converted to a namedtuple:

```python
print m.from_.id  # == message['from']['id']
```

**What if Bot API adds new fields to objects in the future? Would that break the namedtuple() conversion?**

Well, that would break telepot 1.2. **I fixed that in 1.3**. Since 1.3, unexpected fields in data would cause a warning (that reminds you to upgrade the telepot library), but would not crash the program. **Users of 1.2 are recommended to upgrade.**

`namedtuple()` is just a convenience function. The underlying dictionary is always there for your consumption.

#### Send messages

Enough about receiving messages. Sooner or later, your bot would want to send *you* messages. You should have discovered your own user ID from above interactions. I will keeping using my fake ID of `999999999`. Remember to substitute your own (real) user ID.

```python
>>> bot.sendMessage(999999999, 'I am fine')
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
>>> bot.sendPhoto(999999999, u'APNpmPKVulsdkIFAILMDmhTAADmdcmdsdfaldalk')
```

Besides `sendPhoto()`, you may also `sendAudio()`, `sendDocument()`, `sendSticker()`, `sendVideo()`, and `sendVoice()`. See [reference](https://github.com/nickoala/telepot/blob/master/REFERENCE.md) for details.

**[Read the reference »](https://github.com/nickoala/telepot/blob/master/REFERENCE.md)**

<a id="advanced"></a>
## The Advanced

Having a single message-handling function is adequate for simple programs. For more sophisticated programs where states need to be maintained across messages, a single message-handling function may still do the job, but is probably not ideal.

For example, if a bot wants to have an intelligent conversation with a lot of users, and if we could only use a single message-handling function, we would have to maintain some state variables about each conversation *outside* the message-handling function. On receiving each message, we first have to check whether the user already has a conversation initiated, and if so, what we have been talking about. Implementing this type of behaviour calls for something beyond a single message-handler.

Let's look at my solution. Here, I implement a bot that counts how many messages a user has sent it:

```python
import sys
import telepot
from telepot.delegate import create_run

class MessageCounter(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple):
        super(MessageCounter, self).__init__(*seed_tuple)
        self.listener.timeout = 10

    def run(self):
        count = 1
        self.sender.sendMessage(count)

        while 1:
            msg = self.listener.wait(chat__id=self.chat_id)
            count += 1
            self.sender.sendMessage(count)


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.DelegatorBot(TOKEN, [
    (lambda msg: msg['chat']['id'], create_run(MessageCounter)),
])
bot.notifyOnMessage(run_forever=True)
```

Let me explain. First, note that `MessageCounter` is a subclass of `telepot.helper.ChatHandler`. The idea of `ChatHandler` is that it is "responsible" for a certain chat, like a telephone support person is "responsible" for interacting with a certain customer. `ChatHandler` exposes a bunch of very useful properties:

- `listener` - used to wait for certain messages. Above, it is used to suspend execution until next message from the same user arrives.
- `sender` - used to send messages to user. A proxy to `bot.sendZZZ()` methods, it saves you having to supply `chat_id` every time.
- `chat_id` - the target chat
- `bot` - the parent bot 
- `initial_message` - the message that initiated this chat

Pay attention to the method, `listener.wait()`. It blocks until a "specified" message is encountered, as determined by the arguments. Waiting for messages from the same chat is almost a necessity, but it can wait for anything by giving the appropriate arguments. See **[reference](https://github.com/nickoala/telepot/blob/master/REFERENCE.md)** for details.

How is a `MessageCounter` spawned? Is it a thread? Let's look at the bottom part of the code:

```python
bot = telepot.DelegatorBot(TOKEN, [
    (lambda msg: msg['chat']['id'], create_run(MessageCounter)),
])
```

`DelegatorBot` decides when to "delegate" to a `MessageCounter`. This line:

```python
    (lambda msg: msg['chat']['id'], create_run(MessageCounter)),
```

essentially says, for each chat id, create a `MessageCounter` object and spawn a thread around its `run()` method.

Technically, I call the first element *seed_calculating_function*, and the second element *delegate_producing_function*.

- *seed_calculating_function* takes one argument (the message just received by the bot), and returns a *seed*. The bot will check whether the seed is already associated with a delegate. If no such delegate exists, of if that delegate is no longer alive, the *delegate_producing_function* is invoked. And the new delegate will be associated with the seed.

- *delegate_producing_function* takes one argument (a tuple of `(bot, msg, seed)`), and returns one of the following:
  - an object that has a `start()` and `is_alive()` method. Therefore, a `threading.Thread` object is a natural delegate. Once the `object` is obtained, `object.start()` is called.
  - a `function`. In this case, it is wrapped by a `Thread(target=function)` and started.
  - a tuple of `(func, args, kwargs)`. In this case, it is wrapped by a `Thread(target=func, args=args, kwargs=kwargs)` and started.

In case you are wondering, `create_run` above is actually a function that returns a *delegate_producing_function* that returns another function (a `MessageCounter` object's `run` method).

If you want your own implementation of threads or another form of delegation entirely unrelated to threads, you can always wrap it around the `create_run()` function. The **[Chatbox example](#chatbox)** demonstrates this technique. Remember, if *delegate_producing_function* returns an object, it is only required to have a `start()` and `is_alive()` method, not necessarily a thread.

I hope this architecture makes harder programs easier. Thanks to **[Django](https://www.djangoproject.com/)** and **[Tornado](http://www.tornadoweb.org/)** for inspirations.

**[Read the reference »](https://github.com/nickoala/telepot/blob/master/REFERENCE.md)**

<a id="async"></a>
## The Async Stuff (Python 3.4.3 or newer)

*Since 2.0*, I introduced an async version of `Bot` that makes use of the `asyncio` module of **Python 3.4.3**. All async stuff described in this section would not work on earlier versions of Python.

Raspbian does not come with Python 3.4. You have to compile it yourself.

```
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get install libssl-dev openssl
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

#### Create an async `Bot`

```python
import telepot.async
bot = telepot.async.Bot('TOKEN')
```

#### An async skeleton

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

loop.create_task(bot.messageLoop(handle))  # kind of like notifyOnMessage()
print('Listening ...')

loop.run_forever()
```

Note the (superficial) similarities with the traditional skeleton, although the underlying concepts are quite different.

#### Send asynchronously

The async `Bot` has all the `sendZZZ()` methods seen in the traditional `Bot`. Unlike the traditional, however, these methods are now **coroutines**, and will not work in the interactive python interpreter like regular functions would. They will have to be driven by an event loop.

Supply the bot token and your own user ID on the command-line:

```python
import sys
import asyncio
import telepot.async

@asyncio.coroutine
def textme():
    print('Sending a text ...')
    yield from bot.sendMessage(USER_ID, 'Good morning!')


TOKEN = sys.argv[1]         # get token from command-line
USER_ID = int(sys.argv[2])  # get user id from command-line

bot = telepot.async.Bot(TOKEN)

loop = asyncio.get_event_loop()
loop.run_until_complete(textme())
print('Done.')
```

**[Read the reference »](https://github.com/nickoala/telepot/blob/master/REFERENCE.md)**

<a id="examples"></a>
## Examples

#### Dicey Clock

[Here is a tutorial](http://www.instructables.com/id/Set-up-Telegram-Bot-on-Raspberry-Pi/) teaching you how to setup a bot on Raspberry Pi. This simple bot does nothing much but accepts two commands:

- `/roll` - reply with a random integer between 1 and 6, like rolling a dice.
- `/time` - reply with the current time, like a clock.

**[Source »](https://github.com/nickoala/telepot/blob/master/examples/diceyclock.py)**

#### Skeleton

A starting point for your telepot programs.

**[Traditional version »](https://github.com/nickoala/telepot/blob/master/examples/skeleton.py)**   
**[Async version »](https://github.com/nickoala/telepot/blob/master/examples/skeletona.py)**

#### Indoor climate monitor

Running on a Raspberry Pi with a few sensors attached, this bot accepts these commands:

- `/now` - Report current temperature, humidity, and pressure
- `/1m` - Report every 1 minute
- `/1h` - Report every 1 hour
- `/cancel` - Cancel reporting

**[Source »](https://github.com/nickoala/sensor/blob/master/examples/indoor.py)**

#### IP Cam using Telegram as DDNS

Running on a Raspberry Pi with a camera module attached, this bot accepts these commands:

- `/open` - Open a port through the router to make the video stream accessible, and send you the URL (which includes the router's public IP address)
- `/close` - Close the port

**[Project page »](https://github.com/nickoala/ipcam)**

#### Emodi - an Emoji Unicode Decoder

Sooner or later, you want your bots to be able to send emoji. You may look up the unicode on the web, or from now on, you may just fire up Telegram and ask **[Emodi :blush:](https://telegram.me/emodibot)**

**[Traditional version »](https://github.com/nickoala/telepot/blob/master/examples/emodi.py)**  
**[Async version »](https://github.com/nickoala/telepot/blob/master/examples/emodia.py)**

I am running this bot on a CentOS server. You should be able to talk to it 24/7. Intended for multiple users, the async version is being run.

By the way, I just discovered a Python **[emoji](https://pypi.python.org/pypi/emoji/)** package. Use it.

<a id="guess-a-number"></a>
#### Guess-a-number

1. The bot randomly picks an integer between 0-100. 
2. You make a guess. 
3. The bot tells you to go higher or lower.
4. Repeat step 2 and 3, until guess is correct.

This example is able to serve many players at once. It illustrates the use of `DelegateBot` and how to subclass from `ChatHandler`, two very useful techniques beyond simple programs.

**[Traditional version »](https://github.com/nickoala/telepot/blob/master/examples/guess.py)**  
**[Async version »](https://github.com/nickoala/telepot/blob/master/examples/guessa.py)**

<a id="chatbox"></a>
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
