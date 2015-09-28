from functools import reduce

def pick(obj, key):
    if type(obj) is dict:
        return obj[key]
    else:
        if key == 'from':
            key = 'from_'
        
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
    try:
        levels = key.split('__')
        part = reduce(pick, levels, msg)

    except (KeyError, AttributeError):
        return False

    return match(part, template)

def ok(msg, *args, **kwargs):
    return (all(map(match, [msg]*len(args), args)) and 
            all(map(kmatch, [msg]*len(kwargs), *zip(*kwargs.items()))))
                                              # e.g. {'a':1, 'b':2} -> [('a','b'), (1,2)]
