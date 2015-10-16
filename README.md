# telepot - a Python framework for Telegram Bot API

**[Installation](#installation)**  
**[The Basics](#basics)**  
**[The Intermediate](#intermediate)**  
**[The Advanced](#advanced)**  
**[Async Version](#async)** (Python 3.4.3 or newer)  
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

------

Because things are rapidly evolving, instead of sprinkling "since version N.n" all over the place, **all documentations aim at the latest version.**

If you are an existing user, don't worry. Most of the changes are backward-compatible. Where changes are needed in your code, they should not be hard to fix. Feel free to bug me at **lee1nick@yahoo.ca**

Telepot has been tested on **Raspbian** and **CentOS**, using **Python 2.7 - 3.4**. Below discussions are based on Raspbian and Python 2.7, except noted otherwise.

<a id="installation"></a>
## Installation

`sudo apt-get install python-pip` to install the Python package manager.

`sudo pip install telepot` to install the telepot library.

`sudo pip install telepot --upgrade` to upgrade.

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

It is a good habit to always check the *content_type* before further processing. Do not assume every message is a `text` message.

*The old `glance()` function should not be used anymore. It relies on the `from` field, which becomes optional in the latest Bot API. The new `glance2()` will supercede it eventually. I keep it for now to maintain backward-compatibility.*

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

Noteworthy are two classes: `DelegatorBot` and `ChatHandler`. Let me explain one by one.

#### `DelegatorBot`

It is a subclass of `Bot`, with the newfound ability to spawn *delegates*. Its constructor takes a list of tuples telling it when and how to spawn delegates. This line:

```python
    (lambda msg: msg['chat']['id'], create_run(MessageCounter)),
```

essentially says, **for each chat id, create a `MessageCounter` object and spawn a thread around its `run` method.**

Technically, I call the tuple's first element *seed_calculating_function*, and the second element *delegate_producing_function*.

- *seed_calculating_function* takes one argument (the message just received by the bot), and returns a *seed*. The bot will check whether the seed is already associated with a delegate. If no such delegate exists, or if that delegate is no longer alive, the *delegate_producing_function* is invoked. And the new delegate will be associated with the seed.

  In the above example, the seed is the chat id. If no `MessageCounter` is currently associated this chat id, a new one will be spawned. When next message from the same chat id arrives, the bot sees that a `MessageCounter` already exists (assuming still alive) and does nothing.

- *delegate_producing_function* takes one argument (a tuple of *(bot, message, seed)*), and returns one of the following:
  - an object that has a `start()` and `is_alive()` method. Therefore, a `threading.Thread` object is a natural delegate. Once the `object` is obtained, `object.start()` is called.
  - a `function`. In this case, it is wrapped by a `Thread(target=function)` and started.
  - a tuple of `(func, args, kwargs)`. In this case, it is wrapped by a `Thread(target=func, args=args, kwargs=kwargs)` and started.

  In case you are wondering, `create_run` above is actually a function that returns a *delegate_producing_function* that returns another function (a `MessageCounter` object's `run` method).

If you want your own implementation of threads or another form of delegation entirely unrelated to threads, you can always wrap it around the `create_run()` call. The **[Chatbox example](#chatbox)** demonstrates this technique. Remember, if *delegate_producing_function* returns an object, it is only required to have a `start()` and `is_alive()` method, not necessarily a thread.

#### `MessageCounter` and its superclass, `ChatHandler`

The idea of a `ChatHandler` is that it is "the one talking to the user", like a telephone support person talking to a customer. It bares the full responsibility of making that customer happy. In order to fulfill that role, it is equipped with a powerful set of properties:

- `listener` - used to wait for certain messages. Above, it is used to suspend execution until next message from the same chat arrives.
- `sender` - used to send messages to user. A proxy to `bot.sendZZZ()` methods, it saves you having to supply `chat_id` every time.
- `chat_id` - the target chat
- `bot` - the parent bot 
- `initial_message` - the message that initiated this chat

`listener.wait()` blocks until a "specific" message is encountered, as determined by the arguments. Waiting for messages from the same chat is almost always a necessity, but it can wait for anything by giving the appropriate arguments. See **[reference](https://github.com/nickoala/telepot/blob/master/REFERENCE.md)** for details.

I hope this architecture makes harder programs easier. Thanks to **[Django](https://www.djangoproject.com/)** and **[Tornado](http://www.tornadoweb.org/)** for inspirations.

**[Read the reference »](https://github.com/nickoala/telepot/blob/master/REFERENCE.md)**

<a id="async"></a>
## Async Version (Python 3.4.3 or newer)

Everything discussed so far assumes traditional Python. That is, network operations are blocking; if you want to serve many users at the same time, some kind of threads are usually needed. Another option is to use an asynchronous or event-driven framework, such as [Twisted](http://twistedmatrix.com/).

Python 3.4 introduces its own asynchronous architecture, the `asyncio` module. Telepot supports that, too. If your bot is to serve many people, I strongly recommend doing it asynchronously. Threads, in my opinion, is a thing of yesteryears.

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

#### How about `DelegatorBot`?

Again, it is very similar to the traditional version. Please refer to the examples: **[Guess-a-number](#guess-a-number)**, and **[Chatbox](#chatbox)**.

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

**[Traditional version 1 »](https://github.com/nickoala/telepot/blob/master/examples/skeleton.py)**   
**[Traditional version 2 »](https://github.com/nickoala/telepot/blob/master/examples/skeleton_extend.py)**   
**[Async version 1 »](https://github.com/nickoala/telepot/blob/master/examples/skeletona.py)**  
**[Async version 2 »](https://github.com/nickoala/telepot/blob/master/examples/skeletona_extend.py)**

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

#### Message Counter

Count number of messages a user has sent the bot. It illustrates the basic use of `DelegateBot` and `ChatHandler`.

**[Source »](https://github.com/nickoala/telepot/blob/master/examples/counter.py)**  

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
