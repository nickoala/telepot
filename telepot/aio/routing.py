from .helper import _create_invoker
from .. import all_content_types

# Mirror traditional version to avoid having to import one more module
from ..routing import (
    by_content_type, by_command, by_chat_command, by_text, by_data, by_regex,
    process_key, lower_key, upper_key
)

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
                return k[0], _create_invoker(obj, prefix+k[0])
            else:
                raise ValueError()
        else:
            return k, _create_invoker(obj, prefix+k)

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
