import asyncio
import telepot.delegate
from telepot.helper import WaitTooLong, StopListening
from telepot.async.helper import _yell

# aliases for convenience
per_chat_id = telepot.delegate.per_chat_id
per_chat_id_in = telepot.delegate.per_chat_id_in
per_chat_id_except = telepot.delegate.per_chat_id_except

per_from_id = telepot.delegate.per_from_id
per_from_id_in = telepot.delegate.per_from_id_in
per_from_id_except = telepot.delegate.per_from_id_except

per_inline_from_id = telepot.delegate.per_inline_from_id
per_inline_from_id_in = telepot.delegate.per_inline_from_id_in
per_inline_from_id_except = telepot.delegate.per_inline_from_id_except

def call(corofunc, *args, **kwargs):
    def f(seed_tuple):
        return corofunc(seed_tuple, *args, **kwargs)
    return f

def create_run(cls, *args, **kwargs):
    def f(seed_tuple):
        j = cls(seed_tuple, *args, **kwargs)
        return j.run()
    return f

def create_open(cls, *args, **kwargs):
    def f(seed_tuple):
        j = cls(seed_tuple, *args, **kwargs)

        @asyncio.coroutine
        def wait_loop():
            bot, msg, seed = seed_tuple
            try:
                handled = yield from _yell(j.open, msg, seed)
                if not handled:
                    yield from _yell(j.on_message, msg)

                while 1:
                    msg = yield from j.listener.wait()
                    yield from _yell(j.on_message, msg)

            # These exceptions are "normal" exits.
            except (WaitTooLong, StopListening) as e:
                yield from _yell(j.on_close, e)

            # Any other exceptions are accidents. **Print it out.**
            # This is to prevent swallowing exceptions in the case that on_close()
            # gets overridden but fails to account for unexpected exceptions.
            except Exception as e:
                traceback.print_exc()
                yield from _yell(j.on_close, e)

        return wait_loop()
    return f
