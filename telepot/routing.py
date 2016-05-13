import re
from . import glance, _isstring, all_content_types

def by_content_type():
    def f(msg):
        content_type = glance(msg, flavor='chat')[0]
        return content_type, (msg[content_type],)
    return f

def by_command(extractor, prefix=('/',), separator=' ', pass_args=False):
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
    return by_command(lambda msg: msg['text'], prefix, separator, pass_args)

def by_text():
    return lambda msg: msg['text']

def by_data():
    return lambda msg: msg['data']

def by_regex(extractor, regex, key=1):
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
    def f(*aa, **kw):
        k = fn(*aa, **kw)
        if isinstance(k, (tuple, list)):
            return (processor(k[0]),) + tuple(k[1:])
        else:
            return processor(k)
    return f

def lower_key(fn):
    def lower(key):
        try:
            return key.lower()
        except AttributeError:
            return key
    return process_key(lower, fn)

def upper_key(fn):
    def upper(key):
        try:
            return key.upper()
        except AttributeError:
            return key
    return process_key(upper, fn)

def make_routing_table(obj, keys, prefix='on_'):
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
    return make_routing_table(obj, all_content_types, prefix)
