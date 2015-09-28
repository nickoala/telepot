import time
import traceback
import telepot
import telepot.filter

try:
    import Queue as queue
except ImportError:
    import queue

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
            except queue.Full:
                traceback.print_exc()
                pass

class WaitTooLong(telepot.TelepotException):
    pass

class Listener(object):
    def __init__(self, mic, queue, timeout):
        self._mic = mic
        self._queue = queue
        self._timeout = timeout

    def setTimeout(self, seconds):
        self._timeout = seconds

    def wait(self, *args, **kwargs):
        end = time.time() + self._timeout
        while 1:
            timeleft = end - time.time()
            
            if timeleft < 0:
                raise WaitTooLong()

            try:
                msg = self._queue.get(block=True, timeout=timeleft)
            except queue.Empty:
                raise WaitTooLong()

            if telepot.filter.ok(msg, *args, **kwargs):
                return msg
    
    def __del__(self):
        self._mic.remove(self._queue)
