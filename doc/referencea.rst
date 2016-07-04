telepot 8.2 reference (async version, Python 3.5+)
==================================================

A large part of async version simply mirrors the traditional version.
Main differences are:

- blocking methods become coroutines, and should be called with ``await``.
  (e.g. :meth:`telepot.aio.Bot.sendMessage`)
- delegation is achieved by tasks, instead of threads.

Basic Bot
---------

.. autoclass:: telepot.aio.Bot
   :members:

DelegatorBot
------------

.. autoclass:: telepot.aio.DelegatorBot

The meaning of a *seeder* is exactly the same as in :class:`telepot.DelegatorBot`.

A *delegator* is a function that:

- takes one argument - a (bot, message, seed) tuple. This is called a *seed tuple*.
- returns a *coroutine object* for the event loop to create a task of.

Refer to :class:`telepot.DelegatorBot` for remaining details.

``telepot.aio.delegate``
------------------------

.. automodule:: telepot.aio.delegate
   :members:

``telepot.aio.helper``
----------------------

.. autoclass:: telepot.aio.helper.Monitor
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:
   :member-order: groupwise

.. autoclass:: telepot.aio.helper.ChatHandler
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:
   :member-order: groupwise

.. autoclass:: telepot.aio.helper.UserHandler
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:
   :member-order: groupwise

.. autoclass:: telepot.aio.helper.InlineUserHandler
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:
   :member-order: groupwise

.. autoclass:: telepot.aio.helper.Timer
   :members:

.. autoclass:: telepot.aio.helper.Listener
   :show-inheritance:
   :members:
   :inherited-members:

.. autoclass:: telepot.aio.helper.Sender
   :members:

.. autoclass:: telepot.aio.helper.Administrator
   :members:

.. autoclass:: telepot.aio.helper.Editor
   :members:

.. autoclass:: telepot.aio.helper.Answerer
   :show-inheritance:
   :members:
   :inherited-members:

.. autoclass:: telepot.aio.helper.Router
   :members:

``telepot.aio.routing``
-----------------------

.. autofunction:: telepot.aio.routing.by_content_type

.. autofunction:: telepot.aio.routing.by_command

.. autofunction:: telepot.aio.routing.by_chat_command

.. autofunction:: telepot.aio.routing.by_text

.. autofunction:: telepot.aio.routing.by_data

.. autofunction:: telepot.aio.routing.by_regex

.. autofunction:: telepot.aio.routing.process_key

.. autofunction:: telepot.aio.routing.lower_key

.. autofunction:: telepot.aio.routing.upper_key

.. autofunction:: telepot.aio.routing.make_routing_table

.. autofunction:: telepot.aio.routing.make_content_type_routing_table
