.. telepot documentation master file, created by
   sphinx-quickstart on Wed May 25 03:35:38 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

telepot 8.1 reference
=====================

Basic Bot
---------

The ``Bot`` class is mostly a wrapper around `Telegram Bot API <https://core.telegram.org/bots/api>`_.
Many of its methods are straight mappings to Bot API methods. Where appropriate,
I will only give links below. No point to duplicate all the details.

.. autoclass:: telepot.Bot
   :members:

Functions
---------

.. autofunction:: telepot.flavor
.. autofunction:: telepot.glance
.. autofunction:: telepot.flance
.. autofunction:: telepot.message_identifier

DelegatorBot
------------

.. autoclass:: telepot.DelegatorBot

``telepot.delegate``
++++++++++++++++++++

.. autofunction:: telepot.delegate.per_chat_id

``telepot.helper``
++++++++++++++++++

.. autoclass:: telepot.helper.ChatHandler

Other Helpers
-------------

Exceptions
----------

.. automodule:: telepot.exception
   :members:
   :undoc-members:

.. autoclass:: telepot.exception.TelegramError
   :members:

Namedtuples
-----------

Routing
-------

``Router``
++++++++++


``telepot.routing``
+++++++++++++++++++

Low-level HTTP
--------------
