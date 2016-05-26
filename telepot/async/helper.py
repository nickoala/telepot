import asyncio
import traceback
import time
from .. import filtering, helper, exception
from .. import flavor

async def _yell(fn, *args, **kwargs):
    if asyncio.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    else:
        return fn(*args, **kwargs)


def _delay_yell(obj, method_name):
    async def d(*a, **kw):
        method = getattr(obj, method_name)
        return await _yell(method, *a, **kw)
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


class Listener(helper.Listener):
    async def wait(self):
        if not self._criteria:
            raise RuntimeError('Listener has no capture criteria, will wait forever.')

        def meet_some_criteria(msg):
            return any(map(lambda c: filtering.ok(msg, **c), self._criteria))

        timeout, = self.get_options('timeout')

        if timeout is None:
            while 1:
                msg = await self._queue.get()

                if meet_some_criteria(msg):
                    return msg
        else:
            end = time.time() + timeout

            while 1:
                timeleft = end - time.time()

                if timeleft < 0:
                    raise exception.WaitTooLong()

                try:
                    msg = await asyncio.wait_for(self._queue.get(), timeleft)
                except asyncio.TimeoutError:
                    raise exception.WaitTooLong()

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

        async def compute_and_answer():
            try:
                query_id = inline_query['id']

                ans = await _yell(compute_fn, *compute_args, **compute_kwargs)

                if isinstance(ans, list):
                    await self._bot.answerInlineQuery(query_id, ans)
                elif isinstance(ans, tuple):
                    await self._bot.answerInlineQuery(query_id, *ans)
                elif isinstance(ans, dict):
                    await self._bot.answerInlineQuery(query_id, **ans)
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


class Router(helper.Router):
    # The only relevant argument is the first - the message. Following arguments are
    # just placeholders for easy nesting - no matter what the upper-level router gives,
    # nesting can be done like this:
    #   top_router.routing_table['key'] = sub_router.route
    async def route(self, msg, *aa, **kw):
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

        return await _yell(fn, msg, *args, **kwargs)


class DefaultRouterMixin(object):
    def __init__(self):
        super(DefaultRouterMixin, self).__init__()
        self._router = Router(flavor, {'chat': _delay_yell(self, 'on_chat_message'),
                                       'edited_chat': _delay_yell(self, 'on_edited_chat_message'),
                                       'callback_query': _delay_yell(self, 'on_callback_query'),
                                       'inline_query': _delay_yell(self, 'on_inline_query'),
                                       'chosen_inline_result': _delay_yell(self, 'on_chosen_inline_result')})

    @property
    def router(self):
        return self._router

    async def on_message(self, msg):
        await self._router.route(msg)


from ..helper import openable

@openable
class Monitor(helper.ListenerContext, DefaultRouterMixin):
    def __init__(self, seed_tuple, capture):
        bot, initial_msg, seed = seed_tuple
        super(Monitor, self).__init__(bot, seed)

        for c in capture:
            self.listener.capture(**c)

@openable
class ChatHandler(helper.ChatContext, DefaultRouterMixin):
    def __init__(self, seed_tuple, timeout, callback_query=True):
        bot, initial_msg, seed = seed_tuple
        super(ChatHandler, self).__init__(bot, seed, initial_msg['chat']['id'])
        self.listener.set_options(timeout=timeout)
        self.listener.capture(chat__id=self.chat_id)
        if callback_query:
            # Also capture callback_query from the same user
            self.listener.capture(_=lambda msg: flavor(msg)=='callback_query', from__id=self.chat_id)

@openable
class UserHandler(helper.UserContext, DefaultRouterMixin):
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
