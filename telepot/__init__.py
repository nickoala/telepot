import sys
import io
import time
import json
import requests
import threading
import traceback
import collections
import re

try:
    import Queue as queue
except ImportError:
    import queue

from .exception import BadFlavor, BadHTTPResponse, TelegramError

# Suppress InsecurePlatformWarning
requests.packages.urllib3.disable_warnings()


def flavor(msg):
    if 'message_id' in msg:
        return 'normal'
    elif 'query' in msg and 'id' in msg:
        return 'inline_query'
    elif 'result_id' in msg:
        return 'chosen_inline_result'
    else:
        raise BadFlavor(msg)


def _infer_content_type(msg):
    types = [
        'text', 'voice', 'sticker', 'photo', 'audio' ,'document', 'video', 'contact', 'location',
        'new_chat_participant', 'left_chat_participant',  'new_chat_title', 'new_chat_photo',  'delete_chat_photo', 'group_chat_created',
        'supergroup_chat_created', 'channel_chat_created', 'migrate_to_chat_id', 'migrate_from_chat_id',
    ]

    content_type = list(filter(lambda f: f in msg, types))

    if len(content_type) > 1:
        raise RuntimeError('Inferred multiple content types from message', msg)
    elif len(content_type) < 1:
        raise RuntimeError('Cannot infer content type from message', msg)

    return content_type[0]


def glance(msg, flavor='normal', long=False):
    def gl_message():
        content_type = _infer_content_type(msg)

        if long:
            return content_type, msg['chat']['type'], msg['chat']['id'], msg['date'], msg['message_id']
        else:
            return content_type, msg['chat']['type'], msg['chat']['id']

    def gl_inline_query():
        if long:
            return msg['id'], msg['from']['id'], msg['query'], msg['offset']
        else:
            return msg['id'], msg['from']['id'], msg['query']

    def gl_chosen_inline_result():
        return msg['result_id'], msg['from']['id'], msg['query']

    if flavor == 'normal':
        return gl_message()
    elif flavor == 'inline_query':
        return gl_inline_query()
    elif flavor == 'chosen_inline_result':
        return gl_chosen_inline_result()
    else:
        raise BadFlavor(flavor)


glance2 = glance  # alias for backward compatibility


def flance(msg, long=False):
    f = flavor(msg)
    g = glance(msg, flavor=f, long=long)
    return f,g


import telepot.helper

def flavor_router(routing_table):
    router = telepot.helper.Router(flavor, routing_table)
    return router.route


class _BotBase(object):
    def __init__(self, token):
        self._token = token

        # Ensure an exception is raised for requests that take too long
        self._http_timeout = 30

        # For streaming file download
        self._file_chunk_size = 65536

    def _fileurl(self, path):
        return 'https://api.telegram.org/file/bot%s/%s' % (self._token, path)

    def _methodurl(self, method):
        return 'https://api.telegram.org/bot%s/%s' % (self._token, method)

    def _strip(self, params, more=[]):
        return {key: value for key,value in params.items() if key not in ['self']+more}

    def _rectify(self, params, allow_namedtuple=[]):
        # For those parameters that accept namedtuples as values,
        # use `_asdict()` to obtain dictionary representations.
        def ensure_dict(value):
            if isinstance(value, list):
                return [ensure_dict(e) for e in value]
            elif isinstance(value, tuple):
                return {k:v for k,v in value._asdict().items() if v is not None}
            else:
                return {k:v for k,v in value.items() if v is not None}

        def flatten(value, possible_namedtuple):
            v = ensure_dict(value) if possible_namedtuple else value

            if isinstance(v, (dict, list)):
                # json-serialize for non-simple values
                return json.dumps(v, separators=(',',':'))
            else:
                return v

        # remove None, then json-serialize if needed
        return {k: flatten(v, k in allow_namedtuple) for k,v in params.items() if v is not None}


PY_3 = sys.version_info.major >= 3
_string_type = str if PY_3 else basestring
_file_type = io.IOBase if PY_3 else file

def _isstring(s):
    return isinstance(s, _string_type)

def _isfile(f):
    return isinstance(f, _file_type)


class Bot(_BotBase):
    def __init__(self, token):
        super(Bot, self).__init__(token)

        self._router = telepot.helper.Router(flavor, {'normal': lambda msg: self.on_chat_message(msg),
                                                      'inline_query': lambda msg: self.on_inline_query(msg),
                                                      'chosen_inline_result': lambda msg: self.on_chosen_inline_result(msg)})
                                                      # use lambda to delay evaluation of self.on_ZZZ to runtime because 
                                                      # I don't want to require defining all methods right here.

    def handle(self, msg):
        self._router.route(msg)

    def _parse(self, response):
        try:
            data = response.json()
        except ValueError:  # No JSON object could be decoded
            raise BadHTTPResponse(response.status_code, response.text)

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

    def getMe(self):
        r = requests.post(self._methodurl('getMe'), timeout=self._http_timeout)
        return self._parse(r)

    def sendMessage(self, chat_id, text, parse_mode=None, disable_web_page_preview=None, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = self._strip(locals())
        r = requests.post(self._methodurl('sendMessage'),
                          data=self._rectify(p, allow_namedtuple=['reply_markup']),
                          timeout=self._http_timeout)
        return self._parse(r)

    def forwardMessage(self, chat_id, from_chat_id, message_id, disable_notification=None):
        p = self._strip(locals())
        r = requests.post(self._methodurl('forwardMessage'),
                          data=self._rectify(p),
                          timeout=self._http_timeout)
        return self._parse(r)

    def _sendFile(self, inputfile, filetype, params):
        method = {'photo':    'sendPhoto',
                  'audio':    'sendAudio',
                  'document': 'sendDocument',
                  'sticker':  'sendSticker',
                  'video':    'sendVideo',
                  'voice':    'sendVoice',}[filetype]

        if _isstring(inputfile):
            params[filetype] = inputfile
            r = requests.post(self._methodurl(method),
                              data=self._rectify(params, allow_namedtuple=['reply_markup']),
                              timeout=self._http_timeout)
        else:
            files = {filetype: inputfile}
            r = requests.post(self._methodurl(method),
                              data=self._rectify(params, allow_namedtuple=['reply_markup']),
                              files=files)

            # `self._http_timeout` is not used here because, for some reason, the larger the file,
            # the longer it takes for the server to respond (after upload is finished). It is hard to say
            # what value `self._http_timeout` should be. In the future, maybe I should let user specify.

        return self._parse(r)

    def sendPhoto(self, chat_id, photo, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = self._strip(locals(), more=['photo'])
        return self._sendFile(photo, 'photo', p)

    def sendAudio(self, chat_id, audio, duration=None, performer=None, title=None, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = self._strip(locals(), more=['audio'])
        return self._sendFile(audio, 'audio', p)

    def sendDocument(self, chat_id, document, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = self._strip(locals(), more=['document'])
        return self._sendFile(document, 'document', p)

    def sendSticker(self, chat_id, sticker, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = self._strip(locals(), more=['sticker'])
        return self._sendFile(sticker, 'sticker', p)

    def sendVideo(self, chat_id, video, duration=None, width=None, height=None, caption=None, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = self._strip(locals(), more=['video'])
        return self._sendFile(video, 'video', p)

    def sendVoice(self, chat_id, voice, duration=None, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = self._strip(locals(), more=['voice'])
        return self._sendFile(voice, 'voice', p)

    def sendLocation(self, chat_id, latitude, longitude, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = self._strip(locals())
        r = requests.post(self._methodurl('sendLocation'),
                          data=self._rectify(p, allow_namedtuple=['reply_markup']),
                          timeout=self._http_timeout)
        return self._parse(r)

    def sendChatAction(self, chat_id, action):
        p = self._strip(locals())
        r = requests.post(self._methodurl('sendChatAction'),
                          data=self._rectify(p),
                          timeout=self._http_timeout)
        return self._parse(r)

    def getUserProfilePhotos(self, user_id, offset=None, limit=None):
        p = self._strip(locals())
        r = requests.post(self._methodurl('getUserProfilePhotos'),
                          data=self._rectify(p),
                          timeout=self._http_timeout)
        return self._parse(r)

    def getFile(self, file_id):
        p = self._strip(locals())
        r = requests.post(self._methodurl('getFile'),
                          data=self._rectify(p),
                          timeout=self._http_timeout)
        return self._parse(r)

    def getUpdates(self, offset=None, limit=None, timeout=None):
        p = self._strip(locals())
        r = requests.post(self._methodurl('getUpdates'),
                          data=self._rectify(p),
                          timeout=self._http_timeout+(0 if timeout is None else timeout))
        return self._parse(r)

    def setWebhook(self, url=None, certificate=None):
        p = self._strip(locals(), more=['certificate'])

        if certificate:
            files = {'certificate': certificate}
            r = requests.post(self._methodurl('setWebhook'),
                              data=self._rectify(p),
                              files=files,
                              timeout=self._http_timeout)
        else:
            r = requests.post(self._methodurl('setWebhook'),
                              data=self._rectify(p),
                              timeout=self._http_timeout)

        return self._parse(r)

    def downloadFile(self, file_id, dest):
        f = self.getFile(file_id)

        # `file_path` is optional in File object
        if 'file_path' not in f:
            raise TelegramError('No file_path returned', None)

        try:
            r = requests.get(self._fileurl(f['file_path']), stream=True, timeout=self._http_timeout)

            d = dest if _isfile(dest) else open(dest, 'wb')

            for chunk in r.iter_content(chunk_size=self._file_chunk_size):
                if chunk:
                    d.write(chunk)
                    d.flush()
        finally:
            if not _isfile(dest) and 'd' in locals():
                d.close()

            if 'r' in locals():
                r.close()

    def answerInlineQuery(self, inline_query_id, results, cache_time=None, is_personal=None, next_offset=None):
        p = self._strip(locals())
        r = requests.post(self._methodurl('answerInlineQuery'),
                          data=self._rectify(p, allow_namedtuple=['results']),
                          timeout=self._http_timeout)
        return self._parse(r)

    def notifyOnMessage(self, callback=None, relax=0.1, timeout=20, source=None, ordered=True, maxhold=3, run_forever=False):
        if callback is None:
            callback = self.handle
        elif isinstance(callback, dict):
            callback = flavor_router(callback)

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

        def get_from_telegram_server():
            offset = None  # running offset
            while 1:
                try:
                    result = self.getUpdates(offset=offset, timeout=timeout)

                    if len(result) > 0:
                        # No sort. Trust server to give messages in correct order.
                        # Update offset to max(update_id) + 1
                        offset = max([handle(update) for update in result]) + 1
                except:
                    traceback.print_exc()
                finally:
                    time.sleep(relax)

        def dictify3(data):
            if type(data) is bytes:
                return json.loads(data.decode('utf-8'))
            elif type(data) is str:
                return json.loads(data)
            elif type(data) is dict:
                return data
            else:
                raise ValueError()

        def dictify27(data):
            if type(data) in [str, unicode]:
                return json.loads(data)
            elif type(data) is dict:
                return data
            else:
                raise ValueError()

        def get_from_queue_unordered(qu):
            dictify = dictify3 if sys.version_info >= (3,) else dictify27
            while 1:
                try:
                    data = qu.get(block=True)
                    update = dictify(data)
                    handle(update)
                except:
                    traceback.print_exc()

        def get_from_queue(qu):
            dictify = dictify3 if sys.version_info >= (3,) else dictify27

            # Here is the re-ordering mechanism, ensuring in-order delivery of updates.
            max_id = None                 # max update_id passed to callback
            buffer = collections.deque()  # keep those updates which skip some update_id
            qwait = None                  # how long to wait for updates,
                                          # because buffer's content has to be returned in time.

            while 1:
                try:
                    data = qu.get(block=True, timeout=qwait)
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

                except queue.Empty:
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
            t = threading.Thread(target=get_from_telegram_server)
        elif isinstance(source, queue.Queue):
            if ordered:
                t = threading.Thread(target=get_from_queue, args=(source,))
            else:
                t = threading.Thread(target=get_from_queue_unordered, args=(source,))
        else:
            raise ValueError('Invalid source')

        t.daemon = True  # need this for main thread to be killable by Ctrl-C
        t.start()

        if run_forever:
            while 1:
                time.sleep(10)


import inspect

class SpeakerBot(Bot):
    def __init__(self, token):
        super(SpeakerBot, self).__init__(token)
        self._mic = telepot.helper.Microphone()

    @property
    def mic(self):
        return self._mic

    def create_listener(self):
        q = queue.Queue()
        self._mic.add(q)
        ln = telepot.helper.Listener(self._mic, q)
        return ln


class DelegatorBot(SpeakerBot):
    def __init__(self, token, delegation_patterns):
        super(DelegatorBot, self).__init__(token)
        self._delegate_records = [p+({},) for p in delegation_patterns]

    def _startable(self, delegate):
        return ((hasattr(delegate, 'start') and inspect.ismethod(delegate.start)) and
                (hasattr(delegate, 'is_alive') and inspect.ismethod(delegate.is_alive)))

    def _tuple_is_valid(self, t):
        return len(t) == 3 and callable(t[0]) and type(t[1]) in [list, tuple] and type(t[2]) is dict

    def _ensure_startable(self, delegate):
        if self._startable(delegate):
            return delegate
        elif callable(delegate):
            return threading.Thread(target=delegate)
        elif type(delegate) is tuple and self._tuple_is_valid(delegate):
            func, args, kwargs = delegate
            return threading.Thread(target=func, args=args, kwargs=kwargs)
        else:
            raise RuntimeError('Delegate does not have the required methods, is not callable, and is not a valid tuple.')

    def handle(self, msg):
        self._mic.send(msg)

        for calculate_seed, make_delegate, dict in self._delegate_records:
            id = calculate_seed(msg)

            if id is None:
                continue
            elif isinstance(id, collections.Hashable):
                if id not in dict or not dict[id].is_alive():
                    d = make_delegate((self, msg, id))
                    d = self._ensure_startable(d)

                    dict[id] = d
                    dict[id].start()
            else:
                d = make_delegate((self, msg, id))
                d = self._ensure_startable(d)
                d.start()
