import asyncio
import traceback
import time
import telepot
import telepot.helper
import telepot.filtering
from ..exception import WaitTooLong


@asyncio.coroutine
def _yell(fn, *args, **kwargs):
    if asyncio.iscoroutinefunction(fn):
        return (yield from fn(*args, **kwargs))
    else:
        return fn(*args, **kwargs)


def _delay_yell(obj, method_name):
    @asyncio.coroutine
    def d(*a, **kw):
        method = getattr(obj, method_name)
        yield from _yell(method, *a, **kw)
    return d


class Microphone(object):
    def __init__(self):
        self._queues = set()

    def add(self, q):
        self._queues.add(q)

    def remove(self, q):
        self._queues.remove(q)

    def send(self, msg):
        for q in self._queues:
            try:
                q.put_nowait(msg)
            except asyncio.QueueFull:
                traceback.print_exc()
                pass


class Listener(telepot.helper.Listener):
    @asyncio.coroutine
    def wait(self):
        if not self._criteria:
            raise RuntimeError('Listener has no capture criteria, will wait forever.')

        def meet_some_criteria(msg):
            return any(map(lambda c: telepot.filtering.ok(msg, **c), self._criteria))

        timeout, = self.get_options('timeout')

        if timeout is None:
            while 1:
                msg = yield from self._queue.get()

                if meet_some_criteria(msg):
                    return msg
        else:
            end = time.time() + timeout

            while 1:
                timeleft = end - time.time()

                if timeleft < 0:
                    raise WaitTooLong()

                try:
                    msg = yield from asyncio.wait_for(self._queue.get(), timeleft)
                except asyncio.TimeoutError:
                    raise WaitTooLong()

                if meet_some_criteria(msg):
                    return msg


from concurrent.futures._base import CancelledError

class Answerer(object):
    def __init__(self, bot, loop=None):
        self._bot = bot
        self._loop = loop if loop is not None else asyncio.get_event_loop()
        self._working_tasks = {}

    def answer(self, inline_query, compute_fn, *compute_args, **compute_kwargs):
        from_id = inline_query['from']['id']

        @asyncio.coroutine
        def compute_and_answer():
            try:
                query_id = inline_query['id']

                ans = yield from _yell(compute_fn, *compute_args, **compute_kwargs)

                if isinstance(ans, list):
                    yield from self._bot.answerInlineQuery(query_id, ans)
                elif isinstance(ans, tuple):
                    yield from self._bot.answerInlineQuery(query_id, *ans)
                elif isinstance(ans, dict):
                    yield from self._bot.answerInlineQuery(query_id, **ans)
                else:
                    raise ValueError('Invalid answer format')
            except CancelledError:
                # Cancelled. Record has been occupied by new task. Don't touch.
                raise
            except:
                # Die accidentally. Remove myself from record.
                del self._working_tasks[from_id]
                raise
            else:
                # Die naturally. Remove myself from record.
                del self._working_tasks[from_id]

        if from_id in self._working_tasks:
            self._working_tasks[from_id].cancel()

        t = self._loop.create_task(compute_and_answer())
        self._working_tasks[from_id] = t


# Mirror traditional version
openable = telepot.helper.openable

class Router(telepot.helper.Router):
    @asyncio.coroutine
    def route(self, msg):
        k = self._digest(msg)
        
        if isinstance(k, (tuple, list)):
            key, args = k[0], k[1:]
        else:
            key, args = k, ()
        
        try:
            fn = self._table[key]
        except KeyError as e:
            # Check for default handler, key=None
            if None in self._table:
                fn = self._table[None]
            else:
                raise RuntimeError('No handler for key: %s, and default handler not defined' % str(e.args))
        
        yield from _yell(fn, msg, *args)


class DefaultRouterMixin(object):
    def __init__(self):
        super(DefaultRouterMixin, self).__init__()
        self._router = Router(telepot.flavor, {'normal': _delay_yell(self, 'on_chat_message'),
                                               'inline_query': _delay_yell(self, 'on_inline_query'),
                                               'chosen_inline_result': _delay_yell(self, 'on_chosen_inline_result')})

    @property
    def router(self):
        return self._router

    @asyncio.coroutine
    def on_message(self, msg):
        yield from self._router.route(msg)


@openable
class Monitor(telepot.helper.ListenerContext, DefaultRouterMixin):
    def __init__(self, seed_tuple, capture):
        bot, initial_msg, seed = seed_tuple
        super(Monitor, self).__init__(bot, seed)

        for c in capture:
            self.listener.capture(**c)

@openable
class ChatHandler(telepot.helper.ChatContext, DefaultRouterMixin):
    def __init__(self, seed_tuple, timeout):
        bot, initial_msg, seed = seed_tuple
        super(ChatHandler, self).__init__(bot, seed, initial_msg['chat']['id'])
        self.listener.set_options(timeout=timeout)
        self.listener.capture(chat__id=self.chat_id)

@openable
class UserHandler(telepot.helper.UserContext, DefaultRouterMixin):
    def __init__(self, seed_tuple, timeout, flavors='all'):
        bot, initial_msg, seed = seed_tuple
        super(UserHandler, self).__init__(bot, seed, initial_msg['from']['id'])
        self.listener.set_options(timeout=timeout)

        if flavors == 'all':
            self.listener.capture(from__id=self.user_id)
        else:
            self.listener.capture(_=lambda msg: telepot.flavor(msg) in flavors, from__id=self.user_id)
