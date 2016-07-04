import time
import traceback
import threading
import logging
from functools import partial
from . import filtering, exception
from . import flavor, chat_flavors, inline_flavors, _isstring, message_identifier

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
                func(self, *args, **kwargs)
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


class Timer(object):
    def __init__(self, seconds, timeout_class):
        """
        :param seconds:
            Number of seconds to timeout

        :param timeout_class:
            Class of exception to be raised on timeout.
            Must be a subclass of :class:`.exception.WaitTooLong`.
        """
        super(Timer, self).__init__()
        self.seconds = seconds
        self.timeout_class = timeout_class
        self._expiry = None

    def start(self):
        self._expiry = time.time() + self.seconds

    def timeleft(self):
        return self._expiry - time.time()


class Listener(object):
    """
    Suspends execution until specified messages arrive.
    """

    CRITERIA, TIMER, RESTART, CANCEL_ON_TIMEOUT = range(0,4)

    def __init__(self, mic, q):
        self._mic = mic
        self._queue = q
        self._captures = []

    def __del__(self):
        self._mic.remove(self._queue)

    def capture(self, criteria, timer, restart=True, auto_cancel=True, function_compare='bytecode'):
        """
        Add a capture criteria.

        :type criteria: dictionary, a sequence of key/value pairs
        :param criteria:
            - the **key** is used to *select* a part of message
                - use a double__underscore to "drill down a level",
                  e.g. ``chat__id`` selects ``msg['chat']['id']``,
                  ``from`` selects ``msg['from']``.
                - use a ``_`` (single underscore) to select the entire message.

            - the **value** is a "template" to match against selected part, may be one of these:
                - a simple value
                - a function that:
                    - takes one argument - the part of message selected by the key
                    - returns ``True`` to indicate a match
                - a dictionary whose:
                    - **keys** are used to further select parts of message
                    - **values** are "templates" to match against those selected parts

            All key/value pairs have to be satisifed for a message to be considered a match.

        Thanks to `Django <https://www.djangoproject.com/>`_ for inspiration.

        :param timer:
            A :class:`Timer` object to wait for the criteria to be met.
            ``None`` means no time restriction.

        :type restart: bool
        :param restart: Whether to restart the timer when the criteria is met.

        :type auto_cancel: bool
        :param auto_cancel: Whether to cancel the criteria on timeout.

        This method may be called multiple times, resulting in a *list* of capture criteria.
        A message is considered a match if any *one* of these criteria is satisfied.
        """
        # Supposed to override identical criteria, so remove duplicate here, if any.
        self.cancel_capture(criteria, function_compare)

        if not isinstance(restart, (tuple, list)):
            restart = [restart]

        # Convert True to supplied timer, then eliminate False values.
        restart = list(filter(bool, map(lambda e: timer if e is True else e, restart)))

        # Every element in the tuple should have been normalized for later use
        self._captures.append((criteria,
                               timer,
                               restart,
                               auto_cancel))
        if timer:
            timer.start()

    def _isequal(self, c1, c2, function_compare='bytecode'):
        if c1 == c2:
            return True

        if callable(c1) and callable(c2):
            if function_compare == 'bytecode':
                return c1.__code__.co_code == c2.__code__.co_code
            elif function_compare == '__telepot__':
                return c1.__telepot__ == c2.__telepot__
            else:
                raise ValueError()

        if type(c1) != type(c2):
            return False

        if not isinstance(c1, dict):
            return False

        if len(c1) != len(c2):
            return False

        for key,value in c1.items():
            if key not in c2:
                return False

            if not self._isequal(value, c2[key], function_compare):
                return False
        return True

    def cancel_capture(self, criteria, function_compare='bytecode'):
        """ Remove a previously added capture criteria. """
        self._captures = list(filter(lambda cap: not self._isequal(criteria, cap[self.CRITERIA], function_compare), self._captures))

    def is_capturing(self, criteria, function_compare='bytecode'):
        """ Check whether a capture criteria is currently in effect. """
        return any(map(lambda cap: self._isequal(criteria, cap[self.CRITERIA], function_compare), self._captures))

    def clear_captures(self):
        """ Remove all capture criteria. """
        del self._captures[:]

    def _find_shortest_timer(self):
        target = None
        for cap in self._captures:
            timer = cap[self.TIMER]

            if not timer:
                continue

            if not target:
                target = timer
                continue

            if timer.timeleft() < target.timeleft():
                target = timer

        return target

    def wait(self):
        """
        Block until a matched message appears.
        """
        if not self._captures:
            raise RuntimeError('Listener has no capture criteria.')

        while 1:
            short = self._find_shortest_timer()

            try:
                if short:
                    timeleft = short.timeleft()
                    msg = self._queue.get(block=True, timeout=0 if timeleft < 0 else timeleft)
                else:
                    msg = self._queue.get(block=True)
            except queue.Empty:
                if short:
                    # Extract criteria associated with this timeout
                    expired_criteria = [cap[self.CRITERIA] for cap in filter(lambda cap: cap[self.TIMER]==short, self._captures)]

                    # Eliminate entries associated with this timeout that have `cancel_on_timeout`
                    self._captures = list(filter(lambda cap: not (cap[self.TIMER]==short and cap[self.CANCEL_ON_TIMEOUT]), self._captures))

                    # Raise specified error
                    raise short.timeout_class(short.seconds, expired_criteria)

            matched_restarts = [cap[self.RESTART]
                                   for cap in filter(lambda cap: filtering.ok(msg, **cap[self.CRITERIA]), self._captures)]

            if not matched_restarts:
                continue

            # Flatten lists, then use `set` to remove duplicates
            for timer in set([item for sublist in matched_restarts for item in sublist]):
                timer.start()

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
    - :meth:`.Bot.sendAudio`
    - :meth:`.Bot.sendDocument`
    - :meth:`.Bot.sendSticker`
    - :meth:`.Bot.sendVideo`
    - :meth:`.Bot.sendVoice`
    - :meth:`.Bot.sendLocation`
    - :meth:`.Bot.sendVenue`
    - :meth:`.Bot.sendContact`
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
    When processing inline queries, ensures **at most one active thread** per user id.
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
    def __init__(self):
        super(AnswererMixin, self).__init__()
        self._answerer = Answerer(self.bot)

    @property
    def answerer(self):
        return self._answerer


class CallbackQueryCoordinator(object):
    def __init__(self, listener, timer):
        super(CallbackQueryCoordinator, self).__init__()
        self._listener = listener
        self._timer = timer
        self._pending_ids = []
        self._capture_options = {'private': self.make_options(scheme='piggyback',
                                                              callback_timeout=self._timer.seconds),
                                 'group': self.make_options(scheme='piggyback',
                                                            callback_timeout=self._timer.seconds),
                                 'supergroup': self.make_options(scheme='piggyback',
                                                                 callback_timeout=self._timer.seconds),
                                 'channel': self.make_options(scheme='piggyback',
                                                              callback_timeout=self._timer.seconds),
                                 'inline': self.make_options(scheme='independent',
                                                             callback_timeout=self._timer.seconds)}

    def make_options(self, scheme=None, **capture_options):
        if scheme is not None:
            if scheme == 'piggyback':
                return dict(timer=self._timer, restart=True, auto_cancel=True)
            elif scheme == 'independent':
                callback_timeout = capture_options['callback_timeout']
                return dict(timer=Timer(callback_timeout, exception.AbsentCallbackQuery), restart=False, auto_cancel=True)
            elif scheme == 'semi-independent':
                callback_timeout = capture_options['callback_timeout']
                return dict(timer=Timer(callback_timeout, exception.AbsentCallbackQuery), restart=[self._timer], auto_cancel=True)
            else:
                raise ValueError('Bad scheme name')
        else:
            return capture_options

    def set_options(self, context, **capture_options):
        if 'callback_timeout'in capture_options:
            existing = self._capture_options[context]
            existing['timer'].seconds = capture_options['callback_timeout']
        else:
            self._capture_options[context] = capture_options

    def _capture_criteria(self, message=None, msg_identifier=None):
        if message:
            return dict(_=lambda msg: flavor(msg) == 'callback_query',
                        message__chat__id=message['chat']['id'],
                        message__message_id=message['message_id'])
        elif msg_identifier:
            if _isstring(msg_identifier):
                inline_message_id = msg_identifier
            elif isinstance(msg_identifier, tuple) and len(msg_identifier) == 1:
                inline_message_id = msg_identifier[0]
            else:
                raise ValueError('Do not handle 2-tuple (chat_id, message_id) for now')

            return dict(_=lambda msg: flavor(msg) == 'callback_query',
                        inline_message_id=inline_message_id)
        else:
            raise ValueError()

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
        def augmented(*aa, **kw):
            sent = send_func(*aa, **kw)

            if self._contains_callback_data(kw):
                self._listener.capture(self._capture_criteria(message=sent),
                                       **self._capture_options[sent['chat']['type']])

            return sent
        return augmented

    def augment_edit(self, edit_func):
        def augmented(msg_identifier, *aa, **kw):
            edited = edit_func(msg_identifier, *aa, **kw)

            if self._contains_callback_data(kw):
                if edited is True:
                    self._listener.capture(self._capture_criteria(msg_identifier=msg_identifier),
                                           **self._capture_options['inline'])
                elif 'chat' in edited:
                    self._listener.capture(self._capture_criteria(message=edited),
                                           **self._capture_options[edited['chat']['type']])
                else:
                    raise ValueError()
            else:
                if edited is True:
                    self._listener.cancel_capture(self._capture_criteria(msg_identifier=msg_identifier))
                elif 'chat' in edited:
                    self._listener.cancel_capture(self._capture_criteria(message=edited))
                else:
                    raise ValueError()

            return edited
        return augmented

    def augment_answerInlineQuery(self, answer_func):
        def augmented(inline_query_id, results, *aa, **kw):
            response = answer_func(inline_query_id, results, *aa, **kw)
            self._pending_ids = [filtering.pick(r, 'id') for r in results if self._contains_callback_data(r)]
            return response
        return augmented

    def augment_on_message(self, handler):
        def augmented(msg):
            if (flavor(msg) == 'chosen_inline_result'
                    and 'inline_message_id' in msg
                    and msg['result_id'] in self._pending_ids):
                inline_message_id = msg['inline_message_id']
                self._listener.capture(self._capture_criteria(msg_identifier=inline_message_id),
                                       **self._capture_options['inline'])

            return handler(msg)
        return augmented

    def augment_bot(self, bot):
        # Because a plain object cannot be set attributes, we need a class.
        class Proxy(object):
            pass

        proxy = Proxy()

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

        answer_methods = ['answerInlineQuery']

        for method in answer_methods:
            setattr(proxy, method, self.augment_answerInlineQuery(getattr(bot, method)))

        def public_untouched(attr):
            return (not attr.startswith('_')
                    and callable(getattr(bot, attr))
                    and attr not in send_methods + edit_methods + answer_methods)

        for method in filter(public_untouched, dir(bot)):
            setattr(proxy, method, getattr(bot, method))

        return proxy

    def cancel_capture_for(self, msg):
        f = flavor(msg)
        if f in ['chat', 'edited_chat']:
            self._listener.cancel_capture(self._capture_criteria(message=msg))
        elif f == 'chosen_inline_result':
            if 'inline_message_id' in msg:
                self._listener.cancel_capture(self._capture_criteria(msg_identifier=msg['inline_message_id']))
        elif f == 'callback_query':
            if 'message' in msg:
                self._listener.cancel_capture(self._capture_criteria(message=msg['message']))
            elif 'inline_message_id' in msg:
                self._listener.cancel_capture(self._capture_criteria(msg_identifier=msg['inline_message_id']))


class CallbackQueryAble(object):
    COORDINATOR_CLASS = CallbackQueryCoordinator

    def __init__(self, bot, *args, **kwargs):
        timeout, enable_callback_query = kwargs['timeout'], kwargs['enable_callback_query']

        self.__bot = bot  # double__underscore: do not over-shadow ListenerContext._bot
        self._listener = bot.create_listener()
        self._primary_timer = Timer(timeout, exception.IdleTerminate)
        self._callback_query_coordinator = self.COORDINATOR_CLASS(self._listener, self._primary_timer)

        if enable_callback_query:
            augmented_bot = self._callback_query_coordinator.augment_bot(bot)
            super(CallbackQueryAble, self).__init__(augmented_bot, *args)
            self.on_message = self._callback_query_coordinator.augment_on_message(self.on_message)
        else:
            super(CallbackQueryAble, self).__init__(bot, *args)

    @property
    def listener(self):
        """ See :class:`.helper.Listener` """
        return self._listener

    @property
    def primary_timer(self):
        """ See :class:`.helper.Timer` """
        return self._primary_timer

    @property
    def callback_query_coordinator(self):
        """ See :class:`.helper.CallbackQueryCoordinator` """
        return self._callback_query_coordinator


class ListenerContext(object):
    def __init__(self, bot, context_id):
        self._bot = bot  # Initialize before super() so mixin could use.
        self._id = context_id
        super(ListenerContext, self).__init__()
        try:
            self._listener  # Initialized?
        except:
            self._listener = bot.create_listener()  # If not, do so.

    @property
    def bot(self):
        """
        The underlying :class:`.Bot` or an augmented version of it
        able to handle callback query.
        """
        return self._bot

    @property
    def id(self):
        return self._id

    @property
    def listener(self):
        """ See :class:`.helper.Listener` """
        return self._listener


class ChatContext(ListenerContext):
    def __init__(self, bot, context_id, chat_id):
        super(ChatContext, self).__init__(bot, context_id)
        self._chat_id = chat_id
        self._sender = Sender(bot, chat_id)
        self._administrator = Administrator(bot, chat_id)

    @property
    def chat_id(self):
        return self._chat_id

    @property
    def sender(self):
        """ See :class:`.helper.Sender` """
        return self._sender

    @property
    def administrator(self):
        """ See :class:`.helper.Administrator` """
        return self._administrator


class UserContext(ListenerContext):
    def __init__(self, bot, context_id, user_id):
        super(UserContext, self).__init__(bot, context_id)
        self._user_id = user_id
        self._sender = Sender(bot, user_id)

    @property
    def user_id(self):
        return self._user_id

    @property
    def sender(self):
        """ See :class:`.helper.Sender` """
        return self._sender


def openable(cls):
    def open(self, initial_msg, seed):
        """
        Called when the delegate is started.

        :return:
            Whether ``initial_msg`` is considered "handled".
            If this object is created with :func:`.delegate.create_open` and
            this method returns ``False`` (or anything evaluated to boolean ``False``),
            ``self.on_message(initial_msg)`` is called immediately after.

        By default, this method is empty, equivalent to returning a ``False``.
        If you don't override, ``self.on_message(initial_msg)`` will be called.
        The initial message will not be missed.
        """
        pass

    def on_message(self, msg):
        """
        Called when a message is received. Subclasses have to implement.
        """
        raise NotImplementedError()

    def on_timeout(self, exception):
        """
        Called when an :class:`exception.WaitTooLong` happens (but other than
        an :class:`exception.IdleTerminate`).
        """
        pass

    def on_close(self, exception):
        """
        Called when the delegate is about to die. An :class:`exception.IdleTerminate`
        and all exceptions other than an :class:`exception.WaitTooLong` would cause
        a delegate to die.

        :param exception: Cause of death
        """
        logging.error('on_close() called due to %s: %s', type(exception).__name__, exception)

    def close(self, code=None, reason=None):
        """
        Raise an :class:`.exception.StopListening`, causing the delegate to die.

        :param code:
        :param reason: No standard. You decide what they mean.
        """
        raise exception.StopListening(code, reason)

    @property
    def listener(self):
        raise NotImplementedError()

    def ensure_method(name, fn):
        if getattr(cls, name, None) is None:
            setattr(cls, name, fn)

    # set attribute if no such attribute
    ensure_method('open', open)
    ensure_method('on_message', on_message)
    ensure_method('on_timeout', on_timeout)
    ensure_method('on_close', on_close)
    ensure_method('close', close)
    ensure_method('listener', listener)

    return cls


class Router(object):
    """
    This object maps a message to a handler function. It has
    a **key function** and a **routing table** (which is a dictionary).

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

    def route(self, msg, *aa, **kw):
        """
        Apply key function to ``msg`` to obtain a key, look up routing table
        to obtain a handler function, then call the handler function with
        positional and keyword arguments, if any is returned by the key function.

        ``*aa`` and ``**kw`` are dummy placeholders for easy nesting.
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
    def __init__(self):
        super(DefaultRouterMixin, self).__init__()
        self._router = Router(flavor, {'chat': lambda msg: self.on_chat_message(msg),
                                       'edited_chat': lambda msg: self.on_edited_chat_message(msg),
                                       'callback_query': lambda msg: self.on_callback_query(msg),
                                       'inline_query': lambda msg: self.on_inline_query(msg),
                                       'chosen_inline_result': lambda msg: self.on_chosen_inline_result(msg)})
                                       # use lambda to delay evaluation of self.on_ZZZ to runtime because
                                       # I don't want to require defining all methods right here.

    @property
    def router(self):
        """ See :class:`.helper.Router` """
        return self._router

    def on_message(self, msg):
        """
        Called when a message is received.
        By default, call :meth:`Router.route` to handle the message.
        """
        self._router.route(msg)


@openable
class Monitor(ListenerContext, DefaultRouterMixin):
    def __init__(self, seed_tuple, capture):
        """
        A delegate that never times-out, probably doing some kind of background monitoring
        in the application. Most naturally paired with :func:`.delegate.per_application`.

        :param capture: a list of capture criteria for its ``listener``
        """
        bot, initial_msg, seed = seed_tuple
        super(Monitor, self).__init__(bot, seed)

        for c in capture:
            self.listener.capture(c, timer=None)


@openable
class ChatHandler(CallbackQueryAble, ChatContext, DefaultRouterMixin):
    def __init__(self, seed_tuple, timeout, enable_callback_query=True):
        """
        A delegate to handle a chat.
        Most naturally paired with :func:`.delegate.per_chat_id`.

        :type timeout: number of seconds
        :param timeout:
            If no message is captured after this period of time,
            an :class:`.exception.WaitTooLong` will be raised,
            causing the delegate to die.

        :type enable_callback_query: bool
        :param enable_callback_query:
            Whether to augment the bot's public methods with :class:`CallbackQueryCoordinator`
            so callback query can be handled transparently.
        """
        bot, initial_msg, seed = seed_tuple
        super(ChatHandler, self).__init__(bot, seed, initial_msg['chat']['id'],
                                          timeout=timeout,
                                          enable_callback_query=enable_callback_query)

        self.listener.capture(dict(chat__id=self.chat_id), timer=self.primary_timer)


@openable
class UserHandler(CallbackQueryAble, UserContext, DefaultRouterMixin):
    def __init__(self, seed_tuple, timeout, flavors=chat_flavors+inline_flavors, enable_callback_query=True):
        """
        A delegate to handle a user's actions.
        Most naturally paired with :func:`.delegate.per_from_id`.

        :type timeout: number of seconds
        :param timeout:
            If no message is captured after this period of time,
            an :class:`.exception.WaitTooLong` will be raised,
            causing the delegate to die.

        :param flavors:
            A list of flavors to capture. ``all`` covers all flavors.

        :type enable_callback_query: bool
        :param enable_callback_query:
            Whether to augment the bot's public methods with :class:`CallbackQueryCoordinator`
            so callback query can be handled transparently.
        """
        bot, initial_msg, seed = seed_tuple
        super(UserHandler, self).__init__(bot, seed, initial_msg['from']['id'],
                                          timeout=timeout,
                                          enable_callback_query=enable_callback_query)

        if flavors == 'all':
            self.listener.capture(dict(from__id=self.user_id),
                                  timer=self.primary_timer)
        else:
            self.listener.capture(dict(_=lambda msg: flavor(msg) in flavors, from__id=self.user_id),
                                  timer=self.primary_timer)


class InlineUserHandler(UserHandler):
    def __init__(self, seed_tuple, timeout, enable_callback_query=True):
        """
        A delegate to handle a user's inline-related actions.
        It captures messages of flavor ``inline_query`` and ``chosen_inline_result`` only.
        Most naturally paired with :func:`.delegate.per_inline_from_id`.

        :type timeout: number of seconds
        :param timeout:
            If no message is captured after this period of time,
            an :class:`.exception.WaitTooLong` will be raised,
            causing the delegate to die.

        :type enable_callback_query: bool
        :param enable_callback_query:
            Whether to augment the bot's public methods with :class:`CallbackQueryCoordinator`
            so callback query can be handled transparently.
        """
        super(InlineUserHandler, self).__init__(seed_tuple, timeout,
                                                flavors=inline_flavors,
                                                enable_callback_query=enable_callback_query)
