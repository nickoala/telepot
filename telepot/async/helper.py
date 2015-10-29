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
