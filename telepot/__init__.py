import sys
import io
import time
import json
import threading
import traceback
import collections
import bisect

try:
    import Queue as queue
except ImportError:
    import queue

# Patch urllib3 for sending unicode filename
from . import hack

from . import exception


__version_info__ = (12, 7)
__version__ = '.'.join(map(str, __version_info__))


def flavor(msg):
    """
    Return flavor of message or event.

    A message's flavor may be one of these:

    - ``chat``
    - ``callback_query``
    - ``inline_query``
    - ``chosen_inline_result``
    - ``shipping_query``
    - ``pre_checkout_query``

    An event's flavor is determined by the single top-level key.
    """
    if 'message_id' in msg:
        return 'chat'
    elif 'id' in msg and 'chat_instance' in msg:
        return 'callback_query'
    elif 'id' in msg and 'query' in msg:
        return 'inline_query'
    elif 'result_id' in msg:
        return 'chosen_inline_result'
    elif 'id' in msg and 'shipping_address' in msg:
        return 'shipping_query'
    elif 'id' in msg and 'total_amount' in msg:
        return 'pre_checkout_query'
    else:
        top_keys = list(msg.keys())
        if len(top_keys) == 1:
            return top_keys[0]

        raise exception.BadFlavor(msg)


chat_flavors = ['chat']
inline_flavors = ['inline_query', 'chosen_inline_result']


def _find_first_key(d, keys):
    for k in keys:
        if k in d:
            return k
    raise KeyError('No suggested keys %s in %s' % (str(keys), str(d)))


all_content_types = [
    'text', 'audio', 'document', 'game', 'photo', 'sticker', 'video', 'voice', 'video_note',
    'contact', 'location', 'venue', 'new_chat_member', 'left_chat_member', 'new_chat_title',
    'new_chat_photo',  'delete_chat_photo', 'group_chat_created', 'supergroup_chat_created',
    'channel_chat_created', 'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message',
    'new_chat_members', 'invoice', 'successful_payment'
]

def glance(msg, flavor='chat', long=False):
    """
    Extract "headline" info about a message.
    Use parameter ``long`` to control whether a short or long tuple is returned.

    When ``flavor`` is ``chat``
    (``msg`` being a `Message <https://core.telegram.org/bots/api#message>`_ object):

    - short: (content_type, ``msg['chat']['type']``, ``msg['chat']['id']``)
    - long: (content_type, ``msg['chat']['type']``, ``msg['chat']['id']``, ``msg['date']``, ``msg['message_id']``)

    *content_type* can be: ``text``, ``audio``, ``document``, ``game``, ``photo``, ``sticker``, ``video``, ``voice``,
    ``video_note``, ``contact``, ``location``, ``venue``, ``new_chat_member``, ``left_chat_member``, ``new_chat_title``,
    ``new_chat_photo``, ``delete_chat_photo``, ``group_chat_created``, ``supergroup_chat_created``,
    ``channel_chat_created``, ``migrate_to_chat_id``, ``migrate_from_chat_id``, ``pinned_message``,
    ``new_chat_members``, ``invoice``, ``successful_payment``.

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

    When ``flavor`` is ``shipping_query``
    (``msg`` being a `ShippingQuery <https://core.telegram.org/bots/api#shippingquery>`_ object):

    - regardless: (``msg['id']``, ``msg['from']['id']``, ``msg['invoice_payload']``)

    When ``flavor`` is ``pre_checkout_query``
    (``msg`` being a `PreCheckoutQuery <https://core.telegram.org/bots/api#precheckoutquery>`_ object):

    - short: (``msg['id']``, ``msg['from']['id']``, ``msg['invoice_payload']``)
    - long: (``msg['id']``, ``msg['from']['id']``, ``msg['invoice_payload']``, ``msg['currency']``, ``msg['total_amount']``)
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

    def gl_shipping_query():
        return msg['id'], msg['from']['id'], msg['invoice_payload']

    def gl_pre_checkout_query():
        if long:
            return msg['id'], msg['from']['id'], msg['invoice_payload'], msg['currency'], msg['total_amount']
        else:
            return msg['id'], msg['from']['id'], msg['invoice_payload']

    try:
        fn = {'chat': gl_chat,
              'callback_query': gl_callback_query,
              'inline_query': gl_inline_query,
              'chosen_inline_result': gl_chosen_inline_result,
              'shipping_query': gl_shipping_query,
              'pre_checkout_query': gl_pre_checkout_query}[flavor]
    except KeyError:
        raise exception.BadFlavor(flavor)

    return fn()


def flance(msg, long=False):
    """
    A combination of :meth:`telepot.flavor` and :meth:`telepot.glance`,
    return a 2-tuple (flavor, headline_info), where *headline_info* is whatever extracted by
    :meth:`telepot.glance` depending on the message flavor and the ``long`` parameter.
    """
    f = flavor(msg)
    g = glance(msg, flavor=f, long=long)
    return f,g


def peel(event):
    """
    Remove an event's top-level skin (where its flavor is determined), and return
    the core content.
    """
    return list(event.values())[0]


def fleece(event):
    """
    A combination of :meth:`telepot.flavor` and :meth:`telepot.peel`,
    return a 2-tuple (flavor, content) of an event.
    """
    return flavor(event), peel(event)


def is_event(msg):
    """
    Return whether the message looks like an event. That is, whether it has a flavor
    that starts with an underscore.
    """
    return flavor(msg).startswith('_')


def origin_identifier(msg):
    """
    Extract the message identifier of a callback query's origin. Returned value
    is guaranteed to be a tuple.

    ``msg`` is expected to be ``callback_query``.
    """
    if 'message' in msg:
        return msg['message']['chat']['id'], msg['message']['message_id']
    elif 'inline_message_id' in msg:
        return msg['inline_message_id'],
    else:
        raise ValueError()

def message_identifier(msg):
    """
    Extract an identifier for message editing. Useful with :meth:`telepot.Bot.editMessageText`
    and similar methods. Returned value is guaranteed to be a tuple.

    ``msg`` is expected to be ``chat`` or ``choson_inline_result``.
    """
    if 'chat' in msg and 'message_id' in msg:
        return msg['chat']['id'], msg['message_id']
    elif 'inline_message_id' in msg:
        return msg['inline_message_id'],
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

def _split_input_media_array(media_array):
    def ensure_dict(input_media):
        if isinstance(input_media, tuple) and hasattr(input_media, '_asdict'):
            return input_media._asdict()
        elif isinstance(input_media, dict):
            return input_media
        else:
            raise ValueError()

    def given_attach_name(input_media):
        if isinstance(input_media['media'], tuple):
            return input_media['media'][0]
        else:
            return None

    def attach_name_generator(used_names):
        x = 0
        while 1:
            x += 1
            name = 'media' + str(x)
            if name in used_names:
                continue;
            yield name

    def split_media(input_media, name_generator):
        file_spec = input_media['media']

        # file_id, URL
        if _isstring(file_spec):
            return (input_media, None)

        # file-object
        # (attach-name, file-object)
        # (attach-name, (filename, file-object))
        if isinstance(file_spec, tuple):
            name, f = file_spec
        else:
            name, f = next(name_generator), file_spec

        m = input_media.copy()
        m['media'] = 'attach://' + name

        return (m, (name, f))

    ms = [ensure_dict(m) for m in media_array]

    used_names = [given_attach_name(m) for m in ms if given_attach_name(m) is not None]
    name_generator = attach_name_generator(used_names)

    splitted = [split_media(m, name_generator) for m in ms]

    legal_media, attachments = map(list, zip(*splitted))
    files_to_attach = dict([a for a in attachments if a is not None])

    return (legal_media, files_to_attach)


PY_3 = sys.version_info.major >= 3
_string_type = str if PY_3 else basestring
_file_type = io.IOBase if PY_3 else file

def _isstring(s):
    return isinstance(s, _string_type)

def _isfile(f):
    return isinstance(f, _file_type)


from . import helper

def flavor_router(routing_table):
    router = helper.Router(flavor, routing_table)
    return router.route


class _BotBase(object):
    def __init__(self, token):
        self._token = token
        self._file_chunk_size = 65536


def _strip(params, more=[]):
    return {key: value for key,value in params.items() if key not in ['self']+more}

def _rectify(params):
    def make_jsonable(value):
        if isinstance(value, list):
            return [make_jsonable(v) for v in value]
        elif isinstance(value, dict):
            return {k:make_jsonable(v) for k,v in value.items() if v is not None}
        elif isinstance(value, tuple) and hasattr(value, '_asdict'):
            return {k:make_jsonable(v) for k,v in value._asdict().items() if v is not None}
        else:
            return value

    def flatten(value):
        v = make_jsonable(value)

        if isinstance(v, (dict, list)):
            return json.dumps(v, separators=(',',':'))
        else:
            return v

    # remove None, then json-serialize if needed
    return {k: flatten(v) for k,v in params.items() if v is not None}


from . import api

class Bot(_BotBase):
    class Scheduler(threading.Thread):
        # A class that is sorted by timestamp. Use `bisect` module to ensure order in event queue.
        Event = collections.namedtuple('Event', ['timestamp', 'data'])
        Event.__eq__ = lambda self, other: self.timestamp == other.timestamp
        Event.__ne__ = lambda self, other: self.timestamp != other.timestamp
        Event.__gt__ = lambda self, other: self.timestamp > other.timestamp
        Event.__ge__ = lambda self, other: self.timestamp >= other.timestamp
        Event.__lt__ = lambda self, other: self.timestamp < other.timestamp
        Event.__le__ = lambda self, other: self.timestamp <= other.timestamp

        def __init__(self):
            super(Bot.Scheduler, self).__init__()
            self._eventq = []
            self._lock = threading.RLock()  # reentrant lock to allow locked method calling locked method
            self._event_handler = None

        def _locked(fn):
            def k(self, *args, **kwargs):
                with self._lock:
                    return fn(self, *args, **kwargs)
            return k

        @_locked
        def _insert_event(self, data, when):
            ev = self.Event(when, data)
            bisect.insort(self._eventq, ev)
            return ev

        @_locked
        def _remove_event(self, event):
            # Find event according to its timestamp.
            # Index returned should be one behind.
            i = bisect.bisect(self._eventq, event)

            # Having two events with identical timestamp is unlikely but possible.
            # I am going to move forward and compare timestamp AND object address
            # to make sure the correct object is found.

            while i > 0:
                i -= 1
                e = self._eventq[i]

                if e.timestamp != event.timestamp:
                    raise exception.EventNotFound(event)
                elif id(e) == id(event):
                    self._eventq.pop(i)
                    return

            raise exception.EventNotFound(event)

        @_locked
        def _pop_expired_event(self):
            if not self._eventq:
                return None

            if self._eventq[0].timestamp <= time.time():
                return self._eventq.pop(0)
            else:
                return None

        def event_at(self, when, data):
            """
            Schedule some data to emit at an absolute timestamp.

            :type when: int or float
            :type data: dictionary
            :return: an internal Event object
            """
            return self._insert_event(data, when)

        def event_later(self, delay, data):
            """
            Schedule some data to emit after a number of seconds.

            :type delay: int or float
            :type data: dictionary
            :return: an internal Event object
            """
            return self._insert_event(data, time.time()+delay)

        def event_now(self, data):
            """
            Emit some data as soon as possible.

            :type data: dictionary
            :return: an internal Event object
            """
            return self._insert_event(data, time.time())

        def cancel(self, event):
            """
            Cancel an event.

            :type event: an internal Event object
            """
            self._remove_event(event)

        def run(self):
            while 1:
                e = self._pop_expired_event()
                while e:
                    if callable(e.data):
                        d = e.data()  # call the data-producing function
                        if d is not None:
                            self._event_handler(d)
                    else:
                        self._event_handler(e.data)

                    e = self._pop_expired_event()
                time.sleep(0.1)

        def run_as_thread(self):
            self.daemon = True
            self.start()

        def on_event(self, fn):
            self._event_handler = fn

    def __init__(self, token):
        super(Bot, self).__init__(token)

        self._scheduler = self.Scheduler()

        self._router = helper.Router(flavor, {'chat': lambda msg: self.on_chat_message(msg),
                                              'callback_query': lambda msg: self.on_callback_query(msg),
                                              'inline_query': lambda msg: self.on_inline_query(msg),
                                              'chosen_inline_result': lambda msg: self.on_chosen_inline_result(msg)})
                                              # use lambda to delay evaluation of self.on_ZZZ to runtime because
                                              # I don't want to require defining all methods right here.

    @property
    def scheduler(self):
        return self._scheduler

    @property
    def router(self):
        return self._router

    def handle(self, msg):
        self._router.route(msg)

    def _api_request(self, method, params=None, files=None, **kwargs):
        return api.request((self._token, method, params, files), **kwargs)

    def _api_request_with_file(self, method, params, file_key, file_value, **kwargs):
        if _isstring(file_value):
            params[file_key] = file_value
            return self._api_request(method, _rectify(params), **kwargs)
        else:
            files = {file_key: file_value}
            return self._api_request(method, _rectify(params), files, **kwargs)

    def getMe(self):
        """ See: https://core.telegram.org/bots/api#getme """
        return self._api_request('getMe')

    def sendMessage(self, chat_id, text,
                    parse_mode=None,
                    disable_web_page_preview=None,
                    disable_notification=None,
                    reply_to_message_id=None,
                    reply_markup=None):
        """ See: https://core.telegram.org/bots/api#sendmessage """
        p = _strip(locals())
        return self._api_request('sendMessage', _rectify(p))

    def forwardMessage(self, chat_id, from_chat_id, message_id,
                       disable_notification=None):
        """ See: https://core.telegram.org/bots/api#forwardmessage """
        p = _strip(locals())
        return self._api_request('forwardMessage', _rectify(p))

    def sendPhoto(self, chat_id, photo,
                  caption=None,
                  parse_mode=None,
                  disable_notification=None,
                  reply_to_message_id=None,
                  reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#sendphoto

        :param photo:
            - string: ``file_id`` for a photo existing on Telegram servers
            - string: HTTP URL of a photo from the Internet
            - file-like object: obtained by ``open(path, 'rb')``
            - tuple: (filename, file-like object). If the filename contains
              non-ASCII characters and you are using Python 2.7, make sure the
              filename is a unicode string.
        """
        p = _strip(locals(), more=['photo'])
        return self._api_request_with_file('sendPhoto', _rectify(p), 'photo', photo)

    def sendAudio(self, chat_id, audio,
                  caption=None,
                  parse_mode=None,
                  duration=None,
                  performer=None,
                  title=None,
                  disable_notification=None,
                  reply_to_message_id=None,
                  reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#sendaudio

        :param audio: Same as ``photo`` in :meth:`telepot.Bot.sendPhoto`
        """
        p = _strip(locals(), more=['audio'])
        return self._api_request_with_file('sendAudio', _rectify(p), 'audio', audio)

    def sendDocument(self, chat_id, document,
                     caption=None,
                     parse_mode=None,
                     disable_notification=None,
                     reply_to_message_id=None,
                     reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#senddocument

        :param document: Same as ``photo`` in :meth:`telepot.Bot.sendPhoto`
        """
        p = _strip(locals(), more=['document'])
        return self._api_request_with_file('sendDocument', _rectify(p), 'document', document)

    def sendVideo(self, chat_id, video,
                  duration=None,
                  width=None,
                  height=None,
                  caption=None,
                  parse_mode=None,
                  supports_streaming=None,
                  disable_notification=None,
                  reply_to_message_id=None,
                  reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#sendvideo

        :param video: Same as ``photo`` in :meth:`telepot.Bot.sendPhoto`
        """
        p = _strip(locals(), more=['video'])
        return self._api_request_with_file('sendVideo', _rectify(p), 'video', video)

    def sendVoice(self, chat_id, voice,
                  caption=None,
                  parse_mode=None,
                  duration=None,
                  disable_notification=None,
                  reply_to_message_id=None,
                  reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#sendvoice

        :param voice: Same as ``photo`` in :meth:`telepot.Bot.sendPhoto`
        """
        p = _strip(locals(), more=['voice'])
        return self._api_request_with_file('sendVoice', _rectify(p), 'voice', voice)

    def sendVideoNote(self, chat_id, video_note,
                      duration=None,
                      length=None,
                      disable_notification=None,
                      reply_to_message_id=None,
                      reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#sendvideonote

        :param video_note: Same as ``photo`` in :meth:`telepot.Bot.sendPhoto`

        :param length:
            Although marked as optional, this method does not seem to work without
            it being specified. Supply any integer you want. It seems to have no effect
            on the video note's display size.
        """
        p = _strip(locals(), more=['video_note'])
        return self._api_request_with_file('sendVideoNote', _rectify(p), 'video_note', video_note)

    def sendMediaGroup(self, chat_id, media,
                       disable_notification=None,
                       reply_to_message_id=None):
        """
        See: https://core.telegram.org/bots/api#sendmediagroup

        :type media: array of `InputMedia <https://core.telegram.org/bots/api#inputmedia>`_ objects
        :param media:
            To indicate media locations, each InputMedia object's ``media`` field
            should be one of these:

            - string: ``file_id`` for a file existing on Telegram servers
            - string: HTTP URL of a file from the Internet
            - file-like object: obtained by ``open(path, 'rb')``
            - tuple: (form-data name, file-like object)
            - tuple: (form-data name, (filename, file-like object))

            In case of uploading, you may supply customized multipart/form-data
            names for each uploaded file (as in last 2 options above). Otherwise,
            telepot assigns unique names to each uploaded file. Names assigned by
            telepot will not collide with user-supplied names, if any.
        """
        p = _strip(locals(), more=['media'])
        legal_media, files_to_attach = _split_input_media_array(media)

        p['media'] = legal_media
        return self._api_request('sendMediaGroup', _rectify(p), files_to_attach)

    def sendLocation(self, chat_id, latitude, longitude,
                     live_period=None,
                     disable_notification=None,
                     reply_to_message_id=None,
                     reply_markup=None):
        """ See: https://core.telegram.org/bots/api#sendlocation """
        p = _strip(locals())
        return self._api_request('sendLocation', _rectify(p))

    def editMessageLiveLocation(self, msg_identifier, latitude, longitude,
                                reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#editmessagelivelocation

        :param msg_identifier: Same as in :meth:`.Bot.editMessageText`
        """
        p = _strip(locals(), more=['msg_identifier'])
        p.update(_dismantle_message_identifier(msg_identifier))
        return self._api_request('editMessageLiveLocation', _rectify(p))

    def stopMessageLiveLocation(self, msg_identifier,
                                reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#stopmessagelivelocation

        :param msg_identifier: Same as in :meth:`.Bot.editMessageText`
        """
        p = _strip(locals(), more=['msg_identifier'])
        p.update(_dismantle_message_identifier(msg_identifier))
        return self._api_request('stopMessageLiveLocation', _rectify(p))

    def sendVenue(self, chat_id, latitude, longitude, title, address,
                  foursquare_id=None,
                  disable_notification=None,
                  reply_to_message_id=None,
                  reply_markup=None):
        """ See: https://core.telegram.org/bots/api#sendvenue """
        p = _strip(locals())
        return self._api_request('sendVenue', _rectify(p))

    def sendContact(self, chat_id, phone_number, first_name,
                    last_name=None,
                    disable_notification=None,
                    reply_to_message_id=None,
                    reply_markup=None):
        """ See: https://core.telegram.org/bots/api#sendcontact """
        p = _strip(locals())
        return self._api_request('sendContact', _rectify(p))

    def sendGame(self, chat_id, game_short_name,
                 disable_notification=None,
                 reply_to_message_id=None,
                 reply_markup=None):
        """ See: https://core.telegram.org/bots/api#sendgame """
        p = _strip(locals())
        return self._api_request('sendGame', _rectify(p))

    def sendInvoice(self, chat_id, title, description, payload,
                    provider_token, start_parameter, currency, prices,
                    provider_data=None,
                    photo_url=None,
                    photo_size=None,
                    photo_width=None,
                    photo_height=None,
                    need_name=None,
                    need_phone_number=None,
                    need_email=None,
                    need_shipping_address=None,
                    is_flexible=None,
                    disable_notification=None,
                    reply_to_message_id=None,
                    reply_markup=None):
        """ See: https://core.telegram.org/bots/api#sendinvoice """
        p = _strip(locals())
        return self._api_request('sendInvoice', _rectify(p))

    def sendChatAction(self, chat_id, action):
        """ See: https://core.telegram.org/bots/api#sendchataction """
        p = _strip(locals())
        return self._api_request('sendChatAction', _rectify(p))

    def getUserProfilePhotos(self, user_id,
                             offset=None,
                             limit=None):
        """ See: https://core.telegram.org/bots/api#getuserprofilephotos """
        p = _strip(locals())
        return self._api_request('getUserProfilePhotos', _rectify(p))

    def getFile(self, file_id):
        """ See: https://core.telegram.org/bots/api#getfile """
        p = _strip(locals())
        return self._api_request('getFile', _rectify(p))

    def kickChatMember(self, chat_id, user_id,
                       until_date=None):
        """ See: https://core.telegram.org/bots/api#kickchatmember """
        p = _strip(locals())
        return self._api_request('kickChatMember', _rectify(p))

    def unbanChatMember(self, chat_id, user_id):
        """ See: https://core.telegram.org/bots/api#unbanchatmember """
        p = _strip(locals())
        return self._api_request('unbanChatMember', _rectify(p))

    def restrictChatMember(self, chat_id, user_id,
                           until_date=None,
                           can_send_messages=None,
                           can_send_media_messages=None,
                           can_send_other_messages=None,
                           can_add_web_page_previews=None):
        """ See: https://core.telegram.org/bots/api#restrictchatmember """
        p = _strip(locals())
        return self._api_request('restrictChatMember', _rectify(p))

    def promoteChatMember(self, chat_id, user_id,
                          can_change_info=None,
                          can_post_messages=None,
                          can_edit_messages=None,
                          can_delete_messages=None,
                          can_invite_users=None,
                          can_restrict_members=None,
                          can_pin_messages=None,
                          can_promote_members=None):
        """ See: https://core.telegram.org/bots/api#promotechatmember """
        p = _strip(locals())
        return self._api_request('promoteChatMember', _rectify(p))

    def exportChatInviteLink(self, chat_id):
        """ See: https://core.telegram.org/bots/api#exportchatinvitelink """
        p = _strip(locals())
        return self._api_request('exportChatInviteLink', _rectify(p))

    def setChatPhoto(self, chat_id, photo):
        """ See: https://core.telegram.org/bots/api#setchatphoto """
        p = _strip(locals(), more=['photo'])
        return self._api_request_with_file('setChatPhoto', _rectify(p), 'photo', photo)

    def deleteChatPhoto(self, chat_id):
        """ See: https://core.telegram.org/bots/api#deletechatphoto """
        p = _strip(locals())
        return self._api_request('deleteChatPhoto', _rectify(p))

    def setChatTitle(self, chat_id, title):
        """ See: https://core.telegram.org/bots/api#setchattitle """
        p = _strip(locals())
        return self._api_request('setChatTitle', _rectify(p))

    def setChatDescription(self, chat_id,
                           description=None):
        """ See: https://core.telegram.org/bots/api#setchatdescription """
        p = _strip(locals())
        return self._api_request('setChatDescription', _rectify(p))

    def pinChatMessage(self, chat_id, message_id,
                       disable_notification=None):
        """ See: https://core.telegram.org/bots/api#pinchatmessage """
        p = _strip(locals())
        return self._api_request('pinChatMessage', _rectify(p))

    def unpinChatMessage(self, chat_id):
        """ See: https://core.telegram.org/bots/api#unpinchatmessage """
        p = _strip(locals())
        return self._api_request('unpinChatMessage', _rectify(p))

    def leaveChat(self, chat_id):
        """ See: https://core.telegram.org/bots/api#leavechat """
        p = _strip(locals())
        return self._api_request('leaveChat', _rectify(p))

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

    def setChatStickerSet(self, chat_id, sticker_set_name):
        """ See: https://core.telegram.org/bots/api#setchatstickerset """
        p = _strip(locals())
        return self._api_request('setChatStickerSet', _rectify(p))

    def deleteChatStickerSet(self, chat_id):
        """ See: https://core.telegram.org/bots/api#deletechatstickerset """
        p = _strip(locals())
        return self._api_request('deleteChatStickerSet', _rectify(p))

    def answerCallbackQuery(self, callback_query_id,
                            text=None,
                            show_alert=None,
                            url=None,
                            cache_time=None):
        """ See: https://core.telegram.org/bots/api#answercallbackquery """
        p = _strip(locals())
        return self._api_request('answerCallbackQuery', _rectify(p))

    def answerShippingQuery(self, shipping_query_id, ok,
                            shipping_options=None,
                            error_message=None):
        """ See: https://core.telegram.org/bots/api#answershippingquery """
        p = _strip(locals())
        return self._api_request('answerShippingQuery', _rectify(p))

    def answerPreCheckoutQuery(self, pre_checkout_query_id, ok,
                               error_message=None):
        """ See: https://core.telegram.org/bots/api#answerprecheckoutquery """
        p = _strip(locals())
        return self._api_request('answerPreCheckoutQuery', _rectify(p))

    def editMessageText(self, msg_identifier, text,
                        parse_mode=None,
                        disable_web_page_preview=None,
                        reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#editmessagetext

        :param msg_identifier:
            a 2-tuple (``chat_id``, ``message_id``),
            a 1-tuple (``inline_message_id``),
            or simply ``inline_message_id``.
            You may extract this value easily with :meth:`telepot.message_identifier`
        """
        p = _strip(locals(), more=['msg_identifier'])
        p.update(_dismantle_message_identifier(msg_identifier))
        return self._api_request('editMessageText', _rectify(p))

    def editMessageCaption(self, msg_identifier,
                           caption=None,
                           parse_mode=None,
                           reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#editmessagecaption

        :param msg_identifier: Same as ``msg_identifier`` in :meth:`telepot.Bot.editMessageText`
        """
        p = _strip(locals(), more=['msg_identifier'])
        p.update(_dismantle_message_identifier(msg_identifier))
        return self._api_request('editMessageCaption', _rectify(p))

    def editMessageReplyMarkup(self, msg_identifier,
                               reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#editmessagereplymarkup

        :param msg_identifier: Same as ``msg_identifier`` in :meth:`telepot.Bot.editMessageText`
        """
        p = _strip(locals(), more=['msg_identifier'])
        p.update(_dismantle_message_identifier(msg_identifier))
        return self._api_request('editMessageReplyMarkup', _rectify(p))

    def deleteMessage(self, msg_identifier):
        """
        See: https://core.telegram.org/bots/api#deletemessage

        :param msg_identifier:
            Same as ``msg_identifier`` in :meth:`telepot.Bot.editMessageText`,
            except this method does not work on inline messages.
        """
        p = _strip(locals(), more=['msg_identifier'])
        p.update(_dismantle_message_identifier(msg_identifier))
        return self._api_request('deleteMessage', _rectify(p))

    def sendSticker(self, chat_id, sticker,
                    disable_notification=None,
                    reply_to_message_id=None,
                    reply_markup=None):
        """
        See: https://core.telegram.org/bots/api#sendsticker

        :param sticker: Same as ``photo`` in :meth:`telepot.Bot.sendPhoto`
        """
        p = _strip(locals(), more=['sticker'])
        return self._api_request_with_file('sendSticker', _rectify(p), 'sticker', sticker)

    def getStickerSet(self, name):
        """
        See: https://core.telegram.org/bots/api#getstickerset
        """
        p = _strip(locals())
        return self._api_request('getStickerSet', _rectify(p))

    def uploadStickerFile(self, user_id, png_sticker):
        """
        See: https://core.telegram.org/bots/api#uploadstickerfile
        """
        p = _strip(locals(), more=['png_sticker'])
        return self._api_request_with_file('uploadStickerFile', _rectify(p), 'png_sticker', png_sticker)

    def createNewStickerSet(self, user_id, name, title, png_sticker, emojis,
                            contains_masks=None,
                            mask_position=None):
        """
        See: https://core.telegram.org/bots/api#createnewstickerset
        """
        p = _strip(locals(), more=['png_sticker'])
        return self._api_request_with_file('createNewStickerSet', _rectify(p), 'png_sticker', png_sticker)

    def addStickerToSet(self, user_id, name, png_sticker, emojis,
                        mask_position=None):
        """
        See: https://core.telegram.org/bots/api#addstickertoset
        """
        p = _strip(locals(), more=['png_sticker'])
        return self._api_request_with_file('addStickerToSet', _rectify(p), 'png_sticker', png_sticker)

    def setStickerPositionInSet(self, sticker, position):
        """
        See: https://core.telegram.org/bots/api#setstickerpositioninset
        """
        p = _strip(locals())
        return self._api_request('setStickerPositionInSet', _rectify(p))

    def deleteStickerFromSet(self, sticker):
        """
        See: https://core.telegram.org/bots/api#deletestickerfromset
        """
        p = _strip(locals())
        return self._api_request('deleteStickerFromSet', _rectify(p))

    def answerInlineQuery(self, inline_query_id, results,
                          cache_time=None,
                          is_personal=None,
                          next_offset=None,
                          switch_pm_text=None,
                          switch_pm_parameter=None):
        """ See: https://core.telegram.org/bots/api#answerinlinequery """
        p = _strip(locals())
        return self._api_request('answerInlineQuery', _rectify(p))

    def getUpdates(self,
                   offset=None,
                   limit=None,
                   timeout=None,
                   allowed_updates=None):
        """ See: https://core.telegram.org/bots/api#getupdates """
        p = _strip(locals())
        return self._api_request('getUpdates', _rectify(p))

    def setWebhook(self,
                   url=None,
                   certificate=None,
                   max_connections=None,
                   allowed_updates=None):
        """ See: https://core.telegram.org/bots/api#setwebhook """
        p = _strip(locals(), more=['certificate'])

        if certificate:
            files = {'certificate': certificate}
            return self._api_request('setWebhook', _rectify(p), files)
        else:
            return self._api_request('setWebhook', _rectify(p))

    def deleteWebhook(self):
        """ See: https://core.telegram.org/bots/api#deletewebhook """
        return self._api_request('deleteWebhook')

    def getWebhookInfo(self):
        """ See: https://core.telegram.org/bots/api#getwebhookinfo """
        return self._api_request('getWebhookInfo')

    def setGameScore(self, user_id, score, game_message_identifier,
                     force=None,
                     disable_edit_message=None):
        """
        See: https://core.telegram.org/bots/api#setgamescore

        :param game_message_identifier: Same as ``msg_identifier`` in :meth:`telepot.Bot.editMessageText`
        """
        p = _strip(locals(), more=['game_message_identifier'])
        p.update(_dismantle_message_identifier(game_message_identifier))
        return self._api_request('setGameScore', _rectify(p))

    def getGameHighScores(self, user_id, game_message_identifier):
        """
        See: https://core.telegram.org/bots/api#getgamehighscores

        :param game_message_identifier: Same as ``msg_identifier`` in :meth:`telepot.Bot.editMessageText`
        """
        p = _strip(locals(), more=['game_message_identifier'])
        p.update(_dismantle_message_identifier(game_message_identifier))
        return self._api_request('getGameHighScores', _rectify(p))

    def download_file(self, file_id, dest):
        """
        Download a file to local disk.

        :param dest: a path or a ``file`` object
        """
        f = self.getFile(file_id)
        try:
            d = dest if _isfile(dest) else open(dest, 'wb')

            r = api.download((self._token, f['file_path']), preload_content=False)

            while 1:
                data = r.read(self._file_chunk_size)
                if not data:
                    break
                d.write(data)
        finally:
            if not _isfile(dest) and 'd' in locals():
                d.close()

            if 'r' in locals():
                r.release_conn()

    def message_loop(self, callback=None, relax=0.1,
                     timeout=20, allowed_updates=None,
                     source=None, ordered=True, maxhold=3,
                     run_forever=False):
        """
        :deprecated: will be removed in future. Use :class:`.MessageLoop` instead.

        Spawn a thread to constantly ``getUpdates`` or pull updates from a queue.
        Apply ``callback`` to every message received. Also starts the scheduler thread
        for internal events.

        :param callback:
            a function that takes one argument (the message), or a routing table.
            If ``None``, the bot's ``handle`` method is used.

        A *routing table* is a dictionary of ``{flavor: function}``, mapping messages to appropriate
        handler functions according to their flavors. It allows you to define functions specifically
        to handle one flavor of messages. It usually looks like this: ``{'chat': fn1,
        'callback_query': fn2, 'inline_query': fn3, ...}``. Each handler function should take
        one argument (the message).

        :param source:
            Source of updates.
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

        :type relax: float
        :param relax: seconds between each ``getUpdates``

        :type timeout: int
        :param timeout:
            ``timeout`` parameter supplied to :meth:`telepot.Bot.getUpdates`,
            controlling how long to poll.

        :type allowed_updates: array of string
        :param allowed_updates:
            ``allowed_updates`` parameter supplied to :meth:`telepot.Bot.getUpdates`,
            controlling which types of updates to receive.

        When ``source`` is a queue, these parameters are meaningful:

        :type ordered: bool
        :param ordered:
            If ``True``, ensure in-order delivery of messages to ``callback``
            (i.e. updates with a smaller ``update_id`` always come before those with
            a larger ``update_id``).
            If ``False``, no re-ordering is done. ``callback`` is applied to messages
            as soon as they are pulled from queue.

        :type maxhold: float
        :param maxhold:
            Applied only when ``ordered`` is ``True``. The maximum number of seconds
            an update is held waiting for a not-yet-arrived smaller ``update_id``.
            When this number of seconds is up, the update is delivered to ``callback``
            even if some smaller ``update_id``\s have not yet arrived. If those smaller
            ``update_id``\s arrive at some later time, they are discarded.

        Finally, there is this parameter, meaningful always:

        :type run_forever: bool or str
        :param run_forever:
            If ``True`` or any non-empty string, append an infinite loop at the end of
            this method, so it never returns. Useful as the very last line in a program.
            A non-empty string will also be printed, useful as an indication that the
            program is listening.
        """
        if callback is None:
            callback = self.handle
        elif isinstance(callback, dict):
            callback = flavor_router(callback)

        collect_queue = queue.Queue()

        def collector():
            while 1:
                try:
                    item = collect_queue.get(block=True)
                    callback(item)
                except:
                    # Localize error so thread can keep going.
                    traceback.print_exc()

        def relay_to_collector(update):
            key = _find_first_key(update, ['message',
                                           'edited_message',
                                           'channel_post',
                                           'edited_channel_post',
                                           'callback_query',
                                           'inline_query',
                                           'chosen_inline_result',
                                           'shipping_query',
                                           'pre_checkout_query'])
            collect_queue.put(update[key])
            return update['update_id']

        def get_from_telegram_server():
            offset = None  # running offset
            allowed_upd = allowed_updates
            while 1:
                try:
                    result = self.getUpdates(offset=offset,
                                             timeout=timeout,
                                             allowed_updates=allowed_upd)

                    # Once passed, this parameter is no longer needed.
                    allowed_upd = None

                    if len(result) > 0:
                        # No sort. Trust server to give messages in correct order.
                        # Update offset to max(update_id) + 1
                        offset = max([relay_to_collector(update) for update in result]) + 1

                except exception.BadHTTPResponse as e:
                    traceback.print_exc()

                    # Servers probably down. Wait longer.
                    if e.status == 502:
                        time.sleep(30)
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
                    relay_to_collector(update)
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
                        max_id = relay_to_collector(update)

                    elif update['update_id'] == max_id + 1:
                        # No update_id skipped, handle naturally.
                        max_id = relay_to_collector(update)

                        # clear contagious updates in buffer
                        if len(buffer) > 0:
                            buffer.popleft()  # first element belongs to update just received, useless now.
                            while 1:
                                try:
                                    if type(buffer[0]) is dict:
                                        max_id = relay_to_collector(buffer.popleft())  # updates that arrived earlier, handle them.
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
                                max_id = relay_to_collector(buffer.popleft())
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

        collector_thread = threading.Thread(target=collector)
        collector_thread.daemon = True
        collector_thread.start()

        if source is None:
            message_thread = threading.Thread(target=get_from_telegram_server)
        elif isinstance(source, queue.Queue):
            if ordered:
                message_thread = threading.Thread(target=get_from_queue, args=(source,))
            else:
                message_thread = threading.Thread(target=get_from_queue_unordered, args=(source,))
        else:
            raise ValueError('Invalid source')

        message_thread.daemon = True  # need this for main thread to be killable by Ctrl-C
        message_thread.start()

        self._scheduler.on_event(collect_queue.put)
        self._scheduler.run_as_thread()

        if run_forever:
            if _isstring(run_forever):
                print(run_forever)
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
        """
        :param delegation_patterns: a list of (seeder, delegator) tuples.
        """
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
