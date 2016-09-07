import traceback
from functools import wraps
from . import exception
from . import flavor, peel, is_event, chat_flavors, inline_flavors

def _wrap_none(fn):
    def w(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (KeyError, exception.BadFlavor):
            return None
    return w

def per_chat_id(types='all'):
    """
    :param types:
        ``all`` or a list of chat types (``private``, ``group``, ``channel``)

    :return:
        a seeder function that returns the chat id only if the chat type is in ``types``.
    """
    return _wrap_none(lambda msg:
                          msg['chat']['id']
                          if types == 'all' or msg['chat']['type'] in types
                          else None)

def per_chat_id_in(s, types='all'):
    """
    :param s:
        a list or set of chat id

    :param types:
        ``all`` or a list of chat types (``private``, ``group``, ``channel``)

    :return:
        a seeder function that returns the chat id only if the chat id is in ``s``
        and chat type is in ``types``.
    """
    return _wrap_none(lambda msg:
                          msg['chat']['id']
                          if (types == 'all' or msg['chat']['type'] in types) and msg['chat']['id'] in s
                          else None)

def per_chat_id_except(s, types='all'):
    """
    :param s:
        a list or set of chat id

    :param types:
        ``all`` or a list of chat types (``private``, ``group``, ``channel``)

    :return:
        a seeder function that returns the chat id only if the chat id is *not* in ``s``
        and chat type is in ``types``.
    """
    return _wrap_none(lambda msg:
                          msg['chat']['id']
                          if (types == 'all' or msg['chat']['type'] in types) and msg['chat']['id'] not in s
                          else None)

def per_from_id(flavors=chat_flavors+inline_flavors):
    """
    :param flavors:
        ``all`` or a list of flavors

    :return:
        a seeder function that returns the from id only if the message flavor is
        in ``flavors``.
    """
    return _wrap_none(lambda msg:
                          msg['from']['id']
                          if flavors == 'all' or flavor(msg) in flavors
                          else None)

def per_from_id_in(s, flavors=chat_flavors+inline_flavors):
    """
    :param s:
        a list or set of from id

    :param flavors:
        ``all`` or a list of flavors

    :return:
        a seeder function that returns the from id only if the from id is in ``s``
        and message flavor is in ``flavors``.
    """
    return _wrap_none(lambda msg:
                          msg['from']['id']
                          if (flavors == 'all' or flavor(msg) in flavors) and msg['from']['id'] in s
                          else None)

def per_from_id_except(s, flavors=chat_flavors+inline_flavors):
    """
    :param s:
        a list or set of from id

    :param flavors:
        ``all`` or a list of flavors

    :return:
        a seeder function that returns the from id only if the from id is *not* in ``s``
        and message flavor is in ``flavors``.
    """
    return _wrap_none(lambda msg:
                          msg['from']['id']
                          if (flavors == 'all' or flavor(msg) in flavors) and msg['from']['id'] not in s
                          else None)

def per_inline_from_id():
    """
    :return:
        a seeder function that returns the from id only if the message flavor
        is ``inline_query`` or ``chosen_inline_result``
    """
    return per_from_id(flavors=inline_flavors)

def per_inline_from_id_in(s):
    """
    :param s: a list or set of from id
    :return:
        a seeder function that returns the from id only if the message flavor
        is ``inline_query`` or ``chosen_inline_result`` and the from id is in ``s``.
    """
    return per_from_id_in(s, flavors=inline_flavors)

def per_inline_from_id_except(s):
    """
    :param s: a list or set of from id
    :return:
        a seeder function that returns the from id only if the message flavor
        is ``inline_query`` or ``chosen_inline_result`` and the from id is *not* in ``s``.
    """
    return per_from_id_except(s, flavors=inline_flavors)

def per_application():
    """
    :return:
        a seeder function that always returns 1, ensuring at most one delegate is ever spawned
        for the entire application.
    """
    return lambda msg: 1

def per_message(flavors='all'):
    """
    :param flavors: ``all`` or a list of flavors
    :return:
        a seeder function that returns a non-hashable only if the message flavor
        is in ``flavors``.
    """
    return _wrap_none(lambda msg: [] if flavors == 'all' or flavor(msg) in flavors else None)

def per_event_source_id(event_space):
    """
    :return:
        a seeder function that returns an event's source id only if that event's
        source space equals to ``event_space``.
    """
    def f(event):
        if is_event(event):
            v = peel(event)
            if v['source']['space'] == event_space:
                return v['source']['id']
            else:
                return None
        else:
            return None
    return _wrap_none(f)

def per_callback_query_chat_id(types='all'):
    """
    :param types:
        ``all`` or a list of chat types (``private``, ``group``, ``channel``)

    :return:
        a seeder function that returns a callback query's originating chat id
        if the chat type is in ``types``.
    """
    def f(msg):
        if (flavor(msg) == 'callback_query' and 'message' in msg
            and (types == 'all' or msg['message']['chat']['type'] in types)):
            return msg['message']['chat']['id']
        else:
            return None
    return f

def per_callback_query_origin(origins='all'):
    """
    :param origins:
        ``all`` or a list of origin types (``chat``, ``inline``)

    :return:
        a seeder function that returns a callback query's origin identifier if
        that origin type is in ``origins``. The origin identifier is guaranteed
        to be a tuple.
    """
    def f(msg):
        def origin_type_ok():
            return (origins == 'all'
                or ('chat' in origins and 'message' in msg)
                or ('inline' in origins and 'inline_message_id' in msg))

        if flavor(msg) == 'callback_query' and origin_type_ok():
            if 'inline_message_id' in msg:
                return msg['inline_message_id'],
            else:
                return msg['message']['chat']['id'], msg['message']['message_id']
        else:
            return None
    return f

def call(func, *args, **kwargs):
    """
    :return:
        a delegator function that returns a tuple (``func``, (seed tuple,)+ ``args``, ``kwargs``).
        That is, seed tuple is inserted before supplied positional arguments.
        By default, a thread wrapping ``func`` and all those arguments is spawned.
    """
    def f(seed_tuple):
        return func, (seed_tuple,)+args, kwargs
    return f

def create_run(cls, *args, **kwargs):
    """
    :return:
        a delegator function that calls the ``cls`` constructor whose arguments being
        a seed tuple followed by supplied ``*args`` and ``**kwargs``, then returns
        the object's ``run`` method. By default, a thread wrapping that ``run`` method
        is spawned.
    """
    def f(seed_tuple):
        j = cls(seed_tuple, *args, **kwargs)
        return j.run
    return f

def create_open(cls, *args, **kwargs):
    """
    :return:
        a delegator function that calls the ``cls`` constructor whose arguments being
        a seed tuple followed by supplied ``*args`` and ``**kwargs``, then returns
        a looping function that uses the object's ``listener`` to wait for messages
        and invokes instance method ``open``, ``on_message``, and ``on_close`` accordingly.
        By default, a thread wrapping that looping function is spawned.
    """
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

            # These exceptions are "normal" exits.
            except (exception.IdleTerminate, exception.StopListening) as e:
                j.on_close(e)

            # Any other exceptions are accidents. **Print it out.**
            # This is to prevent swallowing exceptions in the case that on_close()
            # gets overridden but fails to account for unexpected exceptions.
            except Exception as e:
                traceback.print_exc()
                j.on_close(e)

        return wait_loop
    return f

def until(condition, fns):
    """
    Try a list of seeder functions until a condition is met.

    :param condition:
        a function that takes one argument - a seed - and returns ``True``
        or ``False``

    :param fns:
        a list of seeder functions

    :return:
        a "composite" seeder function that calls each supplied function in turn,
        and returns the first seed where the condition is met. If the condition
        is never met, it returns ``None``.
    """
    def f(msg):
        for fn in fns:
            seed = fn(msg)
            if condition(seed):
                return seed
        return None
    return f

def chain(*fns):
    """
    :return:
        a "composite" seeder function that calls each supplied function in turn,
        and returns the first seed that is not ``None``.
    """
    return until(lambda seed: seed is not None, fns)

def _ensure_seeders_list(fn):
    @wraps(fn)
    def e(seeders, *aa, **kw):
        return fn(seeders if isinstance(seeders, list) else [seeders], *aa, **kw)
    return e

@_ensure_seeders_list
def pair(seeders, delegator_factory, *args, **kwargs):
    """
    The basic pair producer.

    :return:
        a (seeder, delegator_factory(\*args, \*\*kwargs)) tuple.

    :param seeders:
        If it is a seeder function or a list of one seeder function, it is returned
        as the final seeder. If it is a list of more than one seeder function, they
        are chained together before returned as the final seeder.
    """
    return (chain(*seeders) if len(seeders) > 1 else seeders[0],
            delegator_factory(*args, **kwargs))

def _natural_numbers():
    x = 0
    while 1:
        x += 1
        yield x

_event_space = _natural_numbers()

def pave_event_space(fn=pair):
    """
    :return:
        a pair producer that ensures the seeder and delegator share the same event space.
    """
    global _event_space
    event_space = next(_event_space)

    @_ensure_seeders_list
    def p(seeders, delegator_factory, *args, **kwargs):
        return fn(seeders + [per_event_source_id(event_space)],
                  delegator_factory, *args, event_space=event_space, **kwargs)
    return p

def include_callback_query_chat_id(fn=pair, types='all'):
    """
    :return:
        a pair producer that enables static callback query capturing
        across seeder and delegator.

    :param types:
        ``all`` or a list of chat types (``private``, ``group``, ``channel``)
    """
    @_ensure_seeders_list
    def p(seeders, delegator_factory, *args, **kwargs):
        return fn(seeders + [per_callback_query_chat_id(types=types)],
                  delegator_factory, *args, include_callback_query=True, **kwargs)
    return p

from . import helper

def intercept_callback_query_origin(fn=pair, origins='all'):
    """
    :return:
        a pair producer that enables dynamic callback query origin mapping
        across seeder and delegator.

    :param origins:
        ``all`` or a list of origin types (``chat``, ``inline``).
        Origin mapping is only enabled for specified origin types.
    """
    origin_map = helper.SafeDict()

    # For key functions that returns a tuple as key (e.g. per_callback_query_origin()),
    # wrap the key in another tuple to prevent router from mistaking it as
    # a key followed by some arguments.
    def tuplize(fn):
        def tp(msg):
            return (fn(msg),)
        return tp

    router = helper.Router(tuplize(per_callback_query_origin(origins=origins)),
                           origin_map)

    def modify_origin_map(origin, dest, set):
        if set:
            origin_map[origin] = dest
        else:
            try:
                del origin_map[origin]
            except KeyError:
                pass

    if origins == 'all':
        intercept = modify_origin_map
    else:
        intercept = (modify_origin_map if 'chat' in origins else False,
                     modify_origin_map if 'inline' in origins else False)

    @_ensure_seeders_list
    def p(seeders, delegator_factory, *args, **kwargs):
        return fn(seeders + [_wrap_none(router.map)],
                  delegator_factory, *args, intercept_callback_query=intercept, **kwargs)
    return p
