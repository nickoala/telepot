import requests, json, time, threading, traceback

# Suppress InsecurePlatformWarning
requests.packages.urllib3.disable_warnings()


class TelegramError(Exception):
    def __init__(self, description, error_code):
        super(TelegramError, self).__init__(description, error_code)
        self.description = description
        self.error_code = error_code


class Bot(object):
    def __init__(self, token):
        self._token = token

    def _url(self, method):
        return 'https://api.telegram.org/bot%s/%s' % (self._token, method)

    def _result(self, json_response):
        if json_response['ok']:
            return json_response['result']
        else:
            raise TelegramError(json_response['description'], json_response['error_code'])

    def _rectify(self, params):
        # remove None, then json-serialize if needed
        return {key: value if type(value) in [int, long, float, str] else json.dumps(value, separators=(',',':')) for key,value in params.items() if value is not None}

    def getMe(self):
        r = requests.post(self._url('getMe'))
        return self._result(r.json())

    def sendMessage(self, chat_id, text, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None):
        p = {'chat_id': chat_id, 'text': text, 'disable_web_page_preview': disable_web_page_preview, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}
        r = requests.post(self._url('sendMessage'), params=self._rectify(p))
        return self._result(r.json())

    def forwardMessage(self, chat_id, from_chat_id, message_id):
        p = {'chat_id': chat_id, 'from_chat_id': from_chat_id, 'message_id': message_id}
        r = requests.post(self._url('forwardMessage'), params=self._rectify(p))
        return self._result(r.json())

    def _sendFile(self, inputfile, filetype, params):
        method = {'photo':    'sendPhoto',
                  'audio':    'sendAudio',
                  'document': 'sendDocument',
                  'sticker':  'sendSticker',
                  'video':    'sendVideo',}[filetype]

        if type(inputfile) is file:
            files = {filetype: inputfile}
            r = requests.post(self._url(method), params=self._rectify(params), files=files)
        else:
            params[filetype] = inputfile
            r = requests.post(self._url(method), params=self._rectify(params))

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
        r = requests.post(self._url('sendLocation'), params=self._rectify(p))
        return self._result(r.json())

    def sendChatAction(self, chat_id, action):
        p = {'chat_id': chat_id, 'action': action}
        r = requests.post(self._url('sendChatAction'), params=self._rectify(p))
        return self._result(r.json())

    def getUserProfilePhotos(self, user_id, offset=None, limit=None):
        p = {'user_id': user_id, 'offset': offset, 'limit': limit}
        r = requests.post(self._url('getUserProfilePhotos'), params=self._rectify(p))
        return self._result(r.json())

    def getUpdates(self, offset=None, limit=None, timeout=None):
        p = {'offset': offset, 'limit': limit, 'timeout': timeout}
        r = requests.post(self._url('getUpdates'), params=self._rectify(p))
        return self._result(r.json())

    def setWebhook(self, url=None):
        p = {'url': url}
        r = requests.post(self._url('setWebhook'), params=self._rectify(p))
        return self._result(r.json())

    def notifyOnMessage(self, callback, accept=None, relax=1, offset=None, timeout=20):
        def handle(update):
            try:
                if accept is None or accept(update['message']):
                    callback(update['message'])
            except:
                # Localize the error raised by accept() or callback(),
                # so monitor thread can keep going.
                traceback.print_exc()
            finally:
                return update['update_id']

        def monitor():
            f = offset  # running offset
            while 1:
                result = self.getUpdates(offset=f, timeout=timeout)

                if len(result) > 0:
                    # No sort. Trust server to give messages in correct order.
                    # Update offset to max(update_id) + 1
                    f = max([handle(update) for update in result]) + 1

                time.sleep(relax)

        t = threading.Thread(target=monitor)
        t.daemon = True  # need this for main thread to be killable by Ctrl-C
        t.start()
