"""
This module has a bunch of key function factories and routing table factories
to facilitate the use of :class:`.Router`.

Things to remember:

1. A key function takes one argument - the message, and returns a key, optionally
   followed by positional arguments and keyword arguments.

2. A routing table is just a dictionary. After obtaining one from a factory
   function, you can customize it to your liking.
"""

import re
from . import glance, _isstring, all_content_types

def by_content_type():
    """
    :return:
        A key function that returns a 2-tuple (content_type, (msg[content_type],)).
        In plain English, it returns the message's *content type* as the key,
        and the corresponding content as a positional argument to the handler
        function.
    """
    def f(msg):
        content_type = glance(msg, flavor='chat')[0]
        return content_type, (msg[content_type],)
    return f

def by_command(extractor, prefix=('/',), separator=' ', pass_args=False):
    """
    :param extractor:
        a function that takes one argument (the message) and returns a portion
        of message to be interpreted. To extract the text of a chat message,
        use ``lambda msg: msg['text']``.

    :param prefix:
        a list of special characters expected to indicate the head of a command.

    :param separator:
        a command may be followed by arguments separated by ``separator``.

    :type pass_args: bool
    :param pass_args:
        If ``True``, arguments following a command will be passed to the handler
        function.

    :return:
        a key function that interprets a specific part of a message and returns
        the embedded command, optionally followed by arguments. If the text is
        not preceded by any of the specified ``prefix``, it returns a 1-tuple
        ``(None,)`` as the key. This is to distinguish with the special
        ``None`` key in routing table.
    """
    if not isinstance(prefix, (tuple, list)):
        prefix = (prefix,)

    def f(msg):
        text = extractor(msg)
        for px in prefix:
            if text.startswith(px):
                chunks = text[len(px):].split(separator)
                return chunks[0], (chunks[1:],) if pass_args else ()
        return (None,),  # to distinguish with `None`
    return f

def by_chat_command(prefix=('/',), separator=' ', pass_args=False):
    """
    :param prefix:
        a list of special characters expected to indicate the head of a command.

    :param separator:
        a command may be followed by arguments separated by ``separator``.

    :type pass_args: bool
    :param pass_args:
        If ``True``, arguments following a command will be passed to the handler
        function.

    :return:
        a key function that interprets a chat message's text and returns
        the embedded command, optionally followed by arguments. If the text is
        not preceded by any of the specified ``prefix``, it returns a 1-tuple
        ``(None,)`` as the key. This is to distinguish with the special
        ``None`` key in routing table.
    """
    return by_command(lambda msg: msg['text'], prefix, separator, pass_args)

def by_text():
    """
    :return:
        a key function that returns a message's ``text`` field.
    """
    return lambda msg: msg['text']

def by_data():
    """
    :return:
        a key function that returns a message's ``data`` field.
    """
    return lambda msg: msg['data']

def by_regex(extractor, regex, key=1):
    """
    :param extractor:
        a function that takes one argument (the message) and returns a portion
        of message to be interpreted. To extract the text of a chat message,
        use ``lambda msg: msg['text']``.

    :type regex: str or regex object
    :param regex: the pattern to look for

    :param key: the part of match object to be used as key

    :return:
        a key function that returns ``match.group(key)`` as key (where ``match``
        is the match object) and the match object as a positional argument.
        If no match is found, it returns a 1-tuple ``(None,)`` as the key.
        This is to distinguish with the special ``None`` key in routing table.
    """
    if _isstring(regex):
        regex = re.compile(regex)

    def f(msg):
        text = extractor(msg)
        match = regex.search(text)
        if match:
            index = key if isinstance(key, tuple) else (key,)
            return match.group(*index), (match,)
        else:
            return (None,),  # to distinguish with `None`
    return f

def process_key(processor, fn):
    """
    :param processor:
        a function to process the key returned by the supplied key function

    :param fn:
        a key function

    :return:
        a function that wraps around the supplied key function to further
        process the key before returning.
    """
    def f(*aa, **kw):
        k = fn(*aa, **kw)
        if isinstance(k, (tuple, list)):
            return (processor(k[0]),) + tuple(k[1:])
        else:
            return processor(k)
    return f

def lower_key(fn):
    """
    :param fn: a key function

    :return:
        a function that wraps around the supplied key function to ensure
        the returned key is in lowercase.
    """
    def lower(key):
        try:
            return key.lower()
        except AttributeError:
            return key
    return process_key(lower, fn)

def upper_key(fn):
    """
    :param fn: a key function

    :return:
        a function that wraps around the supplied key function to ensure
        the returned key is in uppercase.
    """
    def upper(key):
        try:
            return key.upper()
        except AttributeError:
            return key
    return process_key(upper, fn)

def make_routing_table(obj, keys, prefix='on_'):
    """
    :return:
        a dictionary roughly equivalent to ``{'key1': obj.on_key1, 'key2': obj.on_key2, ...}``,
        but ``obj`` does not have to define all methods. It may define the needed ones only.

    :param obj: the object

    :param keys: a list of keys

    :param prefix: a string to be prepended to keys to make method names
    """
    def maptuple(k):
        if isinstance(k, tuple):
            if len(k) == 2:
                return k
            elif len(k) == 1:
                return k[0], lambda *aa, **kw: getattr(obj, prefix+k[0])(*aa, **kw)
            else:
                raise ValueError()
        else:
            return k, lambda *aa, **kw: getattr(obj, prefix+k)(*aa, **kw)
                      # Use `lambda` to delay evaluation of `getattr`.
                      # I don't want to require definition of all methods.
                      # Let users define only the ones he needs.

    return dict([maptuple(k) for k in keys])

def make_content_type_routing_table(obj, prefix='on_'):
    """
    :return:
        a dictionary covering all available content types, roughly equivalent to
        ``{'text': obj.on_text, 'photo': obj.on_photo, ...}``,
        but ``obj`` does not have to define all methods. It may define the needed ones only.

    :param obj: the object

    :param prefix: a string to be prepended to content types to make method names
    """
    return make_routing_table(obj, all_content_types, prefix)
