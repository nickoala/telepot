import asyncio
import traceback
from .. import filtering, helper, exception
from .. import (
    flavor, chat_flavors, inline_flavors, is_event,
    message_identifier, origin_identifier)

# Mirror traditional version
from ..helper import (
    Sender, Administrator, Editor, openable,
    StandardEventScheduler, StandardEventMixin)


async def _invoke(fn, *args, **kwargs):
    if asyncio.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    else:
        return fn(*args, **kwargs)


def _create_invoker(obj, method_name):
    async def d(*a, **kw):
        method = getattr(obj, method_name)
        return await _invoke(method, *a, **kw)
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
        if not self._patterns:
            raise RuntimeError('Listener has nothing to capture')

        while 1:
            msg = await self._queue.get()

            if any(map(lambda p: filtering.match_all(msg, p), self._patterns)):
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

                ans = await _invoke(compute_fn, *compute_args, **compute_kwargs)

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


class AnswererMixin(helper.AnswererMixin):
    Answerer = Answerer  # use async Answerer class


class CallbackQueryCoordinator(helper.CallbackQueryCoordinator):
    def augment_send(self, send_func):
        async def augmented(*aa, **kw):
            sent = await send_func(*aa, **kw)

            if self._enable_chat and self._contains_callback_data(kw):
                self.capture_origin(message_identifier(sent))

            return sent
        return augmented

    def augment_edit(self, edit_func):
        async def augmented(msg_identifier, *aa, **kw):
            edited = await edit_func(msg_identifier, *aa, **kw)

            if (edited is True and self._enable_inline) or (isinstance(edited, dict) and self._enable_chat):
                if self._contains_callback_data(kw):
                    self.capture_origin(msg_identifier)
                else:
                    self.uncapture_origin(msg_identifier)

            return edited
        return augmented

    def augment_delete(self, delete_func):
        async def augmented(msg_identifier, *aa, **kw):
            deleted = await delete_func(msg_identifier, *aa, **kw)

            if deleted is True:
                self.uncapture_origin(msg_identifier)

            return deleted
        return augmented

    def augment_on_message(self, handler):
        async def augmented(msg):
            if (self._enable_inline
                    and flavor(msg) == 'chosen_inline_result'
                    and 'inline_message_id' in msg):
                inline_message_id = msg['inline_message_id']
                self.capture_origin(inline_message_id)

            return await _invoke(handler, msg)
        return augmented


class InterceptCallbackQueryMixin(helper.InterceptCallbackQueryMixin):
    CallbackQueryCoordinator = CallbackQueryCoordinator


class IdleEventCoordinator(helper.IdleEventCoordinator):
    def augment_on_message(self, handler):
        async def augmented(msg):
            # Reset timer if this is an external message
            is_event(msg) or self.refresh()
            return await _invoke(handler, msg)
        return augmented

    def augment_on_close(self, handler):
        async def augmented(ex):
            try:
                if self._timeout_event:
                    self._scheduler.cancel(self._timeout_event)
                    self._timeout_event = None
            # This closing may have been caused by my own timeout, in which case
            # the timeout event can no longer be found in the scheduler.
            except exception.EventNotFound:
                self._timeout_event = None
            return await _invoke(handler, ex)
        return augmented


class IdleTerminateMixin(helper.IdleTerminateMixin):
    IdleEventCoordinator = IdleEventCoordinator


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

        return await _invoke(fn, msg, *args, **kwargs)


class DefaultRouterMixin(object):
    def __init__(self, *args, **kwargs):
        self._router = Router(flavor, {'chat': _create_invoker(self, 'on_chat_message'),
                                       'callback_query': _create_invoker(self, 'on_callback_query'),
                                       'inline_query': _create_invoker(self, 'on_inline_query'),
                                       'chosen_inline_result': _create_invoker(self, 'on_chosen_inline_result'),
                                       'shipping_query': _create_invoker(self, 'on_shipping_query'),
                                       'pre_checkout_query': _create_invoker(self, 'on_pre_checkout_query'),
                                       '_idle': _create_invoker(self, 'on__idle')})

        super(DefaultRouterMixin, self).__init__(*args, **kwargs)

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
    def __init__(self, seed_tuple, capture, **kwargs):
        """
        A delegate that never times-out, probably doing some kind of background monitoring
        in the application. Most naturally paired with :func:`telepot.aio.delegate.per_application`.

        :param capture: a list of patterns for ``listener`` to capture
        """
        bot, initial_msg, seed = seed_tuple
        super(Monitor, self).__init__(bot, seed, **kwargs)

        for pattern in capture:
            self.listener.capture(pattern)


@openable
class ChatHandler(helper.ChatContext,
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
class UserHandler(helper.UserContext,
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
class CallbackQueryOriginHandler(helper.CallbackQueryOriginContext,
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


@openable
class InvoiceHandler(helper.InvoiceContext,
                     DefaultRouterMixin,
                     StandardEventMixin,
                     IdleTerminateMixin):
    def __init__(self, seed_tuple, **kwargs):
        """
        A delegate to handle messages related to an invoice.
        """
        bot, initial_msg, seed = seed_tuple
        super(InvoiceHandler, self).__init__(bot, seed, **kwargs)

        self.listener.capture([{'invoice_payload': self.payload}])
        self.listener.capture([{'successful_payment': {'invoice_payload': self.payload}}])
