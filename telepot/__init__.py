import sys
import io
import time
import json
import threading
import traceback
import collections

try:
    import Queue as queue
except ImportError:
    import queue

# Patch urllib3 for sending unicode filename
from . import hack

from . import exception

def flavor(msg):
    """
    There are five message flavors:

    - ``chat``
    - ``edited_chat``
    - ``callback_query``
    - ``inline_query``
    - ``chosen_inline_result``
    """
    if 'message_id' in msg:
        if 'edit_date' in msg:
            return 'edited_chat'
        else:
            return 'chat'
    elif 'id' in msg and 'data' in msg:
        return 'callback_query'
    elif 'id' in msg and 'query' in msg:
        return 'inline_query'
    elif 'result_id' in msg:
        return 'chosen_inline_result'
    else:
        raise exception.BadFlavor(msg)


def _find_first_key(d, keys):
    for k in keys:
        if k in d:
            return k
    raise KeyError(keys)


all_content_types = [
    'text', 'audio', 'document', 'photo', 'sticker', 'video', 'voice',
    'contact', 'location', 'venue', 'new_chat_member', 'left_chat_member',  'new_chat_title',
    'new_chat_photo',  'delete_chat_photo', 'group_chat_created', 'supergroup_chat_created',
    'channel_chat_created', 'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message',
]

def glance(msg, flavor='chat', long=False):
    """
    Extract "headline" info about a message.
    Use parameter ``long`` to control whether a short or long tuple is returned.

    When ``flavor`` is ``chat`` or ``edited_chat``
    (``msg`` being a `Message <https://core.telegram.org/bots/api#message>`_ object):

    - short: (content_type, ``msg['chat']['type']``, ``msg['chat']['id']``)
    - long: (content_type, ``msg['chat']['type']``, ``msg['chat']['id']``, ``msg['date']``, ``msg['message_id']``)

    *content_type* can be: ``text``, ``audio``, ``document``, ``photo``, ``sticker``, ``video``, ``voice``,
    ``contact``, ``location``, ``venue``, ``new_chat_member``, ``left_chat_member``, ``new_chat_title``,
    ``new_chat_photo``, ``delete_chat_photo``, ``group_chat_created``, ``supergroup_chat_created``,
    ``channel_chat_created``, ``migrate_to_chat_id``, ``migrate_from_chat_id``, ``pinned_message``.

    When ``flavor`` is ``callback_query``
    (``msg`` being a `CallbackQuery <https://core.telegram.org/bots/api#callbackquery>`_ object):

    - regardless: (``msg['id']``, ``msg['from']['id']``, ``msg['data']``)

    When ``flavor`` is ``inline_query``
    (``msg`` being a `InlineQuery <https://core.telegram.org/bots/api#inlinequery>`_ object):

    - short: (``msg['id']``, ``msg['from']['id']``, ``msg['query']``)
    - long: (``msg['id']``, ``msg['from']['id']``, ``msg['query']``, ``msg['offset']``)

    When ``flavor`` is ``chosen_inline_result``
    (``msg`` being a `ChosenInlineResult <https://core.telegram.org/bots/api#choseninlineresult>`_ object):

    - regardless: (``msg['result_id']``, ``msg['from']['id']``, ``msg['query']``)
    """
    def gl_chat():
        content_type = _find_first_key(msg, all_content_types)

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
              'edited_chat': gl_chat,
              'callback_query': gl_callback_query,
              'inline_query': gl_inline_query,
              'chosen_inline_result': gl_chosen_inline_result}[flavor]
    except KeyError:
        raise exception.BadFlavor(flavor)

    return fn()


def flance(msg, long=False):
    """
    A combination of :meth:`telepot.flavor` and :meth:`telepot.glance`,
    return a 2-tuple (flavor, headline_info), where *headline_info* is whatever extracted by
    ``glance`` depending on the message flavor and the ``long`` parameter.
    """
    f = flavor(msg)
    g = glance(msg, flavor=f, long=long)
    return f,g


from . import helper

def flavor_router(routing_table):
    router = helper.Router(flavor, routing_table)
    return router.route


class _BotBase(object):
    def __init__(self, token):
        self._token = token
        self._file_chunk_size = 65536

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

def message_identifier(msg):
    """
    Extract an identifier for message editing. Useful with :meth:`telepot.Bot.editMessageText`
    and similar methods.

    ``msg`` is expected to be of flavor ``chat`` or ``choson_inline_result``.
    """
    if 'chat' in msg and 'message_id' in msg:
        return msg['chat']['id'], msg['message_id']
    elif 'inline_message_id' in msg:
        return msg['inline_message_id']
    else:
        raise ValueError()

def _dismantle_message_identifier(f):
    if isinstance(f, tuple):
        if len(f) == 2:
            return {'chat_id': f[0], 'message_id': f[1]}
        elif len(f) == 1:
            return {'inline_message_id': f[0]}
        else:
            raise ValueError()
    else:
        return {'inline_message_id': f}


from . import api

class Bot(_BotBase):
    def __init__(self, token):
        super(Bot, self).__init__(token)

        self._router = helper.Router(flavor, {'chat': lambda msg: self.on_chat_message(msg),
                                              'edited_chat': lambda msg: self.on_edited_chat_message(msg),
                                              'callback_query': lambda msg: self.on_callback_query(msg),
                                              'inline_query': lambda msg: self.on_inline_query(msg),
                                              'chosen_inline_result': lambda msg: self.on_chosen_inline_result(msg)})
                                              # use lambda to delay evaluation of self.on_ZZZ to runtime because
                                              # I don't want to require defining all methods right here.

    def handle(self, msg):
        self._router.route(msg)

    def _api_request(self, method, params=None, files=None, **kwargs):
        return api.request((self._token, method, params, files), **kwargs)

    def getMe(self):
        """ See: https://core.telegram.org/bots/api#getme """
        return self._api_request('getMe')

    def sendMessage(self, chat_id, text,
                    parse_mode=None, disable_web_page_preview=None,
                    disable_notification=None, reply_to_message_id=None, reply_markup=None):
        """ See: https://core.telegram.org/bots/api#sendmessage """
        p = _strip(locals())
        return self._api_request('sendMessage', _rectify(p))

    def forwardMessage(self, chat_id, from_chat_id, message_id, disable_notification=None):
        """ See: https://core.telegram.org/bots/api#forwardmessage """
        p = _strip(locals())
        return self._api_request('forwardMessage', _rectify(p))

    def _sendfile(self, inputfile, filetype, params):
        method = {'photo':    'sendPhoto',
                  'audio':    'sendAudio',
                  'document': 'sendDocument',
                  'sticker':  'sendSticker',
                  'video':    'sendVideo',
                  'voice':    'sendVoice',}[filetype]

        if _isstring(inputfile):
            params[filetype] = inputfile
            return self._api_request(method, _rectify(params))
        else:
            files = {filetype: inputfile}
            return self._api_request(method, _rectify(params), files)

    def sendPhoto(self, chat_id, photo,
                  caption=None,
                  disable_notification=None, reply_to_message_id=None, reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#sendphoto

        :param photo: a string indicating a ``file_id`` on server,
                      a file-like object as obtained by ``open()`` or ``urlopen()``,
                      or a (filename, file-like object) tuple.
                      If the file-like object is obtained by ``urlopen()``, you most likely
                      have to supply a filename because Telegram servers require to know
                      the file extension.
                      If the filename contains non-ASCII characters and you are using Python 2.7,
                      make sure the filename is a unicode string.
        """
        p = _strip(locals(), more=['photo'])
        return self._sendfile(photo, 'photo', p)

    def sendAudio(self, chat_id, audio,
                  duration=None, performer=None, title=None,
                  disable_notification=None, reply_to_message_id=None, reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#sendaudio

        :param audio: Same as ``photo`` in :meth:`telepot.Bot.sendPhoto`
        """
        p = _strip(locals(), more=['audio'])
        return self._sendfile(audio, 'audio', p)

    def sendDocument(self, chat_id, document,
                     caption=None,
                     disable_notification=None, reply_to_message_id=None, reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#senddocument

        :param document: Same as ``photo`` in :meth:`telepot.Bot.sendPhoto`
        """
        p = _strip(locals(), more=['document'])
        return self._sendfile(document, 'document', p)

    def sendSticker(self, chat_id, sticker,
                    disable_notification=None, reply_to_message_id=None, reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#sendsticker

        :param sticker: Same as ``photo`` in :meth:`telepot.Bot.sendPhoto`
        """
        p = _strip(locals(), more=['sticker'])
        return self._sendfile(sticker, 'sticker', p)

    def sendVideo(self, chat_id, video,
                  duration=None, width=None, height=None, caption=None,
                  disable_notification=None, reply_to_message_id=None, reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#sendvideo

        :param video: Same as ``photo`` in :meth:`telepot.Bot.sendPhoto`
        """
        p = _strip(locals(), more=['video'])
        return self._sendfile(video, 'video', p)

    def sendVoice(self, chat_id, voice,
                  duration=None,
                  disable_notification=None, reply_to_message_id=None, reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#sendvoice

        :param voice: Same as ``photo`` in :meth:`telepot.Bot.sendPhoto`
        """
        p = _strip(locals(), more=['voice'])
        return self._sendfile(voice, 'voice', p)

    def sendLocation(self, chat_id, latitude, longitude,
                     disable_notification=None, reply_to_message_id=None, reply_markup=None):
        """ See: https://core.telegram.org/bots/api#sendlocation """
        p = _strip(locals())
        return self._api_request('sendLocation', _rectify(p))

    def sendVenue(self, chat_id, latitude, longitude, title, address,
                  foursquare_id=None,
                  disable_notification=None, reply_to_message_id=None, reply_markup=None):
        """ See: https://core.telegram.org/bots/api#sendvenue """
        p = _strip(locals())
        return self._api_request('sendVenue', _rectify(p))

    def sendContact(self, chat_id, phone_number, first_name,
                    last_name=None,
                    disable_notification=None, reply_to_message_id=None, reply_markup=None):
        """ See: https://core.telegram.org/bots/api#sendcontact """
        p = _strip(locals())
        return self._api_request('sendContact', _rectify(p))

    def sendChatAction(self, chat_id, action):
        """ See: https://core.telegram.org/bots/api#sendchataction """
        p = _strip(locals())
        return self._api_request('sendChatAction', _rectify(p))

    def getUserProfilePhotos(self, user_id, offset=None, limit=None):
        """ See: https://core.telegram.org/bots/api#getuserprofilephotos """
        p = _strip(locals())
        return self._api_request('getUserProfilePhotos', _rectify(p))

    def getFile(self, file_id):
        """ See: https://core.telegram.org/bots/api#getfile """
        p = _strip(locals())
        return self._api_request('getFile', _rectify(p))

    def kickChatMember(self, chat_id, user_id):
        """ See: https://core.telegram.org/bots/api#kickchatmember """
        p = _strip(locals())
        return self._api_request('kickChatMember', _rectify(p))

    def leaveChat(self, chat_id):
        """ See: https://core.telegram.org/bots/api#leavechat """
        p = _strip(locals())
        return self._api_request('leaveChat', _rectify(p))

    def unbanChatMember(self, chat_id, user_id):
        """ See: https://core.telegram.org/bots/api#unbanchatmember """
        p = _strip(locals())
        return self._api_request('unbanChatMember', _rectify(p))

    def getChat(self, chat_id):
        """ See: https://core.telegram.org/bots/api#getchat """
        p = _strip(locals())
        return self._api_request('getChat', _rectify(p))

    def getChatAdministrators(self, chat_id):
        """ See: https://core.telegram.org/bots/api#getchatadministrators """
        p = _strip(locals())
        return self._api_request('getChatAdministrators', _rectify(p))

    def getChatMembersCount(self, chat_id):
        """ See: https://core.telegram.org/bots/api#getchatmemberscount """
        p = _strip(locals())
        return self._api_request('getChatMembersCount', _rectify(p))

    def getChatMember(self, chat_id, user_id):
        """ See: https://core.telegram.org/bots/api#getchatmember """
        p = _strip(locals())
        return self._api_request('getChatMember', _rectify(p))

    def answerCallbackQuery(self, callback_query_id, text=None, show_alert=None):
        """ See: https://core.telegram.org/bots/api#answercallbackquery """
        p = _strip(locals())
        return self._api_request('answerCallbackQuery', _rectify(p))

    def editMessageText(self, msg_identifier, text,
                        parse_mode=None, disable_web_page_preview=None, reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#editmessagetext

        :param msg_identifier: a 2-tuple (``chat_id``, ``message_id``),
                               a 1-tuple (``inline_message_id``),
                               or simply ``inline_message_id``.
                               You may extract this value easily with :meth:`telepot.message_identifier`
        """
        p = _strip(locals(), more=['msg_identifier'])
        p.update(_dismantle_message_identifier(msg_identifier))
        return self._api_request('editMessageText', _rectify(p))

    def editMessageCaption(self, msg_identifier, caption=None, reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#editmessagecaption

        :param msg_identifier: Same as ``msg_identifier`` in :meth:`telepot.Bot.editMessageText`
        """
        p = _strip(locals(), more=['msg_identifier'])
        p.update(_dismantle_message_identifier(msg_identifier))
        return self._api_request('editMessageCaption', _rectify(p))

    def editMessageReplyMarkup(self, msg_identifier, reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#editmessagereplymarkup

        :param msg_identifier: Same as ``msg_identifier`` in :meth:`telepot.Bot.editMessageText`
        """
        p = _strip(locals(), more=['msg_identifier'])
        p.update(_dismantle_message_identifier(msg_identifier))
        return self._api_request('editMessageReplyMarkup', _rectify(p))

    def answerInlineQuery(self, inline_query_id, results,
                          cache_time=None, is_personal=None, next_offset=None,
                          switch_pm_text=None, switch_pm_parameter=None):
        """ See: https://core.telegram.org/bots/api#answerinlinequery """
        p = _strip(locals())
        return self._api_request('answerInlineQuery', _rectify(p))

    def getUpdates(self, offset=None, limit=None, timeout=None):
        """ See: https://core.telegram.org/bots/api#getupdates """
        p = _strip(locals())
        return self._api_request('getUpdates', _rectify(p))

    def setWebhook(self, url=None, certificate=None):
        """ See: https://core.telegram.org/bots/api#setwebhook """
        p = _strip(locals(), more=['certificate'])

        if certificate:
            files = {'certificate': certificate}
            return self._api_request('setWebhook', _rectify(p), files)
        else:
            return self._api_request('setWebhook', _rectify(p))

    def download_file(self, file_id, dest):
        """
        Download a file to local disk.

        :param dest: a path or a ``file`` object
        """
        f = self.getFile(file_id)
        try:
            d = dest if _isfile(dest) else open(dest, 'wb')

            r = api.download((self._token, f['file_path']))

            # Ref:
            #   http://stackoverflow.com/questions/17285464/whats-the-best-way-to-download-file-using-urllib3
            while 1:
                data = r.read(self._file_chunk_size)
                if data is None:
                    break
                d.write(data)
        finally:
            if not _isfile(dest) and 'd' in locals():
                d.close()

            if 'r' in locals():
                r.release_conn()

    def message_loop(self, callback=None, relax=0.1, timeout=20, source=None, ordered=True, maxhold=3, run_forever=False):
        """
        Spawn a thread to constantly ``getUpdates`` or pull updates from a queue.
        Apply ``callback`` to every message received.

        :param callback: a function that takes one argument (the message), or a routing table.
                         If ``None``, the bot's ``handle`` method is used.

        A *routing table* is a dictionary of ``{flavor: function}``, mapping messages to appropriate
        handler functions according to their flavors. It allows you to define functions specifically
        to handle one flavor of messages. It usually looks like this: ``{'chat': fn1,
        'callback_query': fn2, 'inline_query': fn3, ...}``. Each handler function should take
        one argument (the message).

        :param source: Source of updates.
                       If ``None``, ``getUpdates`` is used to obtain new messages from Telegram servers.
                       If it is a synchronized queue (``Queue.Queue`` in Python 2.7 or
                       ``queue.Queue`` in Python 3), new messages are pulled from the queue.
                       A web application implementing a webhook can dump updates into the queue,
                       while the bot pulls from it. This is how telepot can be integrated with webhooks.

        Acceptable contents in queue:

        - ``str``, ``unicode`` (Python 2.7), or ``bytes`` (Python 3, decoded using UTF-8)
          representing a JSON-serialized `Update <https://core.telegram.org/bots/api#update>`_ object.
        - a ``dict`` representing an Update object.

        When ``source`` is ``None``, these parameters are meaningful:

        :param relax: seconds between each ``getUpdates``
        :type relax: float
        :param timeout: ``timeout`` parameter supplied to :meth:`telepot.Bot.getUpdates`,
                        controlling how long to poll.
        :type timeout: int

        When ``source`` is a queue, these parameters are meaningful:

        :param ordered: If ``True``, ensure in-order delivery of messages to ``callback``
                        (i.e. updates with a smaller ``update_id`` always come before those with
                        a larger ``update_id``).
                        If ``False``, no re-ordering is done. ``callback`` is applied to messages
                        as soon as they are pulled from queue.
        :type ordered: bool
        :param maxhold: Applied only when ``ordered`` is ``True``. The maximum number of seconds
                        an update is held waiting for a not-yet-arrived smaller ``update_id``.
                        When this number of seconds is up, the update is delivered to ``callback``
                        even if some smaller ``update_id``\s have not yet arrived. If those smaller
                        ``update_id``\s arrive at some later time, they are discarded.
        :type maxhold: float

        Finally, there is this parameter, meaningful always:

        :param run_forever: If ``True``, append an infinite loop at the end of this method,
                            so it never returns. Useful as the very last line in a program.
        :type run_forever: bool
        """
        if callback is None:
            callback = self.handle
        elif isinstance(callback, dict):
            callback = flavor_router(callback)

        def handle(update):
            try:
                key = _find_first_key(update, ['message',
                                               'edited_message',
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
        self._mic = helper.Microphone()

    @property
    def mic(self):
        return self._mic

    def create_listener(self):
        q = queue.Queue()
        self._mic.add(q)
        ln = helper.Listener(self._mic, q)
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
