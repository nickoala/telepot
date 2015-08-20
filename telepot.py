import requests, json, time, threading, traceback, sys

# Suppress InsecurePlatformWarning
requests.packages.urllib3.disable_warnings()

# Ensure an exception is raised for requests that take too long
http_timeout = 30


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
        """
        Test your bot's auth token. Returns basic information about the bot in form of 
        a `User <https://core.telegram.org/bots/api#user>`_ object.

        **Bot API method:** `getMe <https://core.telegram.org/bots/api#getme>`_
        """
        r = requests.post(self._url('getMe'), timeout=http_timeout)
        return self._result(r.json())

    def sendMessage(self, chat_id, text, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None):
        """
        Send text messages.

        **Bot API method:** `sendMessage <https://core.telegram.org/bots/api#sendmessage>`_

        :type chat_id: integer        
        :param chat_id: Unique identifier for the message recipient - \
        `User <https://core.telegram.org/bots/api#user>`_ or `GroupChat <https://core.telegram.org/bots/api#groupchat>`_ id

        :type text: string
        :param text: Text of the message to be sent
        
        :type disable_web_page_preview: boolean
        :param disable_web_page_preview: Disables link previews for links in this message

        :type reply_to_message_id: integer
        :param reply_to_message_id: If the message is a reply, ID of the original message.
        
        :type reply_markup: dict
        :param reply_markup: Additional interface options: \
        `ReplyKeyboardMarkup <https://core.telegram.org/bots/api#replykeyboardmarkup>`_ for a `custom reply keyboard <https://core.telegram.org/bots#keyboards>`_, \
        `ReplyKeyboardHide <https://core.telegram.org/bots/api#replykeyboardhide>`_ to hide a custom keyboard, \
        or `ForceReply <https://core.telegram.org/bots/api#forcereply>`_ to force a reply from the user.
        
        :return: the sent `Message <https://core.telegram.org/bots/api#message>`_ object
        """
        p = {'chat_id': chat_id, 'text': text, 'disable_web_page_preview': disable_web_page_preview, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}
        r = requests.post(self._url('sendMessage'), params=self._rectify(p), timeout=http_timeout)
        return self._result(r.json())

    def forwardMessage(self, chat_id, from_chat_id, message_id):
        """
        Forward messages of any kind.

        **Bot API method:** `forwardMessage <https://core.telegram.org/bots/api#forwardmessage>`_

        :type chat_id: integer
        :param chat_id: Unique identifier for the message recipient - \
        `User <https://core.telegram.org/bots/api#user>`_ or `GroupChat <https://core.telegram.org/bots/api#groupchat>`_ id

        :type from_chat_id: integer
        :param from_chat_id: Unique identifier for the chat where the original message was sent - \
        `User <https://core.telegram.org/bots/api#user>`_ or `GroupChat <https://core.telegram.org/bots/api#groupchat>`_ id

        :type message_id: integer
        :param message_id: Unique message identifier

        :return: the sent `Message <https://core.telegram.org/bots/api#message>`_ object
        """
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
                  'video':    'sendVideo',
                  'voice':    'sendVoice',}[filetype]

        if self._isfile(inputfile):
            files = {filetype: inputfile}
            r = requests.post(self._url(method), params=self._rectify(params), files=files)

            # `http_timeout` is not used here because, for some reason, the larger the file, 
            # the longer it takes for the server to respond (after upload is finished). It is hard to say
            # what value `http_timeout` should be. In the future, maybe I should let user specify.
        else:
            params[filetype] = inputfile
            r = requests.post(self._url(method), params=self._rectify(params), timeout=http_timeout)

        return self._result(r.json())

    def sendPhoto(self, chat_id, photo, caption=None, reply_to_message_id=None, reply_markup=None):
        """
        Send photos.

        **Bot API method:** `sendPhoto <https://core.telegram.org/bots/api#sendphoto>`_

        :type chat_id: integer
        :param chat_id: Unique identifier for the message recipient - \
        `User <https://core.telegram.org/bots/api#user>`_ or `GroupChat <https://core.telegram.org/bots/api#groupchat>`_ id

        :type photo: file or string
        :param photo: Photo to send. You can either pass a ``file_id`` as string to resend a photo that is already on \
        Telegram servers, or upload a new photo that is stored locally.

        :type caption: string
        :param caption: Photo caption

        :type reply_to_message_id: integer
        :param reply_to_message_id: If the message is a reply, ID of the original message.

        :type reply_markup: dict
        :param reply_markup: Additional interface options: \
        `ReplyKeyboardMarkup <https://core.telegram.org/bots/api#replykeyboardmarkup>`_ for a `custom reply keyboard <https://core.telegram.org/bots#keyboards>`_, \
        `ReplyKeyboardHide <https://core.telegram.org/bots/api#replykeyboardhide>`_ to hide a custom keyboard, \
        or `ForceReply <https://core.telegram.org/bots/api#forcereply>`_ to force a reply from the user.

        :return: the sent `Message <https://core.telegram.org/bots/api#message>`_ object
        """
        return self._sendFile(photo, 'photo', {'chat_id': chat_id, 'caption': caption, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendAudio(self, chat_id, audio, duration=None, performer=None, title=None, reply_to_message_id=None, reply_markup=None):
        """
        Send audio files, if you want Telegram clients to display them in the music player. 
        Your audio must be in the .mp3 format. For sending voice messages, use ``sendVoice()`` instead. 
        Bots can currently send audio files of up to 50 MB in size, this limit may be changed in the future.
        
        **Bot API method:** `sendAudio <https://core.telegram.org/bots/api#sendaudio>`_

        :type chat_id: integer
        :param chat_id: Unique identifier for the message recipient - \
        `User <https://core.telegram.org/bots/api#user>`_ or `GroupChat <https://core.telegram.org/bots/api#groupchat>`_ id

        :type audio: file or string
        :param audio: Audio file to send. You can either pass a ``file_id`` as string to resend an audio that is already on \
        Telegram servers, or upload a new audio file that is stored locally.

        :type duration: integer
        :param duration: Duration of the audio in seconds
        
        :type performer: string
        :param performer: Performer
        
        :type title: string
        :param title: Track name

        :type reply_to_message_id: integer
        :param reply_to_message_id: If the message is a reply, ID of the original message.

        :type reply_markup: dict
        :param reply_markup: Additional interface options: \
        `ReplyKeyboardMarkup <https://core.telegram.org/bots/api#replykeyboardmarkup>`_ for a `custom reply keyboard <https://core.telegram.org/bots#keyboards>`_, \
        `ReplyKeyboardHide <https://core.telegram.org/bots/api#replykeyboardhide>`_ to hide a custom keyboard, \
        or `ForceReply <https://core.telegram.org/bots/api#forcereply>`_ to force a reply from the user.

        :return: the sent `Message <https://core.telegram.org/bots/api#message>`_ object
        """
        return self._sendFile(audio, 'audio', {'chat_id': chat_id, 'duration': duration, 'performer': performer, 'title': title, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendDocument(self, chat_id, document, reply_to_message_id=None, reply_markup=None):
        """
        Send general files. Bots can currently send files of any type of up to 50 MB in size, this limit may be changed in the future.
        
        **Bot API method:** `sendDocument <https://core.telegram.org/bots/api#senddocument>`_

        :type chat_id: integer
        :param chat_id: Unique identifier for the message recipient - \
        `User <https://core.telegram.org/bots/api#user>`_ or `GroupChat <https://core.telegram.org/bots/api#groupchat>`_ id
        
        :type document: file or string
        :param document: File to send. You can either pass a ``file_id`` as string to resend a file that is already on \
        Telegram servers, or upload a new file that is stored locally.
        
        :type reply_to_message_id: integer
        :param reply_to_message_id: If the message is a reply, ID of the original message.

        :type reply_markup: dict
        :param reply_markup: Additional interface options: \
        `ReplyKeyboardMarkup <https://core.telegram.org/bots/api#replykeyboardmarkup>`_ for a `custom reply keyboard <https://core.telegram.org/bots#keyboards>`_, \
        `ReplyKeyboardHide <https://core.telegram.org/bots/api#replykeyboardhide>`_ to hide a custom keyboard, \
        or `ForceReply <https://core.telegram.org/bots/api#forcereply>`_ to force a reply from the user.

        :return: the sent `Message <https://core.telegram.org/bots/api#message>`_ object
        """
        return self._sendFile(document, 'document', {'chat_id': chat_id, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendSticker(self, chat_id, sticker, reply_to_message_id=None, reply_markup=None):
        """
        Send .webp stickers.

        **Bot API method:** `sendSticker <https://core.telegram.org/bots/api#sendsticker>`_

        :type chat_id: integer
        :param chat_id: Unique identifier for the message recipient - \
        `User <https://core.telegram.org/bots/api#user>`_ or `GroupChat <https://core.telegram.org/bots/api#groupchat>`_ id
        
        :type sticker: file or string
        :param sticker: Sticker to send. You can either pass a ``file_id`` as string to resend a sticker that is already on \
        Telegram servers, or upload a new sticker that is stored locally.
        
        :type reply_to_message_id: integer
        :param reply_to_message_id: If the message is a reply, ID of the original message.

        :type reply_markup: dict
        :param reply_markup: Additional interface options: \
        `ReplyKeyboardMarkup <https://core.telegram.org/bots/api#replykeyboardmarkup>`_ for a `custom reply keyboard <https://core.telegram.org/bots#keyboards>`_, \
        `ReplyKeyboardHide <https://core.telegram.org/bots/api#replykeyboardhide>`_ to hide a custom keyboard, \
        or `ForceReply <https://core.telegram.org/bots/api#forcereply>`_ to force a reply from the user.

        :return: the sent `Message <https://core.telegram.org/bots/api#message>`_ object
        """
        return self._sendFile(sticker, 'sticker', {'chat_id': chat_id, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendVideo(self, chat_id, video, duration=None, caption=None, reply_to_message_id=None, reply_markup=None):
        """
        Send video files. Telegram clients support mp4 videos. Other formats may be sent using ``sendDocument()``.
        Bots can currently send video files of up to 50 MB in size, this limit may be changed in the future.

        **Bot API method:** `sendVideo <https://core.telegram.org/bots/api#sendvideo>`_

        :type chat_id: integer
        :param chat_id: Unique identifier for the message recipient - \
        `User <https://core.telegram.org/bots/api#user>`_ or `GroupChat <https://core.telegram.org/bots/api#groupchat>`_ id
        
        :type video: file or string
        :param video: Video to send. You can either pass a ``file_id`` as string to resend a video that is already on \
        Telegram servers, or upload a new video that is stored locally.

        :type duration: integer
        :param duration: Duration of sent video in seconds

        :type caption: string
        :param caption: Video caption
        
        :type reply_to_message_id: integer
        :param reply_to_message_id: If the message is a reply, ID of the original message.

        :type reply_markup: dict
        :param reply_markup: Additional interface options: \
        `ReplyKeyboardMarkup <https://core.telegram.org/bots/api#replykeyboardmarkup>`_ for a `custom reply keyboard <https://core.telegram.org/bots#keyboards>`_, \
        `ReplyKeyboardHide <https://core.telegram.org/bots/api#replykeyboardhide>`_ to hide a custom keyboard, \
        or `ForceReply <https://core.telegram.org/bots/api#forcereply>`_ to force a reply from the user.

        :return: the sent `Message <https://core.telegram.org/bots/api#message>`_ object
        """
        return self._sendFile(video, 'video', {'chat_id': chat_id, 'duration': duration, 'caption': caption, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendVoice(self, chat_id, audio, duration=None, reply_to_message_id=None, reply_markup=None):
        """
        Send audio files, if you want Telegram clients to display the file as a playable voice message.
        For this to work, your audio must be in an .ogg file encoded with OPUS. Other formats may be sent using ``sendAudio()``
        or ``sendDocument()``.
        Bots can currently send voice messages of up to 50 MB in size, this limit may be changed in the future.

        **Bot API method:** `sendVoice <https://core.telegram.org/bots/api#sendvoice>`_

        :type chat_id: integer
        :param chat_id: Unique identifier for the message recipient - \
        `User <https://core.telegram.org/bots/api#user>`_ or `GroupChat <https://core.telegram.org/bots/api#groupchat>`_ id
        
        :type audio: file or string
        :param audio: Audio file to send. You can either pass a ``file_id`` as string to resend an audio that is already on \
        Telegram servers, or upload a new audio file that is stored locally.

        :type duration: integer
        :param duration: Duration of sent audio in seconds
        
        :type reply_to_message_id: integer
        :param reply_to_message_id: If the message is a reply, ID of the original message.

        :type reply_markup: dict
        :param reply_markup: Additional interface options: \
        `ReplyKeyboardMarkup <https://core.telegram.org/bots/api#replykeyboardmarkup>`_ for a `custom reply keyboard <https://core.telegram.org/bots#keyboards>`_, \
        `ReplyKeyboardHide <https://core.telegram.org/bots/api#replykeyboardhide>`_ to hide a custom keyboard, \
        or `ForceReply <https://core.telegram.org/bots/api#forcereply>`_ to force a reply from the user.

        :return: the sent `Message <https://core.telegram.org/bots/api#message>`_ object
        """
        return self._sendFile(audio, 'voice', {'chat_id': chat_id, 'duration': duration, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup})

    def sendLocation(self, chat_id, latitude, longitude, reply_to_message_id=None, reply_markup=None):
        """
        Send point on the map.

        **Bot API method:** `sendLocation <https://core.telegram.org/bots/api#sendlocation>`_

        :type chat_id: integer
        :param chat_id: Unique identifier for the message recipient - \
        `User <https://core.telegram.org/bots/api#user>`_ or `GroupChat <https://core.telegram.org/bots/api#groupchat>`_ id

        :type latitude: float
        :param latitude: Latitude of location

        :type longitude: float
        :param longitude: Longitude of location

        :type reply_to_message_id: integer
        :param reply_to_message_id: If the message is a reply, ID of the original message.

        :type reply_markup: dict
        :param reply_markup: Additional interface options: \
        `ReplyKeyboardMarkup <https://core.telegram.org/bots/api#replykeyboardmarkup>`_ for a `custom reply keyboard <https://core.telegram.org/bots#keyboards>`_, \
        `ReplyKeyboardHide <https://core.telegram.org/bots/api#replykeyboardhide>`_ to hide a custom keyboard, \
        or `ForceReply <https://core.telegram.org/bots/api#forcereply>`_ to force a reply from the user.

        :return: the sent `Message <https://core.telegram.org/bots/api#message>`_ object
        """
        p = {'chat_id': chat_id, 'latitude': latitude, 'longitude': longitude, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}
        r = requests.post(self._url('sendLocation'), params=self._rectify(p), timeout=http_timeout)
        return self._result(r.json())

    def sendChatAction(self, chat_id, action):
        """
        Tell the user that something is happening on the bot's side. The status is set for 5 seconds or less (when a message 
        arrives from your bot, Telegram clients clear its typing status).

        This method is recommended *only* when a response from the bot will take a noticeable amount of time to arrive.

        **Bot API method:** `sendChatAction <https://core.telegram.org/bots/api#sendchataction>`_

        :type chat_id: integer
        :param chat_id: Unique identifier for the message recipient - \
        `User <https://core.telegram.org/bots/api#user>`_ or `GroupChat <https://core.telegram.org/bots/api#groupchat>`_ id

        :type action: string
        :param action: Type of action to broadcast. Choose one, depending on what the user is about to receive: \
        *typing* for text messages, \
        *upload_photo* for photos, \
        *record_video* or *upload_video* for videos, \
        *record_audio* or *upload_audio* for audio files, \
        *upload_document* for general files, \
        *find_location* for location data.
        """
        p = {'chat_id': chat_id, 'action': action}
        r = requests.post(self._url('sendChatAction'), params=self._rectify(p), timeout=http_timeout)
        return self._result(r.json())

    def getUserProfilePhotos(self, user_id, offset=None, limit=None):
        """
        Get a list of profile pictures for a user.

        **Bot API method:** `getUserProfilePhotos <https://core.telegram.org/bots/api#getuserprofilephotos>`_

        :type user_id: integer
        :param user_id: Unique identifier of the target user

        :type offset: integer
        :param offset: Sequential number of the first photo to be returned. If not given, all photos are returned.

        :type limit: integer
        :param limit: Limits the number of photos to be retrieved. Values between 1-100 are accepted. Defaults to 100 if not given.

        :return: a `UserProfilePhotos <https://core.telegram.org/bots/api#userprofilephotos>`_ object
        """
        p = {'user_id': user_id, 'offset': offset, 'limit': limit}
        r = requests.post(self._url('getUserProfilePhotos'), params=self._rectify(p), timeout=http_timeout)
        return self._result(r.json())

    def getUpdates(self, offset=None, limit=None, timeout=None):
        """
        Receive incoming updates using `long polling <https://en.wikipedia.org/wiki/Push_technology#Long_polling>`_.
        
        **Bot API method:** `getUpdates <https://core.telegram.org/bots/api#getupdates>`_

        :type offset: integer
        :param offset: Identifier of the first update to be returned. Must be greater by one than the highest among \
                       the identifiers of previously received updates. By default, updates starting with the earliest \
                       unconfirmed update are returned. An update is considered confirmed as soon as ``getUpdates()`` \
                       is called with an ``offset`` higher than its ``update_id``.

        :type limit: integer
        :param limit: Limits the number of updates to be retrieved. Values between 1-100 are accepted. \
        Defaults to 100 if not given.

        :type timeout: integer
        :param timeout: Timeout in seconds for long polling. Defaults to 0, i.e. usual short polling, if not given.

        :return: an array of `Update <https://core.telegram.org/bots/api#update>`_ objects
        
        **Note:**
            #. This method will not work if a webhook is set up.
            #. In order to avoid getting duplicate updates, recalculate ``offset`` after each server response.
        """
        p = {'offset': offset, 'limit': limit, 'timeout': timeout}
        r = requests.post(self._url('getUpdates'), params=self._rectify(p), timeout=http_timeout+(0 if timeout is None else timeout))
        return self._result(r.json())

    def setWebhook(self, url=None):
        """
        Specify a url and receive incoming updates via an outgoing webhook. Whenever there is an update for the bot, 
        Telegram will send an HTTPS POST request to the specified url, containing a JSON-serialized 
        `Update <https://core.telegram.org/bots/api#update>`_ object. In case of an unsuccessful request, it will give up 
        after a reasonable amount of attempts.

        If you'd like to make sure that the Webhook request comes from Telegram, use a secret path in the URL, 
        e.g. www.example.com/<token>. Since nobody else knows your bot's token, you can be pretty sure it's Telegram.

        **Bot API method:** `setWebhook <https://core.telegram.org/bots/api#setwebhook>`_

        :type url: string
        :param url: HTTPS url to send updates to. Use None or an empty string to remove webhook integration.

        **Note:**
            #. You will not be able to receive updates using ``getUpdates()`` for as long as an outgoing webhook is set up.
            #. Telegram currently do not support self-signed certificates.
            #. Ports currently supported for Webhooks: **443, 80, 88, 8443**.
        """
        p = {'url': url}
        r = requests.post(self._url('setWebhook'), params=self._rectify(p), timeout=http_timeout)
        return self._result(r.json())

    def notifyOnMessage(self, callback, relax=1, timeout=20):
        """
        Spawn a thread to constantly ``getUpdates()``. Apply ``callback`` to every message received.
        ``callback`` must take one argument, which is the message.

        This method allows you to change the callback function by ``notifyOnMessage(new_callback)``. 
        If you don't want to receive messages anymore, cancel the callback by ``notifyOnMessage(None)``. 
        After the callback is cancelled, the message-checking thread will terminate. 
        If a new callback is set later, a new thread will be spawned again.

        :type callback: function
        :param callback: a function to apply to every message received

        :type relax: integer
        :param relax: seconds between each ``getUpdates()``

        :type timeout: integer
        :param timeout: timeout supplied to ``getUpdates()``, controlling how long to poll.
        """

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
