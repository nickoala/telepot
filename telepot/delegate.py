from telepot import flavor

def _wrap_none(fn):
    def w(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except KeyError:
            return None
    return w

def per_chat_id():
    return _wrap_none(lambda msg: msg['chat']['id'])

def per_chat_id_in(s):
    return _wrap_none(lambda msg: msg['chat']['id'] if msg['chat']['id'] in s else None)

def per_chat_id_except(s):
    return _wrap_none(lambda msg: msg['chat']['id'] if msg['chat']['id'] not in s else None)

def per_from_id():
    return _wrap_none(lambda msg: msg['from']['id'])

def per_from_id_in(s):
    return _wrap_none(lambda msg: msg['from']['id'] if msg['from']['id'] in s else None)

def per_from_id_except(s):
    return _wrap_none(lambda msg: msg['from']['id'] if msg['from']['id'] not in s else None)

def _isinline(msg):
    return flavor(msg) in ['inline_query', 'chosen_inline_result']

def per_inline_from_id():
    return _wrap_none(lambda msg: msg['from']['id'] if _isinline(msg) else None)
    
def per_inline_from_id_in(s):
    return _wrap_none(lambda msg: msg['from']['id'] if _isinline(msg) and msg['from']['id'] in s else None)

def per_inline_from_id_except(s):
    return _wrap_none(lambda msg: msg['from']['id'] if _isinline(msg) and msg['from']['id'] not in s else None)

def call(func, *args, **kwargs):
    def f(seed_tuple):
        return func, (seed_tuple,)+args, kwargs
    return f

def create_run(cls, *args, **kwargs):
    def f(seed_tuple):
        j = cls(seed_tuple, *args, **kwargs)
        return j.run
    return f

def create_open(cls, *args, **kwargs):
    def f(seed_tuple):
        j = cls(seed_tuple, *args, **kwargs)

        def wait_loop():
            bot, msg, seed = seed_tuple
            try:
                handled = j.open(msg, seed)
                if not handled:
                    j.on_message(msg)

                while 1:
                    msg = j.listener.wait()
                    j.on_message(msg)

            except Exception as e:
                j.on_close(e)

        return wait_loop
    return f
