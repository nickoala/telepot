import requests, json, time, threading, traceback, sys

# Suppress InsecurePlatformWarning
requests.packages.urllib3.disable_warnings()

# Ensure an exception is raised for requests that take too long
http_timeout = 10


class TelegramError(Exception):
    def __init__(self, description, error_code):
        super(TelegramError, self).__init__(description, error_code)
        self.description = description
        self.error_code = error_code


class Bot(object):
    def __init__(self, token):
        self._token = token
        self._msg_thread = None

    def _url(self, method):
        return 'https://api.telegram.org/bot%s/%s' % (self._token, method)

    def _result(self, json_response):
        if json_response['ok']:
            return json_response['result']
        else:
            raise TelegramError(json_response['description'], json_response['error_code'])

    def _rectify(self, params):
        # remove None, then json-serialize if needed
        return {key: value if type(value) not in [dict, list] else json.dumps(value, separators=(',',':')) for key,value in params.items() if value is not None}

    def getMe(self):
        r = requests.post(self._url('getMe'), timeout=http_timeout)
        return self._result(r.json())

    def sendMessage(self, chat_id, text, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None):
        p = {'chat_id': chat_id, 'text': text, 'disable_web_page_preview': disable_web_page_preview, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}
        r = requests.post(self._url('sendMessage'), params=self._rectify(p), timeout=http_timeout)
        return self._result(r.json())

    def forwardMessage(self, chat_id, from_chat_id, message_id):
        p = {'chat_id': chat_id, 'from_chat_id': from_chat_id, 'message_id': message_id}
        r = requests.post(self._url('forwardMessage'), params=self._rectify(p), timeout=http_timeout)
        return self._result(r.json())

    def _isfile(self, f):
        if sys.version_info.major == 3:
            import io
            return isinstance(f, io.IOBase)
        else:
            return type(f) is file

    def _sendFile(self, inputfile, filetype, params):
        method = {'photo':    'sendPhoto',
                  'audio':    'sendAudio',
                  'document': 'sendDocument',
                  'sticker':  'sendSticker',
                  'video':    'sendVideo',}[filetype]

        if self._isfile(inputfile):
            files = {filetype: inputfile}
            r = requests.post(self._url(method), params=self._rectify(params), files=files, timeout=http_timeout)
        else:
            params[filetype] = inputfile
            r = requests.post(self._url(method), params=self._rectify(params), timeout=http_timeout)

        return self._result(r.json())

    def sendPhoto(self, chat_id, photo, caption=None, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(photo, 'photo', {'chat_id': chat_id, 'caption': caption, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendAudio(self, chat_id, audio, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(audio, 'audio', {'chat_id': chat_id, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendDocument(self, chat_id, document, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(document, 'document', {'chat_id': chat_id, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendSticker(self, chat_id, sticker, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(sticker, 'sticker', {'chat_id': chat_id, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendVideo(self, chat_id, video, reply_to_message_id=None, reply_markup=None):
        return self._sendFile(video, 'video', {'chat_id': chat_id, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendLocation(self, chat_id, latitude, longitude, reply_to_message_id=None, reply_markup=None):
        p = {'chat_id': chat_id, 'latitude': latitude, 'longitude': longitude, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}
        r = requests.post(self._url('sendLocation'), params=self._rectify(p), timeout=http_timeout)
        return self._result(r.json())

    def sendChatAction(self, chat_id, action):
        p = {'chat_id': chat_id, 'action': action}
        r = requests.post(self._url('sendChatAction'), params=self._rectify(p), timeout=http_timeout)
        return self._result(r.json())

    def getUserProfilePhotos(self, user_id, offset=None, limit=None):
        p = {'user_id': user_id, 'offset': offset, 'limit': limit}
        r = requests.post(self._url('getUserProfilePhotos'), params=self._rectify(p), timeout=http_timeout)
        return self._result(r.json())

    def getUpdates(self, offset=None, limit=None, timeout=None):
        p = {'offset': offset, 'limit': limit, 'timeout': timeout}
        r = requests.post(self._url('getUpdates'), params=self._rectify(p), timeout=http_timeout+(0 if timeout is None else timeout))
        return self._result(r.json())

    def setWebhook(self, url=None):
        p = {'url': url}
        r = requests.post(self._url('setWebhook'), params=self._rectify(p), timeout=http_timeout)
        return self._result(r.json())

    def notifyOnMessage(self, callback, relax=1, timeout=20):
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
