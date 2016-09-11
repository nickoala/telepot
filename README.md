# telepot - Python framework for Telegram Bot API

With the release of 9.0 (August 25, 2016), I am finally satisfied with callback query handling.
Many styles of dealing with callback query are now possible.

**[Introduction »](http://telepot.readthedocs.io/en/latest/)**  
**[Reference »](http://telepot.readthedocs.io/en/latest/reference.html)**  
**[Examples »](https://github.com/nickoala/telepot/tree/master/examples)**

### Recent changes

**9.1 (2016-08-26)**

- Changed the name `pave_callback_query_origin_map()` to `intercept_callback_query_origin()`
- Added `include_callback_query_chat_id()`

**9.0 (2016-08-25)**

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
