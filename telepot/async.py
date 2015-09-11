import asyncio, aiohttp, json, traceback, io
from concurrent.futures._base import CancelledError
import telepot


class Bot(object):
    def __init__(self, token, loop=None):
        self._token = token
        self._loop = loop if loop is not None else asyncio.get_event_loop()

    def _url(self, method):
        return 'https://api.telegram.org/bot%s/%s' % (self._token, method)

    def _rectify(self, params):
        # remove None, then json-serialize if needed
        return {key: value if type(value) not in [dict, list] else json.dumps(value, separators=(',',':')) for key,value in params.items() if value is not None}

    @asyncio.coroutine
    def _parse(self, response):
        try:
            data = yield from response.json()
        except ValueError:
            text = yield from response.text()
            raise telepot.BadHTTPResponse(response.status, text)

        if data['ok']:
            return data['result']
        else:
            raise telepot.TelegramError(data['description'], data['error_code'])

    @asyncio.coroutine
    def getMe(self):
        r = yield from asyncio.wait_for(aiohttp.post(self._url('getMe')), telepot._http_timeout)
        return (yield from self._parse(r))

    @asyncio.coroutine
    def sendMessage(self, chat_id, text, parse_mode=None, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None):
        p = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode, 'disable_web_page_preview': disable_web_page_preview, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}
        r = yield from asyncio.wait_for(aiohttp.post(self._url('sendMessage'), params=self._rectify(p)), telepot._http_timeout)
        return (yield from self._parse(r))

    @asyncio.coroutine
    def forwardMessage(self, chat_id, from_chat_id, message_id):
        p = {'chat_id': chat_id, 'from_chat_id': from_chat_id, 'message_id': message_id}
        r = yield from asyncio.wait_for(aiohttp.post(self._url('forwardMessage'), params=self._rectify(p)), telepot._http_timeout)
        return (yield from self._parse(r))

    @asyncio.coroutine
    def _sendFile(self, inputfile, filetype, params):
        method = {'photo':    'sendPhoto',
                  'audio':    'sendAudio',
                  'document': 'sendDocument',
                  'sticker':  'sendSticker',
                  'video':    'sendVideo',
                  'voice':    'sendVoice',}[filetype]

        if isinstance(inputfile, io.IOBase):
            files = {filetype: inputfile}
            r = yield from aiohttp.post(self._url(method), params=self._rectify(params), data=files)

            # `_http_timeout` is not used here because, for some reason, the larger the file, 
            # the longer it takes for the server to respond (after upload is finished). It is hard to say
            # what value `_http_timeout` should be. In the future, maybe I should let user specify.
        else:
            params[filetype] = inputfile
            r = yield from asyncio.wait_for(aiohttp.post(self._url(method), params=self._rectify(params)), telepot._http_timeout)

        return (yield from self._parse(r))

    @asyncio.coroutine
    def sendPhoto(self, chat_id, photo, caption=None, reply_to_message_id=None, reply_markup=None):
        return (yield from self._sendFile(photo, 'photo', {'chat_id': chat_id, 'caption': caption, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}))

    @asyncio.coroutine
    def sendAudio(self, chat_id, audio, duration=None, performer=None, title=None, reply_to_message_id=None, reply_markup=None):
        return (yield from self._sendFile(audio, 'audio', {'chat_id': chat_id, 'duration': duration, 'performer': performer, 'title': title, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}))

    @asyncio.coroutine
    def sendDocument(self, chat_id, document, reply_to_message_id=None, reply_markup=None):
        return (yield from self._sendFile(document, 'document', {'chat_id': chat_id, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}))

    @asyncio.coroutine
    def sendSticker(self, chat_id, sticker, reply_to_message_id=None, reply_markup=None):
        return (yield from self._sendFile(sticker, 'sticker', {'chat_id': chat_id, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}))

    @asyncio.coroutine
    def sendVideo(self, chat_id, video, duration=None, caption=None, reply_to_message_id=None, reply_markup=None):
        return (yield from self._sendFile(video, 'video', {'chat_id': chat_id, 'duration': duration, 'caption': caption, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}))

    @asyncio.coroutine
    def sendVoice(self, chat_id, audio, duration=None, reply_to_message_id=None, reply_markup=None):
        return (yield from self._sendFile(audio, 'voice', {'chat_id': chat_id, 'duration': duration, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}))

    @asyncio.coroutine
    def sendLocation(self, chat_id, latitude, longitude, reply_to_message_id=None, reply_markup=None):
        p = {'chat_id': chat_id, 'latitude': latitude, 'longitude': longitude, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}
        r = yield from asyncio.wait_for(aiohttp.post(self._url('sendLocation'), params=self._rectify(p)), telepot._http_timeout)
        return (yield from self._parse(r))

    @asyncio.coroutine
    def sendChatAction(self, chat_id, action):
        p = {'chat_id': chat_id, 'action': action}
        r = yield from asyncio.wait_for(aiohttp.post(self._url('sendChatAction'), params=self._rectify(p)), telepot._http_timeout)
        return (yield from self._parse(r))

    @asyncio.coroutine
    def getUserProfilePhotos(self, user_id, offset=None, limit=None):
        p = {'user_id': user_id, 'offset': offset, 'limit': limit}
        r = yield from asyncio.wait_for(aiohttp.post(self._url('getUserProfilePhotos'), params=self._rectify(p)), telepot._http_timeout)
        return (yield from self._parse(r))

    @asyncio.coroutine
    def getUpdates(self, offset=None, limit=None, timeout=None):
        p = {'offset': offset, 'limit': limit, 'timeout': timeout}
        r = yield from asyncio.wait_for(aiohttp.post(self._url('getUpdates'), params=self._rectify(p)), telepot._http_timeout+(0 if timeout is None else timeout))
        return (yield from self._parse(r))

    @asyncio.coroutine
    def setWebhook(self, url=None, certificate=None):
        p = {'url': url}

        if certificate:
            files = {'certificate': certificate}
            r = yield from asyncio.wait_for(aiohttp.post(self._url('setWebhook'), params=self._rectify(p), files=files), telepot._http_timeout)
        else:
            r = yield from asyncio.wait_for(aiohttp.post(self._url('setWebhook'), params=self._rectify(p)), telepot._http_timeout)

        return (yield from self._parse(r))

    @asyncio.coroutine
    def messageLoop(self, handler):
        # Wrap it in a coroutine if it is not.
        if not asyncio.iscoroutinefunction(handler):
            handler = asyncio.coroutine(handler)

        offset = None  # running offset
        while 1:
            try:
                updates = yield from self.getUpdates(offset=offset, timeout=20)

                if len(updates) > 0:
                    # Update offset to max(update_id) + 1
                    offset = max([u['update_id'] for u in updates]) + 1

                    for u in updates:
                        self._loop.create_task(handler(u['message']))

            except CancelledError:
                raise  # Stop if cancelled
            except:
                traceback.print_exc()  # Keep running on other errors
                yield from asyncio.sleep(1)
            else:
                yield from asyncio.sleep(1)
