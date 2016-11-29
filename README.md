# telepot - Python framework for Telegram Bot API

### [Introduction »](http://telepot.readthedocs.io/en/latest/)
### [Reference »](http://telepot.readthedocs.io/en/latest/reference.html)
### [Examples »](https://github.com/nickoala/telepot/tree/master/examples)

### Recent changes

**10.2 (2016-11-29)**

- Recognized `channel_post` and `edited_channel_post` in Update object
- Removed flavor `edited_chat`. Keep 4 flavors: `chat`, `callback_query`,
  `inline_query`, and `chosen_inline_result`. When dealing with `chat` messages,
  it is up to the user to differentiate between various kinds, e.g. new/edited,
  private/group/supergroup/channel, etc.
- `setGameScore()` has parameter `force` and `disable_edit_message`
- `answerCallbackQuery()` has parameter `cache_time`
- `Message` namedtuple has field `forward_from_message_id`
- Renamed `ReplyKeyboardHide` to `ReplyKeyboardRemove`

**10.1 (2016-10-25)**

- Used the presence of `chat_instance` to recognize the flavor `callback_query`

**10.0 (2016-10-19)**

- Implemented [Gaming Platform](https://core.telegram.org/bots/games) stuff
- Added game-related methods, e.g. `sendGame`, `setGameScore`, etc.
- Added game-related namedtuple, e.g. `InlineQueryResultGame`, etc.
- `telepot.glance()` may return content type `game`
- Added method `getWebhookInfo`
- Added new parameters to some methods, e.g. `caption` for `sendAudio()`, etc.
- Handled `EventNotFound` in `IdleEventCoordinator.refresh()`
