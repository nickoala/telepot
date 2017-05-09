try:
    import aiohttp
    from urllib.parse import quote

    def content_disposition_header(disptype, quote_fields=True, **params):
        if not disptype or not (aiohttp.helpers.TOKEN > set(disptype)):
            raise ValueError('bad content disposition type {!r}'
                             ''.format(disptype))

        value = disptype
        if params:
            lparams = []
            for key, val in params.items():
                if not key or not (aiohttp.helpers.TOKEN > set(key)):
                    raise ValueError('bad content disposition parameter'
                                     ' {!r}={!r}'.format(key, val))

                ###### Do not encode filename
                if key == 'filename':
                    qval = val
                else:
                    qval = quote(val, '') if quote_fields else val

                lparams.append((key, '"%s"' % qval))

            sparams = '; '.join('='.join(pair) for pair in lparams)
            value = '; '.join((value, sparams))
        return value

    # Override original version
    aiohttp.payload.content_disposition_header = content_disposition_header

# In case aiohttp changes and this hack no longer works, I don't want it to
# bog down the entire library.
except (ImportError, AttributeError):
    pass
