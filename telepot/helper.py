import time
import traceback
import threading
import logging
from functools import partial
from . import filtering, exception
from . import flavor

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


class Listener(object):
    def __init__(self, mic, q):
        self._mic = mic
        self._queue = q

        self._criteria = []

        self._options = {
            'timeout': None,
        }

    def __del__(self):
        self._mic.remove(self._queue)

    def set_options(self, **name_values):
        self._options.update(name_values)

    def get_options(self, *names):
        return tuple(map(lambda n: self._options[n], names))

    def capture(self, **criteria):
        self._criteria.append(criteria)

    def cancel_capture(self, **criteria):
        # remove duplicates
        self._criteria = list(filter(lambda c: c != criteria, self._criteria))

    def clear_captures(self):
        del self._criteria[:]

    def list_captures(self):
        return self._criteria

    def wait(self):
        if not self._criteria:
            raise RuntimeError('Listener has no capture criteria, will wait forever.')

        def meet_some_criteria(msg):
            return any(map(lambda c: filtering.ok(msg, **c), self._criteria))

        timeout, = self.get_options('timeout')

        if timeout is None:
            while 1:
                msg = self._queue.get(block=True)

                if meet_some_criteria(msg):
                    return msg
        else:
            end = time.time() + timeout

            while 1:
                timeleft = end - time.time()

                if timeleft < 0:
                    raise exception.WaitTooLong()

                try:
                    msg = self._queue.get(block=True, timeout=timeleft)
                except queue.Empty:
                    raise exception.WaitTooLong()

                if meet_some_criteria(msg):
                    return msg


class Sender(object):
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
    def __init__(self, bot, msg_identifier):
        for method in ['editMessageText',
                       'editMessageCaption',
                       'editMessageReplyMarkup',]:
            setattr(self, method, partial(getattr(bot, method), msg_identifier))


class Answerer(object):
    def __init__(self, bot):
        self._bot = bot
        self._workers = {}  # map: user id --> worker thread
        self._lock = threading.Lock()  # control access to `self._workers`

    def answer(outerself, inline_query, compute_fn, *compute_args, **compute_kwargs):
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


class ListenerContext(object):
    def __init__(self, bot, context_id):
        super(ListenerContext, self).__init__()
        self._bot = bot
        self._id = context_id
        self._listener = bot.create_listener()

    @property
    def bot(self):
        return self._bot

    @property
    def id(self):
        return self._id

    @property
    def listener(self):
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
        return self._sender

    @property
    def administrator(self):
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
        return self._sender


def openable(cls):
    def open(self, *arg, **kwargs):
        pass

    def on_message(self, msg):
        raise NotImplementedError()

    def on_close(self, exception):
        logging.error('on_close() called due to %s: %s', type(exception).__name__, exception)

    def close(self, code=None, reason=None):
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
    ensure_method('on_close', on_close)
    ensure_method('close', close)
    ensure_method('listener', listener)

    return cls


class Router(object):
    def __init__(self, key_function, routing_table):
        super(Router, self).__init__()
        self.key_function = key_function
        self.routing_table = routing_table

    # The only relevant argument is the first - the message. Following arguments are
    # just placeholders for easy nesting - no matter what the upper-level router gives,
    # nesting can be done like this:
    #   top_router.routing_table['key'] = sub_router.route
    def route(self, msg, *aa, **kw):
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
        return self._router

    def on_message(self, msg):
        self._router.route(msg)


@openable
class Monitor(ListenerContext, DefaultRouterMixin):
    def __init__(self, seed_tuple, capture):
        bot, initial_msg, seed = seed_tuple
        super(Monitor, self).__init__(bot, seed)

        for c in capture:
            self.listener.capture(**c)

@openable
class ChatHandler(ChatContext, DefaultRouterMixin):
    def __init__(self, seed_tuple, timeout, callback_query=True):
        bot, initial_msg, seed = seed_tuple
        super(ChatHandler, self).__init__(bot, seed, initial_msg['chat']['id'])
        self.listener.set_options(timeout=timeout)
        self.listener.capture(chat__id=self.chat_id)
        if callback_query:
            # Also capture callback_query from the same user
            self.listener.capture(_=lambda msg: flavor(msg)=='callback_query', from__id=self.chat_id)

@openable
class UserHandler(UserContext, DefaultRouterMixin):
    def __init__(self, seed_tuple, timeout, flavors='all'):
        bot, initial_msg, seed = seed_tuple
        super(UserHandler, self).__init__(bot, seed, initial_msg['from']['id'])
        self.listener.set_options(timeout=timeout)

        if flavors == 'all':
            self.listener.capture(from__id=self.user_id)
        else:
            self.listener.capture(_=lambda msg: flavor(msg) in flavors, from__id=self.user_id)

class InlineUserHandler(UserHandler):
    def __init__(self, seed_tuple, timeout):
        super(InlineUserHandler, self).__init__(seed_tuple, timeout, flavors=['inline_query', 'chosen_inline_result'])
