import asyncio
import traceback
import telepot.filter


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


class Listener(object):
    def __init__(self, mic, queue):
        self._mic = mic
        self._queue = queue

    @asyncio.coroutine
    def wait(self, **kwargs):
        while 1:
            msg = yield from self._queue.get()
            if telepot.filter.ok(msg, **kwargs):
                return msg
    
    def __del__(self):
        self._mic.remove(self._queue)
