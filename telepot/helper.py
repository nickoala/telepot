import time
import traceback
import telepot
import telepot.filter
from functools import partial

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
    def __init__(self, mic, q):
        self._mic = mic
        self._queue = q

        self.timeout = None

    def wait(self, **kwargs):
        if self.timeout is None:
            while 1:
                msg = self._queue.get(block=True)

                if telepot.filter.ok(msg, **kwargs):
                    return msg
        else:
            end = time.time() + self.timeout

            while 1:
                timeleft = end - time.time()

                if timeleft < 0:
                    raise WaitTooLong()

                try:
                    msg = self._queue.get(block=True, timeout=timeleft)
                except queue.Empty:
                    raise WaitTooLong()

                if telepot.filter.ok(msg, **kwargs):
                    return msg
    
    def __del__(self):
        self._mic.remove(self._queue)


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
                       'sendChatAction',]:
            setattr(self, method, partial(getattr(bot, method), chat_id))
            # Essentially doing:
            #   self.sendMessage = partial(bot.sendMessage, chat_id)


class ChatHandler(object):
    def __init__(self, bot, msg, *args):
        self._bot = bot
        self._initial_msg = msg
        self._chat_id = msg['chat']['id']
        self._listener = bot.create_listener()
        self._sender = Sender(bot, self._chat_id)

    @property
    def chat_id(self):
        return self._chat_id

    @property
    def initial_message(self):
        return self._initial_msg

    @property
    def bot(self):
        return self._bot

    @property
    def listener(self):
        return self._listener

    @property
    def sender(self):
        return self._sender
