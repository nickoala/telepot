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

# Patch Requests for sending unicode filename
import telepot.hack


def flavor(msg):
    if 'message_id' in msg:
        return 'chat'
    elif 'id' in msg and 'data' in msg:
        return 'callback_query'
    elif 'id' in msg and 'query' in msg:
        return 'inline_query'
    elif 'result_id' in msg:
        return 'chosen_inline_result'
    else:
        raise BadFlavor(msg)


def _find_first_key(d, keys):
    for k in keys:
        if k in d:
            return k
    raise KeyError(keys)


def glance(msg, flavor='chat', long=False):
    def gl_chat():
        types = [
            'text', 'audio', 'document', 'photo', 'sticker', 'video', 'voice', 'contact', 'location', 'venue',
            'new_chat_member', 'left_chat_member',  'new_chat_title', 'new_chat_photo',  'delete_chat_photo',
            'group_chat_created', 'supergroup_chat_created', 'channel_chat_created',
            'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message',
        ]

        content_type = _find_first_key(msg, types)

        if long:
            return content_type, msg['chat']['type'], msg['chat']['id'], msg['date'], msg['message_id']
        else:
            return content_type, msg['chat']['type'], msg['chat']['id']

    def gl_callback_query():
        return msg['id'], msg['from']['id'], msg['data']

    def gl_inline_query():
        if long:
            return msg['id'], msg['from']['id'], msg['query'], msg['offset']
        else:
            return msg['id'], msg['from']['id'], msg['query']

    def gl_chosen_inline_result():
        return msg['result_id'], msg['from']['id'], msg['query']

    try:
        fn = {'chat': gl_chat,
              'callback_query': gl_callback_query,
              'inline_query': gl_inline_query,
              'chosen_inline_result': gl_chosen_inline_result}[flavor]
    except KeyError:
        raise BadFlavor(flavor)

    return fn()


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


PY_3 = sys.version_info.major >= 3
_string_type = str if PY_3 else basestring
_file_type = io.IOBase if PY_3 else file

def _isstring(s):
    return isinstance(s, _string_type)

def _isfile(f):
    return isinstance(f, _file_type)

def _strip(params, more=[]):
    return {key: value for key,value in params.items() if key not in ['self']+more}

def _rectify(params):
    def namedtuple_to_dict(value):
        if isinstance(value, list):
            return [namedtuple_to_dict(v) for v in value]
        elif isinstance(value, dict):
            return {k:namedtuple_to_dict(v) for k,v in value.items() if v is not None}
        elif isinstance(value, tuple) and hasattr(value, '_asdict'):
            return {k:namedtuple_to_dict(v) for k,v in value._asdict().items() if v is not None}
        else:
            return value

    def flatten(value):
        v = namedtuple_to_dict(value)

        if isinstance(v, (dict, list)):
            return json.dumps(v, separators=(',',':'))
        else:
            return v

    # remove None, then json-serialize if needed
    return {k: flatten(v) for k,v in params.items() if v is not None}

def _post(url, **kwargs):
    response = requests.post(url, **kwargs)

    try:
        data = response.json()
    except ValueError:  # No JSON object could be decoded
        raise BadHTTPResponse(response.status_code, response.text, response)

    if data['ok']:
        return data['result']
    else:
        description, error_code = data['description'], data['error_code']

        # Look for specific error ...
        for e in TelegramError.__subclasses__():
            n = len(e.DESCRIPTION_PATTERNS)
            if any(map(re.search, e.DESCRIPTION_PATTERNS, n*[description], n*[re.IGNORECASE])):
                raise e(description, error_code, data)

        # ... or raise generic error
        raise TelegramError(description, error_code, data)

def _dismantle_message_id_form(f):
    if isinstance(f, tuple):
        if len(f) == 2:
            return {'chat_id': f[0], 'message_id': f[1]}
        elif len(f) == 1:
            return {'inline_message_id': f[0]}
        else:
            raise RuntimeError()
    else:
        return {'inline_message_id': f}


class Bot(_BotBase):
    def __init__(self, token):
        super(Bot, self).__init__(token)

        self._router = telepot.helper.Router(flavor, {'chat': lambda msg: self.on_chat_message(msg),
                                                      'callback_query': lambda msg: self.on_callback_query(msg),
                                                      'inline_query': lambda msg: self.on_inline_query(msg),
                                                      'chosen_inline_result': lambda msg: self.on_chosen_inline_result(msg)})
                                                      # use lambda to delay evaluation of self.on_ZZZ to runtime because
                                                      # I don't want to require defining all methods right here.

    def handle(self, msg):
        self._router.route(msg)

    def getMe(self):
        return _post(self._methodurl('getMe'), timeout=self._http_timeout)

    def sendMessage(self, chat_id, text,
                    parse_mode=None, disable_web_page_preview=None,
                    disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = _strip(locals())
        return _post(self._methodurl('sendMessage'),
                     data=_rectify(p),
                     timeout=self._http_timeout)

    def forwardMessage(self, chat_id, from_chat_id, message_id, disable_notification=None):
        p = _strip(locals())
        return _post(self._methodurl('forwardMessage'),
                     data=_rectify(p),
                     timeout=self._http_timeout)

    def _sendfile(self, inputfile, filetype, params):
        method = {'photo':    'sendPhoto',
                  'audio':    'sendAudio',
                  'document': 'sendDocument',
                  'sticker':  'sendSticker',
                  'video':    'sendVideo',
                  'voice':    'sendVoice',}[filetype]

        if _isstring(inputfile):
            params[filetype] = inputfile
            return _post(self._methodurl(method),
                         data=_rectify(params),
                         timeout=self._http_timeout)
        else:
            files = {filetype: inputfile}
            return _post(self._methodurl(method),
                         data=_rectify(params),
                         files=files)

            # No timeout is given here because, for some reason, the larger the file,
            # the longer it takes for the server to respond (after upload is finished).
            # It is unclear how long timeout should be.

    def sendPhoto(self, chat_id, photo,
                  caption=None,
                  disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = _strip(locals(), more=['photo'])
        return self._sendfile(photo, 'photo', p)

    def sendAudio(self, chat_id, audio,
                  duration=None, performer=None, title=None,
                  disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = _strip(locals(), more=['audio'])
        return self._sendfile(audio, 'audio', p)

    def sendDocument(self, chat_id, document,
                     caption=None,
                     disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = _strip(locals(), more=['document'])
        return self._sendfile(document, 'document', p)

    def sendSticker(self, chat_id, sticker,
                    disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = _strip(locals(), more=['sticker'])
        return self._sendfile(sticker, 'sticker', p)

    def sendVideo(self, chat_id, video,
                  duration=None, width=None, height=None, caption=None,
                  disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = _strip(locals(), more=['video'])
        return self._sendfile(video, 'video', p)

    def sendVoice(self, chat_id, voice,
                  duration=None,
                  disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = _strip(locals(), more=['voice'])
        return self._sendfile(voice, 'voice', p)

    def sendLocation(self, chat_id, latitude, longitude,
                     disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = _strip(locals())
        return _post(self._methodurl('sendLocation'),
                     data=_rectify(p),
                     timeout=self._http_timeout)

    def sendVenue(self, chat_id, latitude, longitude, title, address,
                  foursquare_id=None,
                  disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = _strip(locals())
        return _post(self._methodurl('sendVenue'),
                     data=_rectify(p),
                     timeout=self._http_timeout)

    def sendContact(self, chat_id, phone_number, first_name,
                    last_name=None,
                    disable_notification=None, reply_to_message_id=None, reply_markup=None):
        p = _strip(locals())
        return _post(self._methodurl('sendContact'),
                     data=_rectify(p),
                     timeout=self._http_timeout)

    def sendChatAction(self, chat_id, action):
        p = _strip(locals())
        return _post(self._methodurl('sendChatAction'),
                     data=_rectify(p),
                     timeout=self._http_timeout)

    def getUserProfilePhotos(self, user_id, offset=None, limit=None):
        p = _strip(locals())
        return _post(self._methodurl('getUserProfilePhotos'),
                     data=_rectify(p),
                     timeout=self._http_timeout)

    def getFile(self, file_id):
        p = _strip(locals())
        return _post(self._methodurl('getFile'),
                     data=_rectify(p),
                     timeout=self._http_timeout)

    def kickChatMember(self, chat_id, user_id):
        p = _strip(locals())
        return _post(self._methodurl('kickChatMember'),
                     data=_rectify(p),
                     timeout=self._http_timeout)

    def unbanChatMember(self, chat_id, user_id):
        p = _strip(locals())
        return _post(self._methodurl('unbanChatMember'),
                     data=_rectify(p),
                     timeout=self._http_timeout)

    def answerCallbackQuery(self, callback_query_id, text=None, show_alert=None):
        p = _strip(locals())
        return _post(self._methodurl('answerCallbackQuery'),
                     data=_rectify(p),
                     timeout=self._http_timeout)

    def editMessageText(self, msgid_form, text,
                        parse_mode=None, disable_web_page_preview=None, reply_markup=None):
        p = _strip(locals(), more=['msgid_form'])
        p.update(_dismantle_message_id_form(msgid_form))
        return _post(self._methodurl('editMessageText'),
                     data=_rectify(p),
                     timeout=self._http_timeout)

    def editMessageCaption(self, msgid_form, caption=None, reply_markup=None):
        p = _strip(locals(), more=['msgid_form'])
        p.update(_dismantle_message_id_form(msgid_form))
        return _post(self._methodurl('editMessageCaption'),
                     data=_rectify(p),
                     timeout=self._http_timeout)

    def editMessageReplyMarkup(self, msgid_form, reply_markup=None):
        p = _strip(locals(), more=['msgid_form'])
        p.update(_dismantle_message_id_form(msgid_form))
        return _post(self._methodurl('editMessageReplyMarkup'),
                     data=_rectify(p),
                     timeout=self._http_timeout)

    def answerInlineQuery(self, inline_query_id, results,
                          cache_time=None, is_personal=None, next_offset=None,
                          switch_pm_text=None, switch_pm_parameter=None):
        p = _strip(locals())
        return _post(self._methodurl('answerInlineQuery'),
                     data=_rectify(p),
                     timeout=self._http_timeout)

    def getUpdates(self, offset=None, limit=None, timeout=None):
        p = _strip(locals())
        return _post(self._methodurl('getUpdates'),
                     data=_rectify(p),
                     timeout=self._http_timeout+(0 if timeout is None else timeout))

    def setWebhook(self, url=None, certificate=None):
        p = _strip(locals(), more=['certificate'])

        if certificate:
            files = {'certificate': certificate}
            return _post(self._methodurl('setWebhook'),
                         data=_rectify(p),
                         files=files,
                         timeout=self._http_timeout)
        else:
            return _post(self._methodurl('setWebhook'),
                         data=_rectify(p),
                         timeout=self._http_timeout)

    def download_file(self, file_id, dest):
        f = self.getFile(file_id)

        # `file_path` is optional in File object
        if 'file_path' not in f:
            raise TelegramError('No `file_path` returned', None, None)

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

    def message_loop(self, callback=None, relax=0.1, timeout=20, source=None, ordered=True, maxhold=3, run_forever=False):
        if callback is None:
            callback = self.handle
        elif isinstance(callback, dict):
            callback = flavor_router(callback)

        def handle(update):
            try:
                key = _find_first_key(update, ['message',
                                               'callback_query',
                                               'inline_query',
                                               'chosen_inline_result'])

                callback(update[key])
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
