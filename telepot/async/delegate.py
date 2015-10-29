import asyncio

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
            @asyncio.coroutine
            def invoke(func, *a):
                if asyncio.iscoroutinefunction(func):
                    return (yield from func(*a))
                else:
                    return func(*a)

            bot, msg, seed = seed_tuple
            try:
                handled = yield from invoke(j.open, msg, seed)
                if not handled:
                    yield from invoke(j.on_message, msg)

                while 1:
                    msg = yield from j.listener.wait()
                    yield from invoke(j.on_message, msg)

            except Exception as e:
                yield from invoke(j.on_close, e)

        return wait_loop()
    return f
