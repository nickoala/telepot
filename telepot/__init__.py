import sys
import io
import time
import json
import requests
import threading
import traceback
import collections
import warnings

# Suppress InsecurePlatformWarning
requests.packages.urllib3.disable_warnings()


_classmap = {}

# Function to produce namedtuple classes.
def _create_class(typename, fields):    
    # extract field names
    field_names = [e[0] if type(e) is tuple else e for e in fields]

    # extract (non-simple) fields that need conversions
    conversions = list(filter(lambda e: type(e) is tuple, fields))

    # Some dictionary keys are Python keywords and cannot be used as field names, e.g. `from`.
    # Get around by appending a '_', e.g. dict['from'] => namedtuple.from_
    keymap = [(k.rstrip('_'), k) for k in filter(lambda e: e in ['from_'], field_names)]

    # Create the base tuple class, with defaults.
    base = collections.namedtuple(typename, field_names)
    base.__new__.__defaults__ = (None,) * len(field_names)

    class sub(base):
        def __new__(cls, **kwargs):
            # Map keys.
            for oldkey, newkey in keymap:
                kwargs[newkey] = kwargs[oldkey]
                del kwargs[oldkey]

            # Any unexpected arguments?
            unexpected = set(kwargs.keys()) - set(super(sub, cls)._fields)

            # Remove unexpected arguments and issue warning.
            if unexpected:
                for k in unexpected:
                    del kwargs[k]

                s = ('Unexpected fields: ' + ', '.join(unexpected) + ''
                     '\nBot API seems to have added new fields to the returned data.'
                     ' This version of namedtuple is not able to capture them.'
                     '\n\nPlease upgrade telepot by:'
                     '\n  sudo pip install telepot --upgrade'
                     '\n\nIf you still see this message after upgrade, that means I am still working to bring the code up-to-date.'
                     ' Please try upgrade again a few days later.'
                     ' In the meantime, you can access the new fields the old-fashioned way, through the raw dictionary.')

                warnings.warn(s, UserWarning)

            # Convert non-simple values to namedtuples.
            for key, func in conversions:
                if key in kwargs:
                    if type(kwargs[key]) is dict:
                        kwargs[key] = func(**kwargs[key])
                    elif type(kwargs[key]) is list:
                        kwargs[key] = func(kwargs[key])
                    else:
                        raise RuntimeError('Can only convert dict or list')

            return super(sub, cls).__new__(cls, **kwargs)

    sub.__name__ = typename
    _classmap[typename] = sub

    return sub


User = _create_class('User', ['id', 'first_name', 'last_name', 'username'])
GroupChat = _create_class('GroupChat', ['id', 'title'])
PhotoSize = _create_class('PhotoSize', ['file_id', 'width', 'height', 'file_size'])

Audio = _create_class('Audio', ['file_id', 'duration', 'performer', 'title', 'mime_type', 'file_size'])
Document = _create_class('Document', ['file_id', ('thumb', PhotoSize), 'file_name', 'mime_type', 'file_size'])
Sticker = _create_class('Sticker', ['file_id', 'width', 'height', ('thumb', PhotoSize), 'file_size'])
Video = _create_class('Video', ['file_id', 'width', 'height', 'duration', ('thumb', PhotoSize), 'mime_type', 'file_size'])
Voice = _create_class('Voice', ['file_id', 'duration', 'mime_type', 'file_size'])

Contact = _create_class('Contact', ['phone_number', 'first_name', 'last_name', 'user_id'])
Location = _create_class('Location', ['longitude', 'latitude'])
File = _create_class('File', ['file_id', 'file_size', 'file_path'])

def PhotoSizeArray(data):
    return [PhotoSize(**p) for p in data]

_classmap['PhotoSize[]'] = PhotoSizeArray

def PhotoSizeArrayArray(data):
    return [[PhotoSize(**p) for p in array] for array in data]

_classmap['PhotoSize[][]'] = PhotoSizeArrayArray

UserProfilePhotos = _create_class('UserProfilePhotos', ['total_count', ('photos', PhotoSizeArrayArray)])

def User_or_GroupChat(**kwargs):
    if kwargs['id'] < 0:
        return GroupChat(**kwargs)
    else:
        return User(**kwargs)

_classmap['User/GroupChat'] = User_or_GroupChat

Message = _create_class('Message', [
              'message_id',
              ('from_', User),
              'date',
              ('chat', User_or_GroupChat),
              ('forward_from', User),
              'forward_date',
              ('reply_to_message', lambda **kwargs: _classmap['Message'](**kwargs)),  # get around the fact that `Message` is not yet defined
              'text',
              ('audio', Audio),
              ('document', Document),
              ('photo', PhotoSizeArray),
              ('sticker', Sticker),
              ('video', Video),
              ('voice', Voice),
              'caption',
              ('contact', Contact),
              ('location', Location),
              ('new_chat_participant', User),
              ('left_chat_participant', User),
              'new_chat_title',
              ('new_chat_photo', PhotoSizeArray),
              'delete_chat_photo',
              'group_chat_created',
          ])

Update = _create_class('Update', ['update_id', ('message', Message)])

def UpdateArray(data):
    return [Update(**u) for u in data]

_classmap['Update[]'] = UpdateArray


"""
Convert a dictionary to a namedtuple, given the type of object.
You can see what `type` is valid by entering this in Python interpreter:
>>> import telepot
>>> print telepot._classmap
It includes all Bot API objects you may get back from the server, plus a few.
"""
def namedtuple(data, type):
    if type[-2:] == '[]':
        return _classmap[type](data)
    else:
        return _classmap[type](**data)


# Extract essential info of the Message.
def glance(msg, long=False):
    types = [
        'text', 'voice', 'sticker', 'photo', 'audio' ,'document', 'video', 'contact', 'location',
        'new_chat_participant', 'left_chat_participant',  'new_chat_title', 'new_chat_photo',  'delete_chat_photo', 'group_chat_created', 
    ]

    if isinstance(msg, Message):
        for msgtype in types:
            if getattr(msg, msgtype) is not None:
                break

        return (msgtype, msg.from_.id, msg.chat.id) if not long else (msgtype, msg.from_.id, msg.chat.id, msg.date, msg.message_id)
    else:
        for msgtype in types:
            if msgtype in msg:
                break

        return (msgtype, msg['from']['id'], msg['chat']['id']) if not long else (msgtype, msg['from']['id'], msg['chat']['id'], msg['date'], msg['message_id'])


class TelepotException(Exception):
    pass

class BadHTTPResponse(TelepotException):
    def __init__(self, status, text):
        super(BadHTTPResponse, self).__init__(status, text)

    @property
    def status(self):
        return self.args[0]

    @property
    def text(self):
        return self.args[1]

class TelegramError(TelepotException):
    def __init__(self, description, error_code):
        super(TelegramError, self).__init__(description, error_code)

    @property
    def description(self):
        return self.args[0]

    @property
    def error_code(self):
        return self.args[1]


# Ensure an exception is raised for requests that take too long
_http_timeout = 30

# For streaming file download
_file_chunk_size = 65536

class Bot(object):
    def __init__(self, token):
        self._token = token
        self._msg_thread = None

    def _fileurl(self, path):
        return 'https://api.telegram.org/file/bot%s/%s' % (self._token, path)

    def _methodurl(self, method):
        return 'https://api.telegram.org/bot%s/%s' % (self._token, method)

    def _parse(self, response):
        try:
            data = response.json()
        except ValueError:  # No JSON object could be decoded
            raise BadHTTPResponse(response.status_code, response.text)

        if data['ok']:
            return data['result']
        else:
            raise TelegramError(data['description'], data['error_code'])

    def _rectify(self, params):
        # remove None, then json-serialize if needed
        return {key: value if type(value) not in [dict, list] else json.dumps(value, separators=(',',':')) for key,value in params.items() if value is not None}

    def getMe(self):
        r = requests.post(self._methodurl('getMe'), timeout=_http_timeout)
        return self._parse(r)

    def sendMessage(self, chat_id, text, parse_mode=None, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None):
        p = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode, 'disable_web_page_preview': disable_web_page_preview, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}
        r = requests.post(self._methodurl('sendMessage'), params=self._rectify(p), timeout=_http_timeout)
        return self._parse(r)

    def forwardMessage(self, chat_id, from_chat_id, message_id):
        p = {'chat_id': chat_id, 'from_chat_id': from_chat_id, 'message_id': message_id}
        r = requests.post(self._methodurl('forwardMessage'), params=self._rectify(p), timeout=_http_timeout)
        return self._parse(r)

    def _isfile(self, f):
        if sys.version_info.major >= 3:
            return isinstance(f, io.IOBase)
        else:
            return type(f) is file

    def _sendFile(self, inputfile, filetype, params):
        method = {'photo':    'sendPhoto',
                  'audio':    'sendAudio',
                  'document': 'sendDocument',
                  'sticker':  'sendSticker',
                  'video':    'sendVideo',
                  'voice':    'sendVoice',}[filetype]

        if self._isfile(inputfile):
            files = {filetype: inputfile}
            r = requests.post(self._methodurl(method), params=self._rectify(params), files=files)

            # `_http_timeout` is not used here because, for some reason, the larger the file, 
            # the longer it takes for the server to respond (after upload is finished). It is hard to say
            # what value `_http_timeout` should be. In the future, maybe I should let user specify.
        else:
            params[filetype] = inputfile
            r = requests.post(self._methodurl(method), params=self._rectify(params), timeout=_http_timeout)

        return self._parse(r)

    def sendPhoto(self, chat_id, photo, caption=None, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(photo, 'photo', {'chat_id': chat_id, 'caption': caption, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendAudio(self, chat_id, audio, duration=None, performer=None, title=None, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(audio, 'audio', {'chat_id': chat_id, 'duration': duration, 'performer': performer, 'title': title, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendDocument(self, chat_id, document, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(document, 'document', {'chat_id': chat_id, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendSticker(self, chat_id, sticker, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(sticker, 'sticker', {'chat_id': chat_id, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendVideo(self, chat_id, video, duration=None, caption=None, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(video, 'video', {'chat_id': chat_id, 'duration': duration, 'caption': caption, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendVoice(self, chat_id, audio, duration=None, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(audio, 'voice', {'chat_id': chat_id, 'duration': duration, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendLocation(self, chat_id, latitude, longitude, reply_to_message_id=None, reply_markup=None):
        p = {'chat_id': chat_id, 'latitude': latitude, 'longitude': longitude, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}
        r = requests.post(self._methodurl('sendLocation'), params=self._rectify(p), timeout=_http_timeout)
        return self._parse(r)

    def sendChatAction(self, chat_id, action):
        p = {'chat_id': chat_id, 'action': action}
        r = requests.post(self._methodurl('sendChatAction'), params=self._rectify(p), timeout=_http_timeout)
        return self._parse(r)

    def getUserProfilePhotos(self, user_id, offset=None, limit=None):
        p = {'user_id': user_id, 'offset': offset, 'limit': limit}
        r = requests.post(self._methodurl('getUserProfilePhotos'), params=self._rectify(p), timeout=_http_timeout)
        return self._parse(r)

    def getFile(self, file_id):
        p = {'file_id': file_id}
        r = requests.post(self._methodurl('getFile'), params=self._rectify(p), timeout=_http_timeout)
        return self._parse(r)

    def getUpdates(self, offset=None, limit=None, timeout=None):
        p = {'offset': offset, 'limit': limit, 'timeout': timeout}
        r = requests.post(self._methodurl('getUpdates'), params=self._rectify(p), timeout=_http_timeout+(0 if timeout is None else timeout))
        return self._parse(r)

    def setWebhook(self, url=None, certificate=None):
        p = {'url': url}

        if certificate:
            files = {'certificate': certificate}
            r = requests.post(self._methodurl('setWebhook'), params=self._rectify(p), files=files, timeout=_http_timeout)
        else:
            r = requests.post(self._methodurl('setWebhook'), params=self._rectify(p), timeout=_http_timeout)

        return self._parse(r)

    def downloadFile(self, file_id, dest):
        f = self.getFile(file_id)

        # `file_path` is optional in File object
        if 'file_path' not in f:
            raise TelegramError('No file_path returned', None)

        try:
            r = requests.get(self._fileurl(f['file_path']), stream=True, timeout=_http_timeout)

            d = dest if self._isfile(dest) else open(dest, 'wb')

            for chunk in r.iter_content(chunk_size=_file_chunk_size):
                if chunk:
                    d.write(chunk)
                    d.flush()
        finally:
            if not self._isfile(dest) and 'd' in locals():
                d.close()

            if 'r' in locals():
                r.close()

    def notifyOnMessage(self, callback, relax=0.1, timeout=20):
        # For MessageThread to call outer class getUpdates()
        def get_updates(offset, timeout):
            return self.getUpdates(offset=offset, timeout=timeout)

        # This is the thread that constantly calls getUpdates() and applies callback function
        # to messages. The main thread sets the params (callback, relax, timeout), and this
        # thread just applies those params.
        #
        # A Bot has at most one MessageThread. If `callback` is set to None (cancelled), 
        # the MessageThread will die. If `callback` is then set to non-None, a new MessageThread 
        # will be spawned. Main thread may modify MessageThread's params (callback, relax, timeout)
        # at any time.
        #
        # The two threads use a `lock` to coordinate their actions.
        # Scroll down to see their designed interactions.

        class MessageThread(threading.Thread):
            def __init__(self, callback, relax, timeout):
                super(MessageThread, self).__init__()
                self.set(callback, relax, timeout)
                self.lock = threading.Lock()
                self.dying = False

            def set(self, callback, relax, timeout):
                self.callback, self.relax, self.timeout = callback, relax, timeout

            def handle(self, update):
                try:
                    self.callback(update['message'])
                except:
                    # Localize the error so message thread can keep going.
                    traceback.print_exc()
                finally:
                    return update['update_id']

            def run(self):
                offset = None  # running offset
                while 1:
                    try:
                        with self.lock:
                            if not self.callback:
                                self.dying = True
                                return

                                # Ideally, I should call getUpdates() once more with the latest `offset`
                                # to acknowledge receiving those messages. But, because main thread may
                                # spawn a new MessageThread after seeing this one is `dying`, two
                                # getUpdates() will collide. Solution is, either to put getUpdates()
                                # within the lock (which causes main thread to block a little bit),
                                # or make the old and new MessageThread coordinate in some ways.
                                #
                                # As of now, some messages may be received twice (if callback is set,
                                # unset, then set again). Since this usage is not frequent and the problem
                                # is minor, I decide to leave it for now.

                        result = get_updates(offset=offset, timeout=self.timeout)

                        with self.lock:
                            if not self.callback:
                                self.dying = True
                                return

                            if len(result) > 0:
                                # No sort. Trust server to give messages in correct order.
                                # Update offset to max(update_id) + 1
                                offset = max([self.handle(update) for update in result]) + 1
                    except:
                        traceback.print_exc()
                    finally:
                        if not self.dying:
                            time.sleep(self.relax)

        # Interaction between main thread and message thread
        # - Message thread: check `callback` to determine `dying` (No callback leads to death)
        # - Main thread: check `dying` to determine whether to spawn a new thread or modify existing thread's `callback`
        #
        # MessageThread's `lock` is used to ensure checking/modifying `callback` and `dying` is done atomically.

        if self._msg_thread:
            with self._msg_thread.lock:
                if callback and self._msg_thread.dying:
                    # Spawn new message thread
                    self._msg_thread = MessageThread(callback, relax, timeout)
                    self._msg_thread.daemon = True
                    self._msg_thread.start()
                else:
                    # Modify existing message thread's params
                    self._msg_thread.set(callback, relax, timeout)
        elif callback:
            # Spawn new message thread
            self._msg_thread = MessageThread(callback, relax, timeout)
            self._msg_thread.daemon = True
            self._msg_thread.start()
