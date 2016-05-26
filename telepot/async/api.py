import aiohttp
import re
from .. import exception
from ..api import _methodurl, _which_pool, _fileurl, _guess_filename

_pools = {
    'default': aiohttp.TCPConnector(limit=10)
}

_onetime_pool_spec = (aiohttp.TCPConnector, dict(force_close=True))

_timeout = 30


def _create_onetime_pool():
    cls, kw = _onetime_pool_spec
    return cls(**kw)

def _default_timeout(req, **user_kw):
    return _timeout

def _compose_timeout(req, **user_kw):
    token, method, params, files = req

    if method == 'getUpdates' and params and 'timeout' in params:
        # Ensure HTTP timeout is longer than getUpdates timeout
        return params['timeout'] + _default_timeout(req, **user_kw)
    elif files:
        # Disable timeout if uploading files. For some reason, the larger the file,
        # the longer it takes for the server to respond (after upload is finished).
        # It is unclear how long timeout should be.
        return None
    else:
        return _default_timeout(req, **user_kw)

def _compose_data(req, **user_kw):
    token, method, params, files = req

    data = aiohttp.helpers.FormData()

    if params:
        for key,value in params.items():
            data.add_field(key, str(value))

    if files:
        for key,f in files.items():
            if isinstance(f, tuple):
                if len(f) == 2:
                    filename, fileobj = f
                else:
                    raise ValueError('Tuple must have exactly 2 elements: filename, fileobj')
            else:
                filename, fileobj = _guess_filename(f) or key, f

            data.add_field(key, fileobj, filename=filename)

    return data

def _transform(req, **user_kw):
    timeout = _compose_timeout(req, **user_kw)

    data = _compose_data(req, **user_kw)

    url = _methodurl(req, **user_kw)

    name = _which_pool(req, **user_kw)

    if name is None:
        connector = _create_onetime_pool()
    else:
        connector = _pools[name]

    kwargs = {'data':data, 'connector':connector}
    kwargs.update(user_kw)

    return aiohttp.post, (url,), kwargs, timeout

async def _parse(response):
    try:
        data = await response.json()
    except ValueError:
        text = await response.text()
        raise exception.BadHTTPResponse(response.status, text, response)

    if data['ok']:
        return data['result']
    else:
        description, error_code = data['description'], data['error_code']

        # Look for specific error ...
        for e in exception.TelegramError.__subclasses__():
            n = len(e.DESCRIPTION_PATTERNS)
            if any(map(re.search, e.DESCRIPTION_PATTERNS, n*[description], n*[re.IGNORECASE])):
                raise e(description, error_code, data)

        # ... or raise generic error
        raise exception.TelegramError(description, error_code, data)

async def request(req, **user_kw):
    fn, args, kwargs, timeout = _transform(req, **user_kw)

    if timeout is None:
        async with fn(*args, **kwargs) as r:
            return await _parse(r)
    else:
        with aiohttp.Timeout(timeout):
            async with fn(*args, **kwargs) as r:
                return await _parse(r)

def download(req):
    with aiohttp.Timeout(_timeout):
        return aiohttp.get(_fileurl(req))
