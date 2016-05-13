from .helper import _delay_yell
from .. import all_content_types

# Mirror traditional version to avoid having to import one more module
from ..routing import (by_content_type, by_command, by_chat_command,
                       by_text, by_data, by_regex,
                       process_key, lower_key, upper_key)

def make_routing_table(obj, keys, prefix='on_'):
    def maptuple(k):
        if isinstance(k, tuple):
            if len(k) == 2:
                return k
            elif len(k) == 1:
                return k[0], _delay_yell(obj, prefix+k[0])
            else:
                raise ValueError()
        else:
            return k, _delay_yell(obj, prefix+k)

    return dict([maptuple(k) for k in keys])

def make_content_type_routing_table(obj, prefix='on_'):
    return make_routing_table(obj, all_content_types, prefix)
