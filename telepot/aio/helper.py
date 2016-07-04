import asyncio
import traceback
import time
from .. import filtering, helper, exception
from .. import flavor, chat_flavors, inline_flavors

# Mirror traditional version
from ..helper import Timer, Sender, Administrator, Editor, openable


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
                    msg = await asyncio.wait_for(self._queue.get(), 0 if timeleft < 0 else timeleft)
                else:
                    msg = await self._queue.get()
            except asyncio.TimeoutError:
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


from concurrent.futures._base import CancelledError

class Answerer(object):
    """
    When processing inline queries, ensures **at most one active task** per user id.
    """

    def __init__(self, bot, loop=None):
        self._bot = bot
        self._loop = loop if loop is not None else asyncio.get_event_loop()
        self._working_tasks = {}

    def answer(self, inline_query, compute_fn, *compute_args, **compute_kwargs):
        """
        Create a task that calls ``compute fn`` (along with additional arguments
        ``*compute_args`` and ``**compute_kwargs``), then applies the returned value to
        :meth:`.Bot.answerInlineQuery` to answer the inline query.
        If a preceding task is already working for a user, that task is cancelled,
        thus ensuring at most one active task per user id.

        :param inline_query:
            The inline query to be processed. The originating user is inferred from ``msg['from']['id']``.

        :param compute_fn:
            A function whose returned value is given to :meth:`.Bot.answerInlineQuery` to send.
            May return:

            - a *list* of `InlineQueryResult <https://core.telegram.org/bots/api#inlinequeryresult>`_
            - a *tuple* whose first element is a list of `InlineQueryResult <https://core.telegram.org/bots/api#inlinequeryresult>`_,
              followed by positional arguments to be supplied to :meth:`.Bot.answerInlineQuery`
            - a *dictionary* representing keyword arguments to be supplied to :meth:`.Bot.answerInlineQuery`

        :param \*compute_args: positional arguments to ``compute_fn``
        :param \*\*compute_kwargs: keyword arguments to ``compute_fn``
        """

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


class AnswererMixin(object):
    def __init__(self):
        super(AnswererMixin, self).__init__()
        self._answerer = Answerer(self.bot)

    @property
    def answerer(self):
        return self._answerer


class CallbackQueryCoordinator(helper.CallbackQueryCoordinator):
    def augment_send(self, send_func):
        async def augmented(*aa, **kw):
            sent = await send_func(*aa, **kw)

            if self._contains_callback_data(kw):
                self._listener.capture(self._capture_criteria(message=sent),
                                       **self._capture_options[sent['chat']['type']])

            return sent
        return augmented

    def augment_edit(self, edit_func):
        async def augmented(msg_identifier, *aa, **kw):
            edited = await edit_func(msg_identifier, *aa, **kw)

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
        async def augmented(inline_query_id, results, *aa, **kw):
            response = await answer_func(inline_query_id, results, *aa, **kw)
            self._pending_ids = [filtering.pick(r, 'id') for r in results if self._contains_callback_data(r)]
            return response
        return augmented

    def augment_on_message(self, handler):
        async def augmented(msg):
            if (flavor(msg) == 'chosen_inline_result'
                    and 'inline_message_id' in msg
                    and msg['result_id'] in self._pending_ids):
                inline_message_id = msg['inline_message_id']
                self._listener.capture(self._capture_criteria(msg_identifier=inline_message_id),
                                       **self._capture_options['inline'])

            return await _yell(handler, msg)
        return augmented


class CallbackQueryAble(helper.CallbackQueryAble):
    COORDINATOR_CLASS = CallbackQueryCoordinator


class Router(helper.Router):
    async def route(self, msg, *aa, **kw):
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
        """ See :class:`.helper.Router` """
        return self._router

    async def on_message(self, msg):
        """
        Called when a message is received.
        By default, call :meth:`Router.route` to handle the message.
        """
        await self._router.route(msg)


@openable
class Monitor(helper.ListenerContext, DefaultRouterMixin):
    def __init__(self, seed_tuple, capture):
        """
        A delegate that never times-out, probably doing some kind of background monitoring
        in the application. Most naturally paired with :func:`telepot.aio.delegate.per_application`.

        :param capture: a list of capture criteria for its ``listener``
        """
        bot, initial_msg, seed = seed_tuple
        super(Monitor, self).__init__(bot, seed)

        for c in capture:
            self.listener.capture(c, timer=None)


@openable
class ChatHandler(CallbackQueryAble, helper.ChatContext, DefaultRouterMixin):
    def __init__(self, seed_tuple, timeout, enable_callback_query=True):
        """
        A delegate to handle a chat.
        Most naturally paired with :func:`telepot.aio.delegate.per_chat_id`.

        :type timeout: number of seconds
        :param timeout:
            If no message is captured after this period of time,
            an :class:`..exception.WaitTooLong` will be raised,
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
class UserHandler(CallbackQueryAble, helper.UserContext, DefaultRouterMixin):
    def __init__(self, seed_tuple, timeout, flavors=chat_flavors+inline_flavors, enable_callback_query=True):
        """
        A delegate to handle a user's actions.
        Most naturally paired with :func:`telepot.aio.delegate.per_from_id`.

        :type timeout: number of seconds
        :param timeout:
            If no message is captured after this period of time,
            an :class:`..exception.WaitTooLong` will be raised,
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
        Most naturally paired with :func:`telepot.aio.delegate.per_inline_from_id`.

        :type timeout: number of seconds
        :param timeout:
            If no message is captured after this period of time,
            an :class:`..exception.WaitTooLong` will be raised,
            causing the delegate to die.

        :type enable_callback_query: bool
        :param enable_callback_query:
            Whether to augment the bot's public methods with :class:`CallbackQueryCoordinator`
            so callback query can be handled transparently.
        """
        super(InlineUserHandler, self).__init__(seed_tuple, timeout,
                                                flavors=inline_flavors,
                                                enable_callback_query=enable_callback_query)
