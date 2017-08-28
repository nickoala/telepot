def _apply_entities(text, entities, escape_map, format_map):
    def inside_entities(i):
        return any(map(lambda e:
                           e['offset'] <= i < e['offset']+e['length'],
                       entities))

    # Split string into char sequence and escape in-place to
    # preserve index positions.
    seq = list(map(lambda c,i:
                       escape_map[c]     # escape special characters
                           if c in escape_map and not inside_entities(i)
                       else c,
                   list(text),           # split string to char sequence
                   range(0,len(text))))  # along with each char's index

    # Ensure smaller offsets come first
    sorted_entities = sorted(entities, key=lambda e: e['offset'])
    offset = 0
    result = ''

    for e in sorted_entities:
        f,n,t = e['offset'], e['length'], e['type']

        result += ''.join(seq[offset:f])

        if t in format_map:
            # apply format
            result += format_map[t](''.join(seq[f:f+n]), e)
        else:
            result += ''.join(seq[f:f+n])

        offset = f + n

    result += ''.join(seq[offset:])
    return result


def apply_entities_as_markdown(text, entities):
    """
    Format text as Markdown. Also take care of escaping special characters.
    Returned value can be passed to :meth:`.Bot.sendMessage` with appropriate
    ``parse_mode``.

    :param text:
        plain text

    :param entities:
        a list of `MessageEntity <https://core.telegram.org/bots/api#messageentity>`_ objects
    """
    escapes = {'*': '\\*',
               '_': '\\_',
               '[': '\\[',
               '`': '\\`',}

    formatters = {'bold':         lambda s,e: '*'+s+'*',
                  'italic':       lambda s,e: '_'+s+'_',
                  'text_link':    lambda s,e: '['+s+']('+e['url']+')',
                  'text_mention': lambda s,e: '['+s+'](tg://user?id='+str(e['user']['id'])+')',
                  'code':         lambda s,e: '`'+s+'`',
                  'pre':          lambda s,e: '```text\n'+s+'```'}

    return _apply_entities(text, entities, escapes, formatters)


def apply_entities_as_html(text, entities):
    """
    Format text as HTML. Also take care of escaping special characters.
    Returned value can be passed to :meth:`.Bot.sendMessage` with appropriate
    ``parse_mode``.

    :param text:
        plain text

    :param entities:
        a list of `MessageEntity <https://core.telegram.org/bots/api#messageentity>`_ objects
    """
    escapes = {'<': '&lt;',
               '>': '&gt;',
               '&': '&amp;',}

    formatters = {'bold':         lambda s,e: '<b>'+s+'</b>',
                  'italic':       lambda s,e: '<i>'+s+'</i>',
                  'text_link':    lambda s,e: '<a href="'+e['url']+'">'+s+'</a>',
                  'text_mention': lambda s,e: '<a href="tg://user?id='+str(e['user']['id'])+'">'+s+'</a>',
                  'code':         lambda s,e: '<code>'+s+'</code>',
                  'pre':          lambda s,e: '<pre>'+s+'</pre>'}

    return _apply_entities(text, entities, escapes, formatters)
