import traceback
from . import exception
from . import flavor, chat_flavors, inline_flavors

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
        and invokes instance method ``open``, ``on_message``, ``on_timeout``,
        and ``on_close`` accordingly.
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
                    try:
                        msg = j.listener.wait()
                        j.on_message(msg)
                    except exception.IdleTerminate:
                        raise
                    except exception.WaitTooLong as e:
                        j.on_timeout(e)

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
