# telepot - Python framework for Telegram Bot API

Version 8.2 just came out (July 4, 2016). Handling of callback query is still unsatisfactory. Treat it as a transitional release.

**[Tutorial »](http://telepot.readthedocs.io/en/latest/)**  
**[Reference, Traditional version »](http://telepot.readthedocs.io/en/latest/reference.html)**  
**[Reference, Async version »](http://telepot.readthedocs.io/en/latest/referencea.html)** (Having trouble building it on readthedocs.org, I am working on it ...)  
**[Examples »](https://github.com/nickoala/telepot/tree/master/examples)**

### Recent changes

**8.3 (2016-07-17)**

- Fixed `urllib3==1.9.1` in `setup.py`

**8.2 (2016-07-04)**

- Handling of callback query still unsatisfactory, a transitional release
- **Changed async version to `telepot.aio`** to avoid collision with `async` keyword
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
