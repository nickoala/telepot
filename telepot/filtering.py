def pick(obj, keys):
    def pick1(k):
        if type(obj) is dict:
            return obj[k]
        else:
            return getattr(obj, k)

    if isinstance(keys, list):
        return [pick1(k) for k in keys]
    else:
        return pick1(keys)

def match(data, template):
    if isinstance(template, dict) and isinstance(data, dict):
        def pick_and_match(kv):
            template_key, template_value = kv
            if hasattr(template_key, 'search'):  # regex
                data_keys = list(filter(template_key.search, data.keys()))
                if not data_keys:
                    return False
            elif template_key in data:
                data_keys = [template_key]
            else:
                return False
            return any(map(lambda data_value: match(data_value, template_value), pick(data, data_keys)))

        return all(map(pick_and_match, template.items()))
    elif callable(template):
        return template(data)
    else:
        return data == template

def match_all(msg, templates):
    return all(map(lambda t: match(msg, t), templates))
