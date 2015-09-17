# telepot changelog

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
