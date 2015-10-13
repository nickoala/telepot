from functools import reduce

def pick(obj, key):
    if type(obj) is dict:
        return obj[key]
    else:
        return getattr(obj, key)

def match(part, template):
    if type(template) is dict:
        try:
            return all([match(pick(part,k),v) for k,v in template.items()])

        except (KeyError, AttributeError):
            return False

    elif callable(template):
        return template(part)

    else:
        return part == template

def kmatch(msg, key, template):
    if key == '_':
        part = msg
    else:
        try:
            levels = key.split('__')
            part = reduce(pick, levels, msg)
            # Drill down one level at a time, similar to:
            #   reduce(lambda a,b: a[b], ['chat', 'id'], msg)

        except (KeyError, AttributeError):
            return False

    return match(part, template)
    # Do not bracket `match()` in above `try` clause because 
    # `template()` may produce its own errors.

def ok(msg, **kwargs):
    return all(map(kmatch, [msg]*len(kwargs), *zip(*kwargs.items())))
                                            # e.g. {'a':1, 'b':2} -> [('a','b'), (1,2)]
