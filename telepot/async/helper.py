import asyncio
import traceback
import time
import telepot.helper
import telepot.filtering


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
                    raise telepot.helper.WaitTooLong()

                try:
                    msg = yield from asyncio.wait_for(self._queue.get(), timeleft)
                except asyncio.TimeoutError:
                    raise telepot.helper.WaitTooLong()

                if meet_some_criteria(msg):
                    return msg


from concurrent.futures._base import CancelledError

class Answerer(object):
    def __init__(self, bot, compute, loop=None):
        self._bot = bot
        self._compute = compute
        self._loop = loop if loop is not None else asyncio.get_event_loop()
        self._working_tasks = {}

    @asyncio.coroutine
    def _compute_and_answer(self, inline_query):
        try:
            from_id = inline_query['from']['id']
            query_id = inline_query['id']

            if asyncio.iscoroutinefunction(self._compute):
                r = yield from self._compute(inline_query)
            else:
                r = self._compute(inline_query)

            if isinstance(r, list):
                yield from self._bot.answerInlineQuery(query_id, r)
            elif isinstance(r, tuple):
                yield from self._bot.answerInlineQuery(query_id, *r)
            elif isinstance(r, dict):
                yield from self._bot.answerInlineQuery(query_id, **r)
            else:
                raise ValueError('Invalid result format')
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

    def answer(self, inline_query):
        from_id = inline_query['from']['id']

        if from_id in self._working_tasks:
            self._working_tasks[from_id].cancel()

        t = self._loop.create_task(self._compute_and_answer(inline_query))
        self._working_tasks[from_id] = t
