import time
import traceback
import threading
import logging
import collections
import re
import inspect
from functools import partial
from . import filtering, exception
from . import (
    flavor, chat_flavors, inline_flavors, is_event,
    message_identifier, origin_identifier)

try:
    import Queue as queue
except ImportError:
    import queue


class Microphone(object):
    def __init__(self):
        self._queues = set()
        self._lock = threading.Lock()

    def _locked(func):
        def k(self, *args, **kwargs):
            with self._lock:
                return func(self, *args, **kwargs)
        return k

    @_locked
    def add(self, q):
        self._queues.add(q)

    @_locked
    def remove(self, q):
        self._queues.remove(q)

    @_locked
    def send(self, msg):
        for q in self._queues:
            try:
                q.put_nowait(msg)
            except queue.Full:
                traceback.print_exc()


class Listener(object):
    def __init__(self, mic, q):
        self._mic = mic
        self._queue = q
        self._patterns = []

    def __del__(self):
        self._mic.remove(self._queue)

    def capture(self, pattern):
        """
        Add a pattern to capture.

        :param pattern: a list of templates.

        A template may be a function that:
            - takes one argument - a message
            - returns ``True`` to indicate a match

        A template may also be a dictionary whose:
            - **keys** are used to *select* parts of message. Can be strings or
              regular expressions (as obtained by ``re.compile()``)
            - **values** are used to match against the selected parts. Can be
              typical data or a function.

        All templates must produce a match for a message to be considered a match.
        """
        self._patterns.append(pattern)

    def wait(self):
        """
        Block until a matched message appears.
        """
        if not self._patterns:
            raise RuntimeError('Listener has nothing to capture')

        while 1:
            msg = self._queue.get(block=True)

            if any(map(lambda p: filtering.match_all(msg, p), self._patterns)):
                return msg


class Sender(object):
    """
    When you are dealing with a particular chat, it is tedious to have to supply
    the same ``chat_id`` every time to send a message, or to send anything.

    This object is a proxy to a bot's ``send*`` and ``forwardMessage`` methods,
    automatically fills in a fixed chat id for you. Available methods have
    identical signatures as those of the underlying bot, **except there is no need
    to supply the aforementioned** ``chat_id``:

    - :meth:`.Bot.sendMessage`
    - :meth:`.Bot.forwardMessage`
    - :meth:`.Bot.sendPhoto`
    - :meth:`.Bot.sendAudio`
    - :meth:`.Bot.sendDocument`
    - :meth:`.Bot.sendSticker`
    - :meth:`.Bot.sendVideo`
    - :meth:`.Bot.sendVoice`
    - :meth:`.Bot.sendLocation`
    - :meth:`.Bot.sendVenue`
    - :meth:`.Bot.sendContact`
    - :meth:`.Bot.sendGame`
    - :meth:`.Bot.sendChatAction`
    """

    def __init__(self, bot, chat_id):
        for method in ['sendMessage',
                       'forwardMessage',
                       'sendPhoto',
                       'sendAudio',
                       'sendDocument',
                       'sendSticker',
                       'sendVideo',
                       'sendVoice',
                       'sendLocation',
                       'sendVenue',
                       'sendContact',
                       'sendGame',
                       'sendChatAction',]:
            setattr(self, method, partial(getattr(bot, method), chat_id))
            # Essentially doing:
            #   self.sendMessage = partial(bot.sendMessage, chat_id)


class Administrator(object):
    """
    When you are dealing with a particular chat, it is tedious to have to supply
    the same ``chat_id`` every time to get a chat's info or to perform administrative
    tasks.

    This object is a proxy to a bot's chat administration methods,
    automatically fills in a fixed chat id for you. Available methods have
    identical signatures as those of the underlying bot, **except there is no need
    to supply the aforementioned** ``chat_id``:

    - :meth:`.Bot.kickChatMember`
    - :meth:`.Bot.leaveChat`
    - :meth:`.Bot.unbanChatMember`
    - :meth:`.Bot.getChat`
    - :meth:`.Bot.getChatAdministrators`
    - :meth:`.Bot.getChatMembersCount`
    - :meth:`.Bot.getChatMember`
    """

    def __init__(self, bot, chat_id):
        for method in ['kickChatMember',
                       'leaveChat',
                       'unbanChatMember',
                       'getChat',
                       'getChatAdministrators',
                       'getChatMembersCount',
                       'getChatMember',]:
            setattr(self, method, partial(getattr(bot, method), chat_id))


class Editor(object):
    """
    If you want to edit a message over and over, it is tedious to have to supply
    the same ``msg_identifier`` every time.

    This object is a proxy to a bot's message-editing methods, automatically fills
    in a fixed message identifier for you. Available methods have
    identical signatures as those of the underlying bot, **except there is no need
    to supply the aforementioned** ``msg_identifier``:

    - :meth:`.Bot.editMessageText`
    - :meth:`.Bot.editMessageCaption`
    - :meth:`.Bot.editMessageReplyMarkup`

    A message's identifier can be easily extracted with :func:`telepot.message_identifier`.
    """

    def __init__(self, bot, msg_identifier):
        """
        :param msg_identifier:
            a message identifier as mentioned above, or a message (whose
            identifier will be automatically extracted).
        """
        # Accept dict as argument. Maybe expand this convenience to other cases in future.
        if isinstance(msg_identifier, dict):
            msg_identifier = message_identifier(msg_identifier)

        for method in ['editMessageText',
                       'editMessageCaption',
                       'editMessageReplyMarkup',]:
            setattr(self, method, partial(getattr(bot, method), msg_identifier))


class Answerer(object):
    """
    When processing inline queries, ensure **at most one active thread** per user id.
    """

    def __init__(self, bot):
        self._bot = bot
        self._workers = {}  # map: user id --> worker thread
        self._lock = threading.Lock()  # control access to `self._workers`

    def answer(outerself, inline_query, compute_fn, *compute_args, **compute_kwargs):
        """
        Spawns a thread that calls ``compute fn`` (along with additional arguments
        ``*compute_args`` and ``**compute_kwargs``), then applies the returned value to
        :meth:`.Bot.answerInlineQuery` to answer the inline query.
        If a preceding thread is already working for a user, that thread is cancelled,
        thus ensuring at most one active thread per user id.

        :param inline_query:
            The inline query to be processed. The originating user is inferred from ``msg['from']['id']``.

        :param compute_fn:
            A **thread-safe** function whose returned value is given to :meth:`.Bot.answerInlineQuery` to send.
            May return:

            - a *list* of `InlineQueryResult <https://core.telegram.org/bots/api#inlinequeryresult>`_
            - a *tuple* whose first element is a list of `InlineQueryResult <https://core.telegram.org/bots/api#inlinequeryresult>`_,
              followed by positional arguments to be supplied to :meth:`.Bot.answerInlineQuery`
            - a *dictionary* representing keyword arguments to be supplied to :meth:`.Bot.answerInlineQuery`

        :param \*compute_args: positional arguments to ``compute_fn``
        :param \*\*compute_kwargs: keyword arguments to ``compute_fn``
        """

        from_id = inline_query['from']['id']

        class Worker(threading.Thread):
            def __init__(innerself):
                super(Worker, innerself).__init__()
                innerself._cancelled = False

            def cancel(innerself):
                innerself._cancelled = True

            def run(innerself):
                try:
                    query_id = inline_query['id']

                    if innerself._cancelled:
                        return

                    # Important: compute function must be thread-safe.
                    ans = compute_fn(*compute_args, **compute_kwargs)

                    if innerself._cancelled:
                        return

                    if isinstance(ans, list):
                        outerself._bot.answerInlineQuery(query_id, ans)
                    elif isinstance(ans, tuple):
                        outerself._bot.answerInlineQuery(query_id, *ans)
                    elif isinstance(ans, dict):
                        outerself._bot.answerInlineQuery(query_id, **ans)
                    else:
                        raise ValueError('Invalid answer format')
                finally:
                    with outerself._lock:
                        # Delete only if I have NOT been cancelled.
                        if not innerself._cancelled:
                            del outerself._workers[from_id]

                        # If I have been cancelled, that position in `outerself._workers`
                        # no longer belongs to me. I should not delete that key.

        # Several threads may access `outerself._workers`. Use `outerself._lock` to protect.
        with outerself._lock:
            if from_id in outerself._workers:
                outerself._workers[from_id].cancel()

            outerself._workers[from_id] = Worker()
            outerself._workers[from_id].start()


class AnswererMixin(object):
    """
    Install an :class:`.Answerer` to handle inline query.
    """
    Answerer = Answerer  # let subclass customize Answerer class

    def __init__(self, *args, **kwargs):
        self._answerer = self.Answerer(self.bot)
        super(AnswererMixin, self).__init__(*args, **kwargs)

    @property
    def answerer(self):
        return self._answerer


class CallbackQueryCoordinator(object):
    def __init__(self, id, origin_set, enable_chat, enable_inline):
        """
        :param origin_set:
            Callback query whose origin belongs to this set will be captured

        :param enable_chat:
            - ``False``: Do not intercept *chat-originated* callback query
            - ``True``: Do intercept
            - Notifier function: Do intercept and call the notifier function
              on adding or removing an origin

        :param enable_inline:
            Same meaning as ``enable_chat``, but apply to *inline-originated*
            callback query

        Notifier functions should have the signature ``notifier(origin, id, adding)``:

        - On adding an origin, ``notifier(origin, my_id, True)`` will be called.
        - On removing an origin, ``notifier(origin, my_id, False)`` will be called.
        """
        self._id = id
        self._origin_set = origin_set

        def dissolve(enable):
            if not enable:
                return False, None
            elif enable is True:
                return True, None
            elif callable(enable):
                return True, enable
            else:
                raise ValueError()

        self._enable_chat, self._chat_notify = dissolve(enable_chat)
        self._enable_inline, self._inline_notify = dissolve(enable_inline)

    def configure(self, listener):
        """
        Configure a :class:`.Listener` to capture callback query
        """
        listener.capture([
            lambda msg: flavor(msg) == 'callback_query',
            {'message': self._chat_origin_included}
        ])

        listener.capture([
            lambda msg: flavor(msg) == 'callback_query',
            {'inline_message_id': self._inline_origin_included}
        ])

    def _chat_origin_included(self, msg):
        try:
            return (msg['chat']['id'], msg['message_id']) in self._origin_set
        except KeyError:
            return False

    def _inline_origin_included(self, inline_message_id):
        return (inline_message_id,) in self._origin_set

    def _rectify(self, msg_identifier):
        if isinstance(msg_identifier, tuple):
            if len(msg_identifier) == 2:
                return msg_identifier, self._chat_notify
            elif len(msg_identifier) == 1:
                return msg_identifier, self._inline_notify
            else:
                raise ValueError()
        else:
            return (msg_identifier,), self._inline_notify

    def capture_origin(self, msg_identifier, notify=True):
        msg_identifier, notifier = self._rectify(msg_identifier)
        self._origin_set.add(msg_identifier)
        notify and notifier and notifier(msg_identifier, self._id, True)

    def uncapture_origin(self, msg_identifier, notify=True):
        msg_identifier, notifier = self._rectify(msg_identifier)
        self._origin_set.discard(msg_identifier)
        notify and notifier and notifier(msg_identifier, self._id, False)

    def _contains_callback_data(self, message_kw):
        def contains(obj, key):
            if isinstance(obj, dict):
                return key in obj
            else:
                return hasattr(obj, key)

        if contains(message_kw, 'reply_markup'):
            reply_markup = filtering.pick(message_kw, 'reply_markup')
            if contains(reply_markup, 'inline_keyboard'):
                inline_keyboard = filtering.pick(reply_markup, 'inline_keyboard')
                for array in inline_keyboard:
                    if any(filter(lambda button: contains(button, 'callback_data'), array)):
                        return True
        return False

    def augment_send(self, send_func):
        """
        :param send_func:
            functions that send messages, such as :meth:`.Bot.send\*`

        :return:
            a function that wraps around ``send_func`` and examines whether the
            sent message contains an inline keyboard with callback data. If so,
            future callback query originating from the sent message will be captured.
        """
        def augmented(*aa, **kw):
            sent = send_func(*aa, **kw)

            if self._enable_chat and self._contains_callback_data(kw):
                self.capture_origin(message_identifier(sent))

            return sent
        return augmented

    def augment_edit(self, edit_func):
        """
        :param edit_func:
            functions that edit messages, such as :meth:`.Bot.edit*`

        :return:
            a function that wraps around ``edit_func`` and examines whether the
            edited message contains an inline keyboard with callback data. If so,
            future callback query originating from the edited message will be captured.
            If not, such capturing will be stopped.
        """
        def augmented(msg_identifier, *aa, **kw):
            edited = edit_func(msg_identifier, *aa, **kw)

            if (edited is True and self._enable_inline) or (isinstance(edited, dict) and self._enable_chat):
                if self._contains_callback_data(kw):
                    self.capture_origin(msg_identifier)
                else:
                    self.uncapture_origin(msg_identifier)

            return edited
        return augmented

    def augment_on_message(self, handler):
        """
        :param handler:
            an ``on_message()`` handler function

        :return:
            a function that wraps around ``handler`` and examines whether the
            incoming message is a chosen inline result with an ``inline_message_id``
            field. If so, future callback query originating from this chosen
            inline result will be captured.
        """
        def augmented(msg):
            if (self._enable_inline
                    and flavor(msg) == 'chosen_inline_result'
                    and 'inline_message_id' in msg):
                inline_message_id = msg['inline_message_id']
                self.capture_origin(inline_message_id)

            return handler(msg)
        return augmented

    def augment_bot(self, bot):
        """
        :return:
            a proxy to ``bot`` with these modifications:

            - all ``send*`` methods augmented by :meth:`augment_send`
            - all ``edit*`` methods augmented by :meth:`augment_edit`
            - all other public methods, including properties, copied unchanged
        """
        # Because a plain object cannot be set attributes, we need a class.
        class BotProxy(object):
            pass

        proxy = BotProxy()

        send_methods = ['sendMessage',
                        'forwardMessage',
                        'sendPhoto',
                        'sendAudio',
                        'sendDocument',
                        'sendSticker',
                        'sendVideo',
                        'sendVoice',
                        'sendLocation',
                        'sendVenue',
                        'sendContact',
                        'sendChatAction',]

        for method in send_methods:
            setattr(proxy, method, self.augment_send(getattr(bot, method)))

        edit_methods = ['editMessageText',
                        'editMessageCaption',
                        'editMessageReplyMarkup',]

        for method in edit_methods:
            setattr(proxy, method, self.augment_edit(getattr(bot, method)))

        def public_untouched(nv):
            name, value = nv
            return (not name.startswith('_')
                    and name not in send_methods + edit_methods)

        for name, value in filter(public_untouched, inspect.getmembers(bot)):
            setattr(proxy, name, value)

        return proxy


class SafeDict(dict):
    """
    A subclass of ``dict``, thread-safety added::

        d = SafeDict()  # Thread-safe operations include:
        d['a'] = 3      # key assignment
        d['a']          # key retrieval
        del d['a']      # key deletion
    """

    def __init__(self, *args, **kwargs):
        super(SafeDict, self).__init__(*args, **kwargs)
        self._lock = threading.Lock()

    def _locked(func):
        def k(self, *args, **kwargs):
            with self._lock:
                return func(self, *args, **kwargs)
        return k

    @_locked
    def __getitem__(self, key):
        return super(SafeDict, self).__getitem__(key)

    @_locked
    def __setitem__(self, key, value):
        return super(SafeDict, self).__setitem__(key, value)

    @_locked
    def __delitem__(self, key):
        return super(SafeDict, self).__delitem__(key)


_cqc_origins = SafeDict()

class InterceptCallbackQueryMixin(object):
    """
    Install a :class:`.CallbackQueryCoordinator` to capture callback query
    dynamically.

    Using this mixin has one consequence. The :meth:`self.bot` property no longer
    returns the original :class:`.Bot` object. Instead, it returns an augmented
    version of the :class:`.Bot` (augmented by :class:`.CallbackQueryCoordinator`).
    The original :class:`.Bot` can be accessed with ``self.__bot`` (double underscore).
    """
    CallbackQueryCoordinator = CallbackQueryCoordinator

    def __init__(self, intercept_callback_query, *args, **kwargs):
        """
        :param intercept_callback_query:
            a 2-tuple (enable_chat, enable_inline) to pass to
            :class:`.CallbackQueryCoordinator`
        """
        global _cqc_origins

        # Restore origin set to CallbackQueryCoordinator
        if self.id in _cqc_origins:
            origin_set = _cqc_origins[self.id]
        else:
            origin_set = set()
            _cqc_origins[self.id] = origin_set

        if isinstance(intercept_callback_query, tuple):
            cqc_enable = intercept_callback_query
        else:
            cqc_enable = (intercept_callback_query,) * 2

        self._callback_query_coordinator = self.CallbackQueryCoordinator(self.id, origin_set, *cqc_enable)
        cqc = self._callback_query_coordinator
        cqc.configure(self.listener)

        self.__bot = self._bot  # keep original version of bot
        self._bot = cqc.augment_bot(self._bot)  # modify send* and edit* methods
        self.on_message = cqc.augment_on_message(self.on_message)  # modify on_message()

        super(InterceptCallbackQueryMixin, self).__init__(*args, **kwargs)

    def __del__(self):
        global _cqc_origins
        if self.id in _cqc_origins and not _cqc_origins[self.id]:
            del _cqc_origins[self.id]
            # Remove empty set from dictionary

    @property
    def callback_query_coordinator(self):
        return self._callback_query_coordinator


class IdleEventCoordinator(object):
    def __init__(self, scheduler, timeout):
        self._scheduler = scheduler
        self._timeout_seconds = timeout
        self._timeout_event = None

    def refresh(self):
        """ Refresh timeout timer """
        try:
            if self._timeout_event:
                self._scheduler.cancel(self._timeout_event)

        # Timeout event has been popped from queue prematurely
        except exception.EventNotFound:
            pass

        # Ensure a new event is scheduled always
        finally:
            self._timeout_event = self._scheduler.event_later(
                                      self._timeout_seconds,
                                      ('_idle', {'seconds': self._timeout_seconds}))

    def augment_on_message(self, handler):
        """
        :return:
            a function wrapping ``handler`` to refresh timer for every
            non-event message
        """
        def augmented(msg):
            # Reset timer if this is an external message
            is_event(msg) or self.refresh()

            # Ignore timeout event that have been popped from queue prematurely
            if flavor(msg) == '_idle' and msg is not self._timeout_event.data:
                return

            return handler(msg)
        return augmented

    def augment_on_close(self, handler):
        """
        :return:
            a function wrapping ``handler`` to cancel timeout event
        """
        def augmented(ex):
            try:
                if self._timeout_event:
                    self._scheduler.cancel(self._timeout_event)
                    self._timeout_event = None
            # This closing may have been caused by my own timeout, in which case
            # the timeout event can no longer be found in the scheduler.
            except exception.EventNotFound:
                self._timeout_event = None
            return handler(ex)
        return augmented


class IdleTerminateMixin(object):
    """
    Install an :class:`.IdleEventCoordinator` to manage idle timeout. Also define
    instance method ``on__idle()`` to handle idle timeout events.
    """
    IdleEventCoordinator = IdleEventCoordinator

    def __init__(self, timeout, *args, **kwargs):
        self._idle_event_coordinator = self.IdleEventCoordinator(self.scheduler, timeout)
        idlec = self._idle_event_coordinator
        idlec.refresh()  # start timer
        self.on_message = idlec.augment_on_message(self.on_message)
        self.on_close = idlec.augment_on_close(self.on_close)
        super(IdleTerminateMixin, self).__init__(*args, **kwargs)

    @property
    def idle_event_coordinator(self):
        return self._idle_event_coordinator

    def on__idle(self, event):
        """
        Raise an :class:`.IdleTerminate` to close the delegate.
        """
        raise exception.IdleTerminate(event['_idle']['seconds'])


class StandardEventScheduler(object):
    """
    A proxy to the underlying :class:`.Bot`\'s scheduler, this object implements
    the *standard event format*. A standard event looks like this::

        {'_flavor': {
            'source': {
                'space': event_space, 'id': source_id}
            'custom_key1': custom_value1,
            'custom_key2': custom_value2,
             ... }}

    - There is a single top-level key indicating the flavor, starting with an _underscore.
    - On the second level, there is a ``source`` key indicating the event source.
    - An event source consists of an *event space* and a *source id*.
    - An event space is shared by all delegates in a group. Source id simply refers
      to a delegate's id. They combine to ensure a delegate is always able to capture
      its own events, while its own events would not be mistakenly captured by others.

    Events scheduled through this object always have the second-level ``source`` key fixed,
    while the flavor and other data may be customized.
    """
    def __init__(self, scheduler, event_space, source_id):
        self._base = scheduler
        self._event_space = event_space
        self._source_id = source_id

    @property
    def event_space(self):
        return self._event_space

    def configure(self, listener):
        """
        Configure a :class:`.Listener` to capture events with this object's
        event space and source id.
        """
        listener.capture([{re.compile('^_.+'): {'source': {'space': self._event_space, 'id': self._source_id}}}])

    def make_event_data(self, flavor, data):
        """
        Marshall ``flavor`` and ``data`` into a standard event.
        """
        if not flavor.startswith('_'):
            raise ValueError('Event flavor must start with _underscore')

        d = {'source': {'space': self._event_space, 'id': self._source_id}}
        d.update(data)
        return {flavor: d}

    def event_at(self, when, data_tuple):
        """
        Schedule an event to be emitted at a certain time.

        :param when: an absolute timestamp
        :param data_tuple: a 2-tuple (flavor, data)
        :return: an event object, useful for cancelling.
        """
        return self._base.event_at(when, self.make_event_data(*data_tuple))

    def event_later(self, delay, data_tuple):
        """
        Schedule an event to be emitted after a delay.

        :param delay: number of seconds
        :param data_tuple: a 2-tuple (flavor, data)
        :return: an event object, useful for cancelling.
        """
        return self._base.event_later(delay, self.make_event_data(*data_tuple))

    def event_now(self, data_tuple):
        """
        Schedule an event to be emitted now.

        :param data_tuple: a 2-tuple (flavor, data)
        :return: an event object, useful for cancelling.
        """
        return self._base.event_now(self.make_event_data(*data_tuple))

    def cancel(self, event):
        """ Cancel an event. """
        return self._base.cancel(event)


class StandardEventMixin(object):
    """
    Install a :class:`.StandardEventScheduler`.
    """
    StandardEventScheduler = StandardEventScheduler

    def __init__(self, event_space, *args, **kwargs):
        self._scheduler = self.StandardEventScheduler(self.bot.scheduler, event_space, self.id)
        self._scheduler.configure(self.listener)
        super(StandardEventMixin, self).__init__(*args, **kwargs)

    @property
    def scheduler(self):
        return self._scheduler


class ListenerContext(object):
    def __init__(self, bot, context_id, *args, **kwargs):
        # Initialize members before super() so mixin could use them.
        self._bot = bot
        self._id = context_id
        self._listener = bot.create_listener()
        super(ListenerContext, self).__init__(*args, **kwargs)

    @property
    def bot(self):
        """
        The underlying :class:`.Bot` or an augmented version thereof
        """
        return self._bot

    @property
    def id(self):
        return self._id

    @property
    def listener(self):
        """ See :class:`.Listener` """
        return self._listener


class ChatContext(ListenerContext):
    def __init__(self, bot, context_id, *args, **kwargs):
        super(ChatContext, self).__init__(bot, context_id, *args, **kwargs)
        self._chat_id = context_id
        self._sender = Sender(self.bot, self._chat_id)
        self._administrator = Administrator(self.bot, self._chat_id)

    @property
    def chat_id(self):
        return self._chat_id

    @property
    def sender(self):
        """ A :class:`.Sender` for this chat """
        return self._sender

    @property
    def administrator(self):
        """ An :class:`.Administrator` for this chat """
        return self._administrator


class UserContext(ListenerContext):
    def __init__(self, bot, context_id, *args, **kwargs):
        super(UserContext, self).__init__(bot, context_id, *args, **kwargs)
        self._user_id = context_id
        self._sender = Sender(self.bot, self._user_id)

    @property
    def user_id(self):
        return self._user_id

    @property
    def sender(self):
        """ A :class:`.Sender` for this user """
        return self._sender


class CallbackQueryOriginContext(ListenerContext):
    def __init__(self, bot, context_id, *args, **kwargs):
        super(CallbackQueryOriginContext, self).__init__(bot, context_id, *args, **kwargs)
        self._origin = context_id
        self._editor = Editor(self.bot, self._origin)

    @property
    def origin(self):
        """ Mesasge identifier of callback query's origin """
        return self._origin

    @property
    def editor(self):
        """ An :class:`.Editor` to the originating message """
        return self._editor


def openable(cls):
    """
    A class decorator to fill in certain methods and properties to ensure
    a class can be used by :func:`.create_open`.

    These instance methods and property will be added, if not defined
    by the class:

    - ``open(self, initial_msg, seed)``
    - ``on_message(self, msg)``
    - ``on_close(self, ex)``
    - ``close(self, ex=None)``
    - property ``listener``
    """

    def open(self, initial_msg, seed):
        pass

    def on_message(self, msg):
        raise NotImplementedError()

    def on_close(self, ex):
        logging.error('on_close() called due to %s: %s', type(ex).__name__, ex)

    def close(self, ex=None):
        raise ex if ex else exception.StopListening()

    @property
    def listener(self):
        raise NotImplementedError()

    def ensure_method(name, fn):
        if getattr(cls, name, None) is None:
            setattr(cls, name, fn)

    # set attribute if no such attribute
    ensure_method('open', open)
    ensure_method('on_message', on_message)
    ensure_method('on_close', on_close)
    ensure_method('close', close)
    ensure_method('listener', listener)

    return cls


class Router(object):
    """
    Map a message to a handler function, using a **key function** and
    a **routing table** (dictionary).

    A *key function* digests a message down to a value. This value is treated
    as a key to the *routing table* to look up a corresponding handler function.
    """

    def __init__(self, key_function, routing_table):
        """
        :param key_function:
            A function that takes one argument (the message) and returns
            one of the following:

            - a key to the routing table
            - a 1-tuple (key,)
            - a 2-tuple (key, (positional, arguments, ...))
            - a 3-tuple (key, (positional, arguments, ...), {keyword: arguments, ...})

            Extra arguments, if returned, will be applied to the handler function
            after using the key to look up the routing table.

        :param routing_table:
            A dictionary of ``{key: handler}``. A ``None`` key acts as a default
            catch-all. If the key being looked up does not exist in the routing
            table, the ``None`` key and its corresponding handler is used.
        """
        super(Router, self).__init__()
        self.key_function = key_function
        self.routing_table = routing_table

    def map(self, msg):
        """
        Apply key function to ``msg`` to obtain a key. Return the routing table entry.
        """
        k = self.key_function(msg)
        key = k[0] if isinstance(k, (tuple, list)) else k
        return self.routing_table[key]

    def route(self, msg, *aa, **kw):
        """
        Apply key function to ``msg`` to obtain a key, look up routing table
        to obtain a handler function, then call the handler function with
        positional and keyword arguments, if any is returned by the key function.

        ``*aa`` and ``**kw`` are dummy placeholders for easy chaining.
        Regardless of any number of arguments returned by the key function,
        multi-level routing may be achieved like this::

            top_router.routing_table['key1'] = sub_router1.route
            top_router.routing_table['key2'] = sub_router2.route
        """
        k = self.key_function(msg)

        if isinstance(k, (tuple, list)):
            key, args, kwargs = {1: tuple(k) + ((),{}),
                                 2: tuple(k) + ({},),
                                 3: tuple(k),}[len(k)]
        else:
            key, args, kwargs = k, (), {}

        try:
            fn = self.routing_table[key]
        except KeyError as e:
            # Check for default handler, key=None
            if None in self.routing_table:
                fn = self.routing_table[None]
            else:
                raise RuntimeError('No handler for key: %s, and default handler not defined' % str(e.args))

        return fn(msg, *args, **kwargs)


class DefaultRouterMixin(object):
    """
    Install a default :class:`.Router` and the instance method ``on_message()``.
    """
    def __init__(self, *args, **kwargs):
        self._router = Router(flavor, {'chat': lambda msg: self.on_chat_message(msg),
                                       'callback_query': lambda msg: self.on_callback_query(msg),
                                       'inline_query': lambda msg: self.on_inline_query(msg),
                                       'chosen_inline_result': lambda msg: self.on_chosen_inline_result(msg),
                                       '_idle': lambda event: self.on__idle(event)})
                                       # use lambda to delay evaluation of self.on_ZZZ to runtime because
                                       # I don't want to require defining all methods right here.

        super(DefaultRouterMixin, self).__init__(*args, **kwargs)

    @property
    def router(self):
        return self._router

    def on_message(self, msg):
        """ Call :meth:`.Router.route` to handle the message. """
        self._router.route(msg)


@openable
class Monitor(ListenerContext, DefaultRouterMixin):
    def __init__(self, seed_tuple, capture, **kwargs):
        """
        A delegate that never times-out, probably doing some kind of background monitoring
        in the application. Most naturally paired with :func:`.per_application`.

        :param capture: a list of patterns for :class:`.Listener` to capture
        """
        bot, initial_msg, seed = seed_tuple
        super(Monitor, self).__init__(bot, seed, **kwargs)

        for pattern in capture:
            self.listener.capture(pattern)


@openable
class ChatHandler(ChatContext,
                  DefaultRouterMixin,
                  StandardEventMixin,
                  IdleTerminateMixin):
    def __init__(self, seed_tuple,
                 include_callback_query=False, **kwargs):
        """
        A delegate to handle a chat.
        """
        bot, initial_msg, seed = seed_tuple
        super(ChatHandler, self).__init__(bot, seed, **kwargs)

        self.listener.capture([{'chat': {'id': self.chat_id}}])

        if include_callback_query:
            self.listener.capture([{'message': {'chat': {'id': self.chat_id}}}])


@openable
class UserHandler(UserContext,
                  DefaultRouterMixin,
                  StandardEventMixin,
                  IdleTerminateMixin):
    def __init__(self, seed_tuple,
                 include_callback_query=False,
                 flavors=chat_flavors+inline_flavors, **kwargs):
        """
        A delegate to handle a user's actions.

        :param flavors:
            A list of flavors to capture. ``all`` covers all flavors.
        """
        bot, initial_msg, seed = seed_tuple
        super(UserHandler, self).__init__(bot, seed, **kwargs)

        if flavors == 'all':
            self.listener.capture([{'from': {'id': self.user_id}}])
        else:
            self.listener.capture([lambda msg: flavor(msg) in flavors, {'from': {'id': self.user_id}}])

        if include_callback_query:
            self.listener.capture([{'message': {'chat': {'id': self.user_id}}}])


class InlineUserHandler(UserHandler):
    def __init__(self, seed_tuple, **kwargs):
        """
        A delegate to handle a user's inline-related actions.
        """
        super(InlineUserHandler, self).__init__(seed_tuple, flavors=inline_flavors, **kwargs)


@openable
class CallbackQueryOriginHandler(CallbackQueryOriginContext,
                                 DefaultRouterMixin,
                                 StandardEventMixin,
                                 IdleTerminateMixin):
    def __init__(self, seed_tuple, **kwargs):
        """
        A delegate to handle callback query from one origin.
        """
        bot, initial_msg, seed = seed_tuple
        super(CallbackQueryOriginHandler, self).__init__(bot, seed, **kwargs)

        self.listener.capture([
            lambda msg:
                flavor(msg) == 'callback_query' and origin_identifier(msg) == self.origin
        ])
