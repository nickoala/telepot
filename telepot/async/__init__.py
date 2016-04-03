import io
import json
import time
import asyncio
import aiohttp
import traceback
import re
from requests.utils import guess_filename
from concurrent.futures._base import CancelledError
import collections
import telepot
import telepot.async.helper
from ..exception import BadFlavor, BadHTTPResponse, TelegramError


def flavor_router(routing_table):
    router = telepot.async.helper.Router(telepot.flavor, routing_table)
    return router.route

                                         
class Bot(telepot._BotBase):
    def __init__(self, token, loop=None):
        super(Bot, self).__init__(token)
        self._loop = loop if loop is not None else asyncio.get_event_loop()

        self._router = telepot.async.helper.Router(telepot.flavor, {'normal': telepot.async.helper._delay_yell(self, 'on_chat_message'),
                                                                    'inline_query': telepot.async.helper._delay_yell(self, 'on_inline_query'),
                                                                    'chosen_inline_result': telepot.async.helper._delay_yell(self, 'on_chosen_inline_result')})

    @property
    def loop(self):
        return self._loop

    @asyncio.coroutine
    def handle(self, msg):
        yield from self._router.route(msg)

    @asyncio.coroutine
    def _parse(self, response):
        try:
            data = yield from response.json()
        except ValueError:
            text = yield from response.text()
            raise BadHTTPResponse(response.status, text)

        if data['ok']:
            return data['result']
        else:
            description, error_code = data['description'], data['error_code']

            # Look for specific error ...
            for e in TelegramError.__subclasses__():
                n = len(e.DESCRIPTION_PATTERNS)
                if any(map(re.search, e.DESCRIPTION_PATTERNS, n*[description], n*[re.IGNORECASE])):
                    raise e(description, error_code)

            # ... or raise generic error
            raise TelegramError(description, error_code)

    @asyncio.coroutine
    def getMe(self):
        r = yield from asyncio.wait_for(
                aiohttp.post(self._methodurl('getMe')), 
                self._http_timeout
            )
        return (yield from self._parse(r))

    @asyncio.coroutine
    def sendMessage(self, chat_id, text, parse_mode=None, disable_web_page_preview=None, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = self._strip(locals())
        r = yield from asyncio.wait_for(
                aiohttp.post(
                    self._methodurl('sendMessage'), 
                    data=self._rectify(p, allow_namedtuple=['reply_markup'])), 
                self._http_timeout
            )
        return (yield from self._parse(r))

    @asyncio.coroutine
    def forwardMessage(self, chat_id, from_chat_id, message_id, disable_notification=None):
        p = self._strip(locals())
        r = yield from asyncio.wait_for(
                aiohttp.post(
                    self._methodurl('forwardMessage'), 
                    data=self._rectify(p)), 
                self._http_timeout
            )
        return (yield from self._parse(r))

    @asyncio.coroutine
    def _sendFile(self, inputfile, filetype, params):
        method = {'photo':    'sendPhoto',
                  'audio':    'sendAudio',
                  'document': 'sendDocument',
                  'sticker':  'sendSticker',
                  'video':    'sendVideo',
                  'voice':    'sendVoice',}[filetype]

        if telepot._isstring(inputfile):            
            params[filetype] = inputfile
            r = yield from asyncio.wait_for(
                    aiohttp.post(
                        self._methodurl(method), 
                        data=self._rectify(params, allow_namedtuple=['reply_markup'])), 
                    self._http_timeout)
        else:
            if isinstance(inputfile, tuple):
                if len(inputfile) == 2:
                    filename, fileobj = inputfile
                else:
                    raise ValueError('Tuple must have exactly 2 elements: filename, fileobj')
            else:
                filename, fileobj = guess_filename(inputfile) or filetype, inputfile

            mpwriter = aiohttp.MultipartWriter('form-data')
            part = mpwriter.append(fileobj)
            part.set_content_disposition('form-data', name=filetype, filename=filename)

            r = yield from aiohttp.post(
                    self._methodurl(method), 
                    params=self._rectify(params, allow_namedtuple=['reply_markup']), 
                    data=mpwriter)

            # `_http_timeout` is not used here because, for some reason, the larger the file, 
            # the longer it takes for the server to respond (after upload is finished). It is hard to say
            # what value `_http_timeout` should be. In the future, maybe I should let user specify.

        return (yield from self._parse(r))

    @asyncio.coroutine
    def sendPhoto(self, chat_id, photo, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = self._strip(locals(), more=['photo'])
        return (yield from self._sendFile(photo, 'photo', p))

    @asyncio.coroutine
    def sendAudio(self, chat_id, audio, duration=None, performer=None, title=None, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = self._strip(locals(), more=['audio'])
        return (yield from self._sendFile(audio, 'audio', p))

    @asyncio.coroutine
    def sendDocument(self, chat_id, document, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = self._strip(locals(), more=['document'])
        return (yield from self._sendFile(document, 'document', p))

    @asyncio.coroutine
    def sendSticker(self, chat_id, sticker, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = self._strip(locals(), more=['sticker'])
        return (yield from self._sendFile(sticker, 'sticker', p))

    @asyncio.coroutine
    def sendVideo(self, chat_id, video, duration=None, width=None, height=None, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = self._strip(locals(), more=['video'])
        return (yield from self._sendFile(video, 'video', p))

    @asyncio.coroutine
    def sendVoice(self, chat_id, voice, duration=None, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = self._strip(locals(), more=['voice'])
        return (yield from self._sendFile(voice, 'voice', p))

    @asyncio.coroutine
    def sendLocation(self, chat_id, latitude, longitude, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = self._strip(locals())
        r = yield from asyncio.wait_for(
                aiohttp.post(
                    self._methodurl('sendLocation'), 
                    data=self._rectify(p, allow_namedtuple=['reply_markup'])), 
                self._http_timeout
            )
        return (yield from self._parse(r))

    @asyncio.coroutine
    def sendChatAction(self, chat_id, action):
        p = self._strip(locals())
        r = yield from asyncio.wait_for(
                aiohttp.post(
                    self._methodurl('sendChatAction'), 
                    data=self._rectify(p)), 
                self._http_timeout
            )
        return (yield from self._parse(r))

    @asyncio.coroutine
    def getUserProfilePhotos(self, user_id, offset=None, limit=None):
        p = self._strip(locals())
        r = yield from asyncio.wait_for(
                aiohttp.post(
                    self._methodurl('getUserProfilePhotos'), 
                    data=self._rectify(p)), 
                self._http_timeout
            )
        return (yield from self._parse(r))

    @asyncio.coroutine
    def getFile(self, file_id):
        p = self._strip(locals())
        r = yield from asyncio.wait_for(
                aiohttp.post(
                    self._methodurl('getFile'), 
                    data=self._rectify(p)), 
                self._http_timeout
            )
        return (yield from self._parse(r))

    @asyncio.coroutine
    def getUpdates(self, offset=None, limit=None, timeout=None):
        p = self._strip(locals())
        r = yield from asyncio.wait_for(
                aiohttp.post(
                    self._methodurl('getUpdates'), 
                    data=self._rectify(p)), 
                self._http_timeout+(0 if timeout is None else timeout)
            )
        return (yield from self._parse(r))

    @asyncio.coroutine
    def setWebhook(self, url=None, certificate=None):
        p = self._strip(locals(), more=['certificate'])

        if certificate:
            files = {'certificate': certificate}
            r = yield from asyncio.wait_for(
                    aiohttp.post(
                        self._methodurl('setWebhook'), 
                        params=self._rectify(p), 
                        data=files), 
                    self._http_timeout)
        else:
            r = yield from asyncio.wait_for(
                    aiohttp.post(
                        self._methodurl('setWebhook'), 
                        data=self._rectify(p)), 
                    self._http_timeout)

        return (yield from self._parse(r))

    @asyncio.coroutine
    def downloadFile(self, file_id, dest):
        f = yield from self.getFile(file_id)

        # `file_path` is optional in File object
        if 'file_path' not in f:
            raise TelegramError('No file_path returned', None)

        try:
            r = yield from asyncio.wait_for(
                    aiohttp.get(self._fileurl(f['file_path'])), 
                    self._http_timeout)

            d = dest if isinstance(dest, io.IOBase) else open(dest, 'wb')

            while 1:
                chunk = yield from r.content.read(self._file_chunk_size)
                if not chunk:
                    break
                d.write(chunk)
                d.flush()
        finally:
            if not isinstance(dest, io.IOBase) and 'd' in locals():
                d.close()

            if 'r' in locals():
                r.close()

    @asyncio.coroutine
    def answerInlineQuery(self, inline_query_id, results, cache_time=None, is_personal=None, next_offset=None):
        p = self._strip(locals())
        r = yield from asyncio.wait_for(
                aiohttp.post(
                    self._methodurl('answerInlineQuery'), 
                    data=self._rectify(p, allow_namedtuple=['results'])),
                timeout=self._http_timeout
            )
        return (yield from self._parse(r))

    @asyncio.coroutine
    def messageLoop(self, handler=None, source=None, ordered=True, maxhold=3):
        if handler is None:
            handler = self.handle
        elif isinstance(handler, dict):
            handler = flavor_router(handler)

        def create_task_for(msg):
            self.loop.create_task(handler(msg))

        if asyncio.iscoroutinefunction(handler):
            callback = create_task_for
        else:
            callback = handler

        def handle(update):
            try:
                if 'message' in update:
                    callback(update['message'])
                elif 'inline_query' in update:
                    callback(update['inline_query'])
                elif 'chosen_inline_result' in update:
                    callback(update['chosen_inline_result'])
                else:
                    # Do not swallow. Make sure developer knows.
                    raise BadFlavor(update)
            except:
                # Localize the error so message thread can keep going.
                traceback.print_exc()
            finally:
                return update['update_id']

        @asyncio.coroutine
        def get_from_telegram_server():
            offset = None  # running offset
            while 1:
                try:
                    result = yield from self.getUpdates(offset=offset, timeout=20)

                    if len(result) > 0:
                        # No sort. Trust server to give messages in correct order.
                        # Update offset to max(update_id) + 1
                        offset = max([handle(update) for update in result]) + 1
                except CancelledError:
                    raise
                except:
                    traceback.print_exc()
                    yield from asyncio.sleep(0.1)
                else:
                    yield from asyncio.sleep(0.1)

        def dictify(data):
            if type(data) is bytes:
                return json.loads(data.decode('utf-8'))
            elif type(data) is str:
                return json.loads(data)
            elif type(data) is dict:
                return data
            else:
                raise ValueError()

        @asyncio.coroutine
        def get_from_queue_unordered(qu):
            while 1:
                try:
                    data = yield from qu.get()
                    update = dictify(data)
                    handle(update)
                except:
                    traceback.print_exc()

        @asyncio.coroutine
        def get_from_queue(qu):
            # Here is the re-ordering mechanism, ensuring in-order delivery of updates.
            max_id = None                 # max update_id passed to callback
            buffer = collections.deque()  # keep those updates which skip some update_id
            qwait = None                  # how long to wait for updates,
                                          # because buffer's content has to be returned in time.

            while 1:
                try:
                    data = yield from asyncio.wait_for(qu.get(), qwait)
                    update = dictify(data)

                    if max_id is None:
                        # First message received, handle regardless.
                        max_id = handle(update)

                    elif update['update_id'] == max_id + 1:
                        # No update_id skipped, handle naturally.
                        max_id = handle(update)

                        # clear contagious updates in buffer
                        if len(buffer) > 0:
                            buffer.popleft()  # first element belongs to update just received, useless now.
                            while 1:
                                try:
                                    if type(buffer[0]) is dict:
                                        max_id = handle(buffer.popleft())  # updates that arrived earlier, handle them.
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
                                max_id = handle(buffer.popleft())
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

        if source is None:
            yield from get_from_telegram_server()
        elif isinstance(source, asyncio.Queue):
            if ordered:
                yield from get_from_queue(source)
            else:
                yield from get_from_queue_unordered(source)
        else:
            raise ValueError('Invalid source')


class SpeakerBot(Bot):
    def __init__(self, token, loop=None):
        super(SpeakerBot, self).__init__(token, loop)
        self._mic = telepot.async.helper.Microphone()

    @property
    def mic(self):
        return self._mic

    def create_listener(self):
        q = asyncio.Queue()
        self._mic.add(q)
        ln = telepot.async.helper.Listener(self._mic, q)
        return ln


class DelegatorBot(SpeakerBot):
    def __init__(self, token, delegation_patterns, loop=None):
        super(DelegatorBot, self).__init__(token, loop)
        self._delegate_records = [p+({},) for p in delegation_patterns]

    def handle(self, msg):
        self._mic.send(msg)

        for calculate_seed, make_coroutine_obj, dict in self._delegate_records:
            id = calculate_seed(msg)

            if id is None:
                continue
            elif isinstance(id, collections.Hashable):
                if id not in dict or dict[id].done():
                    c = make_coroutine_obj((self, msg, id))

                    if not asyncio.iscoroutine(c):
                        raise RuntimeError('You must produce a coroutine *object* as delegate.')

                    dict[id] = self._loop.create_task(c)
            else:
                c = make_coroutine_obj((self, msg, id))
                self._loop.create_task(c)
