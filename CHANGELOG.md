# telepot changelog

## 12.5 (2017-11-28)

- Bot API 3.5
- Added method `sendMediaGroup` and namedtuple `InputMediaPhoto` and
  `InputMediaVideo`
- Added parameter `provider_data` to method `sendInvoice`
- Better exception handling in `telepot.aio.api` module

## 12.4 (2017-10-19)

- Bot API 3.4
- Live location:
    - Added `live_period` to method `sendLocation`, and namedtuple
      `InlineQueryResultLocation` and `InputLocationMessageContent`
    - Added method `editMessageLiveLocation` and `stopMessageLiveLocation`
- Added method `setChatStickerSet` and `deleteChatStickerSet`
- Added `sticker_set_name` and `can_set_sticker_set` to namedtuple `Chat`
- Added `caption_entities` to namedtuple `Message`
- Added method `editMessageLiveLocation` and `stopMessageLiveLocation` to class
  `Editor`
- Added method `setChatStickerSet` and `deleteChatStickerSet` to class
  `Administrator`
- Allowed supplying initial `offset` to `MessageLoop`
- Allowed Bot API access through proxy

## 12.3 (2017-08-28)

- Bot API 3.3
- Added new fields to namedtuple `Chat`, `Message`, and `User`
- Included `aiohttp.ClientResponseError` in raising `BadHTTPResponse`
- Added package `telepot.text` to help format Markdown and HTML by applying
  entities

## 12.2 (2017-08-01)

- Bot API 3.2
- Added methods:
    - `getStickerSet()`
    - `uploadStickerFile()`
    - `createNewStickerSet()`
    - `addStickerToSet()`
    - `setStickerPositionInSet()`
    - `deleteStickerFromSet()`
- Added namedtuple `StickerSet`, `MaskPosition`
- Added new fields to `Sticker`
- Added `cancel()` to async `MessageLoop` (no change to traditional counterpart)

## 12.1 (2017-07-04)

- Bot API 3.1
- Added methods:
    - `restrictChatMember()`
    - `promoteChatMember()`
    - `exportChatInviteLink()`
    - `setChatPhoto()`
    - `deleteChatPhoto()`
    - `setChatTitle()`
    - `setChatDescription()`
    - `pinChatMessage()`
    - `unpinChatMessage()`
- Added parameter `until_date` to method `kickChatMember()`
- Added fields to namedtuple `Chat` and `ChatMember`
- Added namedtuple `ChatPhoto`
- Added exception `NotEnoughRightsError` to capture situations where the bot does
  not have enough rights to perform operations on channels, groups, or supergroups.
- Changed some internal function names to be more descriptive, e.g. `_yell()`
  becomes `_invoke()`, `_delay_yell()` becomes `_create_invoker()`.
- Tested on Python 3.6.1

## 12.0 (2017-05-26)

- Bot API 3.0
- Can receive updates containing ShippingQuery and PreCheckoutQuery
- Added flavors `shipping_option` and `pre_checkout_query`
- Added nametuples `Invoice`, `LabeledPrice`, `ShippingOption`, `ShippingAddress`,
  `OrderInfo`, `ShippingQuery`, `PreCheckoutQuery`, `SuccessfulPayment`
- Added method `sendInvoice()`, `answerShippingQuery()`, and `answerPreCheckoutQuery()`
- Added method `deleteMessage()` and `sendVideoNote()`. Added namedtuple `VideoNote`.
- Added new fields to various namedtuples
- Added function `per_invoice_payload` and class `InvoiceHandler`

## 11.0 (2017-05-09)

- Async version compliant with aiohttp2
- Added `telepot.loop` and `telepot.aio.loop` module. Method `message_loop()` deprecated.
  Use class `MessageLoop`, `OrderedWebhook`, or `Webhook` instead.

## 10.5 (2017-03-02)

- In `message_loop()`, delay longer between HTTP 502 responses
- Handled empty JSON responses (async version)
- Added `quote_fields` parameter to aiohttp hack
- Fixed dependency at `aiohttp==1.3`

## 10.4 (2016-12-25)

- Async Bot's scheduler method `event_at()` was modified to use unix timestamp

## 10.3 (2016-12-16)

- Added parameter `max_connections` and `allowed_updates` to method `setWebhook()`
- Added parameter `allowed_updates` to method `getUpdates()` and `message_loop()`
- Added method `deleteWebhook()`

## 10.2 (2016-11-29)

- Recognized `channel_post` and `edited_channel_post` in Update object
- Removed flavor `edited_chat`. Keep 4 flavors: `chat`, `callback_query`,
  `inline_query`, and `chosen_inline_result`. When dealing with `chat` messages,
  it is up to the user to differentiate between various kinds, e.g. new/edited, private/group/supergroup/channel, etc.
- `setGameScore()` has parameter `force` and `disable_edit_message`
- `answerCallbackQuery()` has parameter `cache_time`
- `Message` namedtuple has field `forward_from_message_id`
- Renamed `ReplyKeyboardHide` to `ReplyKeyboardRemove`

## 10.1 (2016-10-25)

- Used the presence of `chat_instance` to recognize the flavor `callback_query`

## 10.0 (2016-10-19)

- Implemented Gaming Platform stuff
- Added game-related methods, e.g. `sendGame`, `setGameScore`, etc.
- Added game-related namedtuple, e.g. `InlineQueryResultGame`, etc.
- `telepot.glance()` may return content type `game`
- Added method `getWebhookInfo`
- Added new parameters to some methods, e.g. `caption` for `sendAudio()`, etc.
- Handled `EventNotFound` in `IdleEventCoordinator.refresh()`

## 9.1 (2016-08-26)

- Changed the name `pave_callback_query_origin_map()` to `intercept_callback_query_origin()`
- Added `include_callback_query_chat_id()`

## 9.0 (2016-08-25)

- I am finally satisfied with callback query handling. Many styles of dealing with
callback query are now possible.
- Added a few `per_callback_query_*()` seeder factories
- Added a few pair producers, e.g. `pave_event_space()`, `pave_callback_query_origin_map()`
- Added `Bot.Scheduler` to schedule internal events
- Invented a standard event format for delegates to create their own events easily
- Improved Mixin framework. Added `StandardEventMixin`, `IdleTerminateMixin`, and
`InterceptCallbackQueryMixin`.
- Added `CallbackQueryOriginHandler`
- Revamped `Listener` and message capture specifications
- Default `retries=3` for `urllib3`
- Relaxed `urllib3>=1.9.1` in `setup.py`

## 8.3 (2016-07-17)

- Fixed `urllib3==1.9.1` in `setup.py`

## 8.2 (2016-07-04)

- Handling of callback query still unsatisfactory, a transitional release
- Changed async version to `telepot.aio` to avoid collision with `async` keyword
- Added `CallbackQueryCoordinator` and `CallbackQueryAble` to facilitate transparent handling of `CallbackQuery`
- Added `AnswererMixin` to give an `Answerer` instance
- Added `Timer` to express different timeout behaviors
- Added `enable_callback_query` parameter to `*Handler` constructors
- Added default `on_timeout` method to `@openable` decorator
- Added `IdleTerminate` and `AbsentCallbackQuery` as subclasses of `WaitTooLong` to distinguish between different timeout situations
- Revamped `Listener` to handle different timeout requirements
- Added `types` parameter to `per_chat_id()`
- By default, `per_from_id()` and `UserHandler` reacts to non-`callback_query` only
- Fixed `Bot.download_file()`
- Added docstrings for Sphinx generation
- Re-organized examples

## 8.1 (2016-05-26)

- Added flavor `edited_chat` and handler function `on_edited_chat_message`
- New Bot API methods: `getChat`, `leaveChat`, `getChatAdministrators`, `getChatMember`, and `getChatMembersCount`
- Added namedtuple `ChatMember` and other new fields
- No longer dependent on `requests`. Use `urllib3` throughout (traditional version).
- Start adding docstring and using Sphinx to generate documentations.

## 8.0 (2016-05-13)

- Added HTTP connection pooling (for both traditional and async version). Bot API requests are much speedier.
- Most requests are now done with `urllib3`, moving away from `requests`.
- Added module `telepot.routing` and `telepot.async.routing` to provide common key functions and routing tables for `Router` to use.
- Removed method `set_key_function` and `set_routing_table` from `Router`. Access instance variable `key_function` and `routing_table` instead.
- Added function `telepot.message_identifier` to extract message identifier for editing messages.
- Added helper class `Editor` to ease editing messages.
- `ChatHandler`, by default, also captures `callback_query` from the same user.
- Added `InlineUserHandler` to capture only inline-related messages.
- Async version uses `async`/`await`, stops supporting Python 3.4, works on Python 3.5+ from now on.

## 7.1 (2016-04-24)

- Patched `requests` and `aiohttp` to send unicode filenames

## 7.0 (2016-04-18)

- Bot API 2.0
    - Added new flavor `callback_query`
    - Added a bunch of namedtuples to reflect new objects in Bot API
    - Added methods:
        - `sendVenue()`, `sendContact()`
        - `kickChatMember()`, `unbanChatMember()`
        - `answerCallbackQuery()`
        - `editMessageText()`, `editMessageCaption()`, `editMessageReplyMarkup()`
    - To `ChatContext`, added a property `administrator`
- Added `telepot.exception.MigratedToSupergroupChatError`
- Backward-incompatible name changes
    - Flavor `normal` → `chat`
    - Method `notifyOnMessage` → `message_loop`
    - Method `messageLoop` → `message_loop`
    - Method `downloadFile` → `download_file`
    - Function `telepot.namedtuple.namedtuple` was removed. Create namedtuples using their constructors directly.
    - Function `telepot.glance2` was removed. Use `telepot.glance`.
    - Chat messages' content type returned by `telepot.glance`:
        - `new_chat_participant` → `new_chat_member`
        - `left_chat_participant` → `left_chat_member`

## 6.8 (2016-04-11)

- Added underlying response object to `BadHTTPResponse` and underlying JSON object to `TelegramError`
- Added `TooManyRequestsError` as a subclass to `TelegramError`

## 6.7 (2016-04-03)

- Added a few `TelegramError` subclasses to indicate specific errors
- Override `BadHTTPResponse`'s `__unicode__()` and `__str__()` to shorten traceback

## 6.6 (2016-03-20)

- Changed `Answerer` interface. Compute function is now passed to method `answer()`, not to the constructor.
- Added parameter `disable_notification` to methods `sendZZZ()`
- Added function `telepot.delegate.per_application()` and `per_message()`
- Used `data` to pass POST parameters to prevent too-long query strings on URL
- Async version support pushed back to Python 3.4.2

## 6.5 (2016-02-21)

- Supports file-like object and filename when sending files
- Moved all exceptions to module `telepot.exception`
- Expanded testing to Python 3.5

## 6.4 (2016-02-16)

- Introduced automatic message routing to `Bot.handle()` and `ZZZHandler.on_message()`. Messages are routed to sub-handlers according to flavor, by default.
- As an alternative to implementing `Bot.handle(msg)`, you may implement `Bot.on_chat_message(msg)`, `Bot.on_inline_query(msg)`, and `Bot.on_chosen_inline_result(msg)` as needed.
- As an alternative to implementing `ZZZHandler.on_message()`, you may implement `ZZZHandler.on_chat_message(msg)`, `ZZZHandler.on_inline_query(msg)`, and `ZZZHandler.on_chosen_inline_result(msg)` as needed.
- `notifyOnMessage()` and `messageLoop()` accept a dict as callback, routing messages according to flavor.
- Added function `telepot.flavor_router()`, classes `telepot.helper.Router` and `telepot.helper.DefaultRouterMixin`, and their async counterparts to facilitate message routing.
- Many functions in `telepot.delegate` and `telepot.helper` now have aliases in their respective async modules, making imports more symmetric.

## 6.3 (2016-02-06)

- Added `Answerer` class to better deal with inline queries
- Made `telepot.glance()` equivalent to `telepot.glance2()`. Developers are encouraged to use `telepot.glance()` from now on.
- Added `telepot.flance()`, a combination of `telepot.flavor()` and `telepot.glance()`.

## 6.2 (2016-01-18)

- Handle new field `chosen_inline_result` in Update object
- `telepot.flavor()` returns a new flavor `chosen_inline_result`
- Added `telepot.namedtuple.ChosenInlineResult` class

## 6.1 (2016-01-13)

- Changed normal message's flavor to `normal`

## 6.0 (2016-01-13)

- Moved all namedtuple-related stuff to a new module `telepot.namedtuple`. All calls to the function `telepot.namedtuple()` should be changed to `telepot.namedtuple.namedtuple()`
- Added a function `telepot.flavor()` to differentiate between a normal message and an inline query
- Added `flavor` parameter to `telepot.glance2()` to extract info according to message flavor
- `notifyOnMessage()` and `messageLoop()` can handle inline query as well as normal chat messages
- Added a few `per_XXX_id()` functions useful for spawning delegates for inline queries
- Added `UserHandler`
- `reply_markup` parameter can accept namedtuples `ReplyKeyboardMarkup`, `ReplyKeyboardHide`, `ForceReply` as values

## 5.0 (2015-12-28)

- Added webhook interface
- Added `supergroup_chat_created`, `migrate_to_chat_id`, `migrate_from_chat_id`, and `channel_chat_created` fields to Message

## 4.1 (2015-11-03)

- Added `openable()` class decorator
- Default `on_close()` prints out exception
- Async `SpeakerBot` and `DelegatorBot` constructor accepts `loop` parameter

## 4.0 (2015-10-29)

- Revamped `Listener` and `ChatHandler` architecture
- Added `create_open()`

## 3.2 (2015-10-13)

- Conforms to latest Telegram Bot API as of October 8, 2015
- Added `Chat` class, removed `GroupChat`
- Added `glance2()`

## 3.1 (2015-10-08)

- Added `per_chat_id_except()`
- Added lock to `Microphone`, make it thread-safe

## 3.0 (2015-10-05)

- Added listener and delegation mechanism

## 2.6 (2015-09-22)

- Conforms to latest Telegram Bot API as of September 18, 2015
- Added `getFile()` and `downloadFile()` method
- Added `File` namedtuple
- Removed `file_link` field from namedtuples

## 2.51 (2015-09-17)

- In async `messageLoop()`, a regular handler function would be called directly, whereas a coroutine would be allocated a task, using `BaseEventLoop.create_task()`.
- In `messageLoop()` and `notifyOnMessage()`, the `relax` time default is now 0.1 second.

## 2.5 (2015-09-15)

- Fixed `pip install` syntax error
- Having wasted a lot of version numbers, I finally get a better hang of setup.py, pip, and PyPI.

## 2.0 (2015-09-11)

- Conforms to latest Telegram Bot API as of September 7, 2015
- Added an async version for Python 3.4
- Added a `file_link` field to some namedtuples, in response to a not-yet-documented change in Bot API
- Better exception handling on receiving invalid JSON responses

## 1.3 (2015-09-01)

- On receiving unexpected fields, `namedtuple()` would issue a warning and would not break.

## 1.2 (2015-08-30)

- Conforms to latest Telegram Bot API as of August 29, 2015
- Added `certificate` parameters to `setWebhook()`
- Added `telepot.glance()` and `telepot.namedtuple()`
- Consolidated all tests into one script

## 1.1 (2015-08-21)

- Use MIT license

## 1.0 (2015-08-20)

- Conforms to latest Telegram Bot API as of August 15, 2015
- Added `sendVoice()`
- Added `caption` and `duration` parameters to `sendVideo()`
- Added `performer` and `title` parameters to `sendAudio()`
- Test scripts test the module more completely
