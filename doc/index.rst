Introduction
============

.. toctree::
   :hidden:
   :maxdepth: 2

   reference

Telepot helps you build applications for `Telegram Bot API <https://core.telegram.org/bots>`_.
It works on Python 2.7 and Python 3. For Python 3.5+, it also has an `async version <#async-version-python-3-5>`_
based on `asyncio <https://docs.python.org/3/library/asyncio.html>`_.

For a time, I tried to list the features here like many projects do. Eventually, I gave up.

Common and straight-forward features are too trivial to worth listing.
For more unique and novel features, I cannot find standard terms to describe them.
The best way to experience telepot is by reading this page and going through the
`examples <https://github.com/nickoala/telepot/tree/master/examples>`_. Let's go.

.. contents::
    :local:

Installation
------------

pip::

    $ pip install telepot
    $ pip install telepot --upgrade  # UPGRADE

easy_install::

    $ easy_install telepot
    $ easy_install --upgrade telepot  # UPGRADE

Get a token
-----------

To use the `Telegram Bot API <https://core.telegram.org/bots/api>`_, you first
have to `get a bot account <http://www.instructables.com/id/Set-up-Telegram-Bot-on-Raspberry-Pi/>`_
by `chatting with BotFather <https://core.telegram.org/bots#6-botfather>`_.

BotFather will give you a **token**, something like ``123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ``.
With the token in hand, you can start using telepot to access the bot account.

Test the account
----------------

::

    >>> import telepot
    >>> bot = telepot.Bot('***** PUT YOUR TOKEN HERE *****')
    >>> bot.getMe()
    {'first_name': 'Your Bot', 'username': 'YourBot', 'id': 123456789}

Receive messages
----------------

Bots cannot initiate conversations with users. You have to send it a message first.
Get the message by calling :meth:`.Bot.getUpdates`::

    >>> from pprint import pprint
    >>> response = bot.getUpdates()
    >>> pprint(response)
    [{'message': {'chat': {'first_name': 'Nick',
                           'id': 999999999,
                           'type': 'private'},
                  'date': 1465283242,
                  'from': {'first_name': 'Nick', 'id': 999999999},
                  'message_id': 10772,
                  'text': 'Hello'},
      'update_id': 100000000}]

``999999999`` is obviously a fake id. ``Nick`` is my real name, though.

The ``chat`` field represents the conversation. Its ``type`` can be ``private``,
``group``, or ``channel`` (whose meanings should be obvious, I hope). Above,
``Nick`` just sent a ``private`` message to the bot.

According to Bot API, the method `getUpdates <https://core.telegram.org/bots/api#getupdates>`_
returns an array of `Update <https://core.telegram.org/bots/api#update>`_ objects.
As you can see, an Update object is nothing more than a Python dictionary.
In telepot, **Bot API objects are represented as dictionary.**

Note the ``update_id``. It is an ever-increasing number. Next time you should use
``getUpdates(offset=100000001)`` to avoid getting the same old messages over and over.
Giving an ``offset`` essentially acknowledges to the server that you have received
all ``update_id``\s lower than ``offset``::

    >>> bot.getUpdates(offset=100000001)
    []

An easier way to receive messages
---------------------------------

It is troublesome to keep checking messages while managing ``offset``. Let telepot
take care of the mundane stuff and notify you whenever new messages arrive::

    >>> from telepot.loop import MessageLoop
    >>> def handle(msg):
    ...     pprint(msg)
    ...
    >>> MessageLoop(bot, handle).run_as_thread()

After setting this up, send it a few messages. Sit back and monitor the
messages arriving.

Send a message
--------------

Sooner or later, your bot will want to send *you* messages. You should have
discovered your own user id from above interactions. I will keep using my
fake id of ``999999999``. Remember to substitute your own (real) id::

    >>> bot.sendMessage(999999999, 'Hey!')

Quickly ``glance`` a message
----------------------------

When processing a message, a few pieces of information are so central that you
almost always have to extract them. Use :func:`telepot.glance` to extract
"headline info". Try this skeleton, a bot which echoes what you said::

    import sys
    import time
    import telepot
    from telepot.loop import MessageLoop

    def handle(msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id)

        if content_type == 'text':
            bot.sendMessage(chat_id, msg['text'])

    TOKEN = sys.argv[1]  # get token from command-line

    bot = telepot.Bot(TOKEN)
    MessageLoop(bot, handle).run_as_thread()
    print ('Listening ...')

    # Keep the program running.
    while 1:
        time.sleep(10)

It is a good habit to always check ``content_type`` before further processing.
Do not assume every message is a ``text``.

Custom Keyboard and Inline Keyboard
-----------------------------------

Besides sending messages back and forth, Bot API allows richer interactions
with `custom keyboard <https://core.telegram.org/bots#keyboards>`_ and
`inline keyboard <https://core.telegram.org/bots#inline-keyboards-and-on-the-fly-updating>`_.
Both can be specified with the parameter ``reply_markup`` in :meth:`.Bot.sendMessage`.
The module :mod:`telepot.namedtuple` provides namedtuple classes for easier
construction of these keyboards.

Pressing a button on a *custom* keyboard results in a
`Message <https://core.telegram.org/bots/api#message>`_ object sent to the bot,
which is no different from a regular chat message composed by typing.

Pressing a button on an *inline* keyboard results in a
`CallbackQuery <https://core.telegram.org/bots/api#callbackquery>`_ object sent
to the bot, which we have to distinguish from a Message object.

Here comes the concept of **flavor**.

Message has a Flavor
--------------------

Regardless of the type of objects received, telepot generically calls them
"message" (with a lowercase "m"). A message's *flavor* depends on the
underlying object:

- a Message object gives the flavor ``chat``
- a CallbackQuery object gives the flavor ``callback_query``
- there are two more flavors, which you will come to shortly.

Use :func:`telepot.flavor` to check a message's flavor.

Here is a bot which does two things:

- When you send it a message, it gives you an inline keyboard.
- When you press a button on the inline keyboard, it says "Got it".

Pay attention to these things in the code:

- How I use namedtuple to construct
  an `InlineKeyboardMarkup <https://core.telegram.org/bots/api#inlinekeyboardmarkup>`_
  and an `InlineKeyboardButton <https://core.telegram.org/bots/api#inlinekeyboardbutton>`_
  object
- :func:`telepot.glance` works on any type of messages. Just give it the flavor.
- Use :meth:`.Bot.answerCallbackQuery` to react to callback query
- To *route* messages according to flavor, give a *routing table* to
  :class:`.MessageLoop`

.. literalinclude:: _code/inline_keyboard.py
   :emphasize-lines: 10,11,12,17,20,25,26

Inline Query
------------

So far, the bot has been operating in a chat - private, group, or channel.

In a private chat, Alice talks to Bot. Simple enough.

In a group chat, Alice, Bot, and Charlie share the same group. As the humans
gossip in the group, Bot hears selected messages (depending on whether in
`privacy mode <https://core.telegram.org/bots#privacy-mode>`_ or not) and may
chime in once in a while.

`Inline query <https://core.telegram.org/bots/inline>`_ is a totally different
mode of operations.

Imagine this. Alice wants to recommend a restaurant to Zach, but she can't remember the location
right off her head. *Inside the chat screen with Zach*, Alice types
``@Bot where is my favorite restaurant``, issuing an inline query to Bot, like
asking Bot a question. Bot gives back a list of answers; Alice can choose one of
them - as she taps on an answer, that answer is sent to Zach as a chat message.
In this case, Bot never takes part in the conversation. Instead, *Bot acts as
an assistant*, ready to give you talking materials. For every answer Alice chooses,
Bot gets notified with a *chosen inline result*.

To enable a bot to receive `InlineQuery <https://core.telegram.org/bots/api#inlinequery>`_,
you have to send a ``/setinline`` command to BotFather.
**An InlineQuery message gives the flavor** ``inline_query``.

To enable a bot to receive `ChosenInlineResult <https://core.telegram.org/bots/api#choseninlineresult>`_,
you have to send a ``/setinlinefeedback`` command to BotFather.
**A ChosenInlineResult message gives the flavor** ``chosen_inline_result``.

In this code sample, pay attention to these things:

- How I use namedtuple `InlineQueryResultArticle <https://core.telegram.org/bots/api#inlinequeryresultarticle>`_
  and `InputTextMessageContent <https://core.telegram.org/bots/api#inputtextmessagecontent>`_
  to construct an answer to inline query.

- Use :meth:`.Bot.answerInlineQuery` to send back answers

.. literalinclude:: _code/inline_query_simple.py
   :emphasize-lines: 11-15,19

However, this has a small problem. As you types and pauses,
types and pauses, types and pauses ... closely bunched inline queries arrive.
In fact, a new inline query often arrives *before* we finish processing a preceding one.
With only a single thread of execution, we can only process the closely bunched
inline queries sequentially. Ideally, whenever we see a new inline query coming from
the same user, it should override and cancel any preceding inline queries being processed
(that belong to the same user).

My solution is this. An :class:`.Answerer` takes an inline query, inspects its ``from`` ``id``
(the originating user id), and checks to see whether that user has an *unfinished* thread
processing a preceding inline query. If there is, the unfinished thread will be cancelled
before a new thread is spawned to process the latest inline query. In other words,
an :class:`.Answerer` ensures **at most one** active inline-query-processing thread per user.

:class:`.Answerer` also frees you from having to call :meth:`.Bot.answerInlineQuery` every time.
You supply it with a *compute function*. It takes that function's returned value and calls
:meth:`.Bot.answerInlineQuery` to send the results. Being accessible by multiple threads,
the compute function must be **thread-safe**.

.. literalinclude:: _code/inline_query_answerer.py
   :emphasize-lines: 22,31

Maintain Threads of Conversation
--------------------------------

So far, we have been using a single line of execution to handle messages.
That is adequate for simple programs. For more sophisticated programs where states need
to be maintained across messages, a better approach is needed.

Consider this scenario. A bot wants to have an intelligent conversation with a lot of users,
and if we could only use a single line of execution to handle messages (like what we have done so far),
we would have to maintain some state variables about each conversation *outside* the message-handling
function(s). On receiving each message, we first have to check whether the user already has a conversation
started, and if so, what we have been talking about. To avoid such mundaneness, we need a structured way
to maintain "threads" of conversation.

Let's look at my solution. Here, I implemented a bot that counts how many messages have been sent
by an individual user. If no message is received after 10 seconds, it starts over (timeout).
The counting is done *per chat* - that's the important point.

.. literalinclude:: _code/counter.py
   :emphasize-lines: 18-21

A :class:`.DelegatorBot` is able to spawn *delegates*. Above, it is spawning one ``MessageCounter``
*per chat id*.

Also noteworthy is :func:`.pave_event_space()`. To kill itself after 10 seconds
of inactivity, the delegate schedules a timeout event. For events to work, we
need to prepare an *event space*.

Detailed explanation of the delegation mechanism (e.g. how and when a ``MessageCounter`` is created, and why)
is beyond the scope here. Please refer to :class:`.DelegatorBot`.

Inline Handler per User
-----------------------

You may also want to answer inline query differently depending on user. When Alice asks Bot
"Where is my favorite restaurant?", Bot should give a different answer than when Charlie asks
the same question.

In the code sample below, pay attention to these things:

- :class:`.AnswererMixin` adds an :class:`.Answerer` instance to the object
- :func:`.per_inline_from_id` ensures one instance of :class:`QueryCounter` per originating user

.. literalinclude:: _code/inline_per_user.py
   :emphasize-lines: 8,31,41

Async Version (Python 3.5+)
---------------------------

Everything discussed so far assumes traditional Python. That is, network operations are blocking;
if you want to serve many users at the same time, some kind of threads are usually needed.
Another option is to use an asynchronous or event-driven framework, such as `Twisted <http://twistedmatrix.com/>`_.

Python 3.5+ has its own ``asyncio`` module. Telepot supports that, too.

Here is how to compile and install Python 3.6, if your O/S does not have it built in::

    $ sudo apt-get update
    $ sudo apt-get upgrade
    $ sudo apt-get install libssl-dev openssl libreadline-dev
    $ cd ~
    $ wget https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tgz
    $ tar zxf Python-3.6.1.tgz
    $ cd Python-3.6.1
    $ ./configure
    $ make
    $ sudo make install

Finally::

    $ pip3.6 install telepot

In case you are not familiar with asynchronous programming, let's start by learning about generators and coroutines:

- `'yield' and Generators Explained <https://www.jeffknupp.com/blog/2013/04/07/improve-your-python-yield-and-generators-explained/>`_
- `Sequences and Coroutines <http://wla.berkeley.edu/~cs61a/fa11/lectures/streams.html>`_

... why we want asynchronous programming:

- `Problem: Threads Are Bad <https://glyph.twistedmatrix.com/2014/02/unyielding.html>`_

... how generators and coroutines are applied to asynchronous programming:

- `Understanding Asynchronous IO <http://sahandsaba.com/understanding-asyncio-node-js-python-3-4.html>`_
- `A Curious Course on Coroutines and Concurrency <http://www.dabeaz.com/coroutines/>`_

... and how an asyncio program is generally structured:

- `The New asyncio Module in Python 3.4 <http://www.drdobbs.com/open-source/the-new-asyncio-module-in-python-34-even/240168401>`_
- `Event loop examples <https://docs.python.org/3/library/asyncio-eventloop.html#event-loop-examples>`_
- `HTTP server and client <http://aiohttp.readthedocs.org/en/stable/>`_

Telepot's async version basically mirrors the traditional version. Main differences are:

- blocking methods are now coroutines, and should be called with ``await``
- delegation is achieved by tasks, instead of threads

Because of that (and this is true of asynchronous Python in general), a lot of methods
will not work in the interactive Python interpreter like regular functions would.
They will have to be driven by an event loop.

Async version is under module :mod:`telepot.aio`. I duplicate the message counter example
below in async style:

- Substitute async version of relevant classes and functions
- Use ``async/await`` to perform asynchronous operations
- Use :meth:`.MessageLoop.run_forever` instead of :meth:`.run_as_thread`

.. literalinclude:: _code/countera.py
   :emphasize-lines: 4-5,7,12-14,24

`More Examples » <https://github.com/nickoala/telepot/tree/master/examples>`_
-----------------------------------------------------------------------------
