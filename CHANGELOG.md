# telepot changelog

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
