import asyncio
import time
import traceback
import collections
from concurrent.futures._base import CancelledError

from . import flavor_router

from ..loop import _extract_message, _dictify
from .. import exception


class GetUpdatesLoop(object):
    def __init__(self, bot, on_update):
        self._bot = bot
        self._update_handler = on_update

    async def run_forever(self, relax=0.1, offset=None, timeout=20, allowed_updates=None):
        """
        Process new updates in infinity loop

        :param relax: float
        :param offset: int
        :param timeout: int
        :param allowed_updates: bool
        """
        while 1:
            try:
                result = await self._bot.getUpdates(offset=offset,
                                                    timeout=timeout,
                                                    allowed_updates=allowed_updates)

                # Once passed, this parameter is no longer needed.
                allowed_updates = None

                # No sort. Trust server to give messages in correct order.
                for update in result:
                    self._update_handler(update)
                    offset = update['update_id'] + 1

            except CancelledError:
                break
            except exception.BadHTTPResponse as e:
                traceback.print_exc()

                # Servers probably down. Wait longer.
                if e.status == 502:
                    await asyncio.sleep(30)
            except:
                traceback.print_exc()
                await asyncio.sleep(relax)
            else:
                await asyncio.sleep(relax)


def _infer_handler_function(bot, h):
    if h is None:
        handler = bot.handle
    elif isinstance(h, dict):
        handler = flavor_router(h)
    else:
        handler = h

    def create_task_for(msg):
        bot.loop.create_task(handler(msg))

    if asyncio.iscoroutinefunction(handler):
        return create_task_for
    else:
        return handler


class MessageLoop(object):
    def __init__(self, bot, handle=None):
        self._bot = bot
        self._handle = _infer_handler_function(bot, handle)
        self._task = None

    async def run_forever(self, *args, **kwargs):
        updatesloop = GetUpdatesLoop(self._bot,
                                     lambda update:
                                         self._handle(_extract_message(update)[1]))

        self._task = self._bot.loop.create_task(updatesloop.run_forever(*args, **kwargs))

        self._bot.scheduler.on_event(self._handle)

    def cancel(self):
        self._task.cancel()


class Webhook(object):
    def __init__(self, bot, handle=None):
        self._bot = bot
        self._handle = _infer_handler_function(bot, handle)

    async def run_forever(self):
        self._bot.scheduler.on_event(self._handle)

    def feed(self, data):
        update = _dictify(data)
        self._handle(_extract_message(update)[1])


class OrderedWebhook(object):
    def __init__(self, bot, handle=None):
        self._bot = bot
        self._handle = _infer_handler_function(bot, handle)
        self._update_queue = asyncio.Queue(loop=bot.loop)

    async def run_forever(self, maxhold=3):
        self._bot.scheduler.on_event(self._handle)

        def extract_handle(update):
            try:
                self._handle(_extract_message(update)[1])
            except:
                # Localize the error so message thread can keep going.
                traceback.print_exc()
            finally:
                return update['update_id']

        # Here is the re-ordering mechanism, ensuring in-order delivery of updates.
        max_id = None                 # max update_id passed to callback
        buffer = collections.deque()  # keep those updates which skip some update_id
        qwait = None                  # how long to wait for updates,
                                      # because buffer's content has to be returned in time.

        while 1:
            try:
                update = await asyncio.wait_for(self._update_queue.get(), qwait)

                if max_id is None:
                    # First message received, handle regardless.
                    max_id = extract_handle(update)

                elif update['update_id'] == max_id + 1:
                    # No update_id skipped, handle naturally.
                    max_id = extract_handle(update)

                    # clear contagious updates in buffer
                    if len(buffer) > 0:
                        buffer.popleft()  # first element belongs to update just received, useless now.
                        while 1:
                            try:
                                if type(buffer[0]) is dict:
                                    max_id = extract_handle(buffer.popleft())  # updates that arrived earlier, handle them.
                                else:
                                    break  # gap, no more contagious updates
                            except IndexError:
                                break  # buffer empty

                elif update['update_id'] > max_id + 1:
                    # Update arrives pre-maturely, insert to buffer.
                    nbuf = len(buffer)
                    if update['update_id'] <= max_id + nbuf:
                        # buffer long enough, put update at position
                        buffer[update['update_id'] - max_id - 1] = update
                    else:
                        # buffer too short, lengthen it
                        expire = time.time() + maxhold
                        for a in range(nbuf, update['update_id']-max_id-1):
                            buffer.append(expire)  # put expiry time in gaps
                        buffer.append(update)

                else:
                    pass  # discard

            except asyncio.TimeoutError:
                # debug message
                # print('Timeout')

                # some buffer contents have to be handled
                # flush buffer until a non-expired time is encountered
                while 1:
                    try:
                        if type(buffer[0]) is dict:
                            max_id = extract_handle(buffer.popleft())
                        else:
                            expire = buffer[0]
                            if expire <= time.time():
                                max_id += 1
                                buffer.popleft()
                            else:
                                break  # non-expired
                    except IndexError:
                        break  # buffer empty
            except:
                traceback.print_exc()
            finally:
                try:
                    # don't wait longer than next expiry time
                    qwait = buffer[0] - time.time()
                    if qwait < 0:
                        qwait = 0
                except IndexError:
                    # buffer empty, can wait forever
                    qwait = None

                # debug message
                # print ('Buffer:', str(buffer), ', To Wait:', qwait, ', Max ID:', max_id)

    def feed(self, data):
        update = _dictify(data)
        self._update_queue.put_nowait(update)
