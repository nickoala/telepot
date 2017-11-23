import asyncio
import aiohttp
import async_timeout
import atexit
import re
import json
from .. import exception
from ..api import _methodurl, _which_pool, _fileurl, _guess_filename

_loop = asyncio.get_event_loop()

_pools = {
    'default': aiohttp.ClientSession(
                   connector=aiohttp.TCPConnector(limit=10),
                   loop=_loop)
}

_timeout = 30
_proxy = None  # (url, (username, password))

def set_proxy(url, basic_auth=None):
    global _proxy
    if not url:
        _proxy = None
    else:
        _proxy = (url, basic_auth) if basic_auth else (url,)

def _close_pools():
    global _pools
    for s in _pools.values():
        s.close()

atexit.register(_close_pools)

def _create_onetime_pool():
    return aiohttp.ClientSession(
               connector=aiohttp.TCPConnector(limit=1, force_close=True),
               loop=_loop)

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

    data = aiohttp.FormData()

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
        session = _create_onetime_pool()
        cleanup = session.close  # one-time session: remember to close
    else:
        session = _pools[name]
        cleanup = None  # reuse: do not close

    kwargs = {'data':data}
    kwargs.update(user_kw)

    return session.post, (url,), kwargs, timeout, cleanup

async def _parse(response):
    try:
        data = await response.json()
        if data is None:
            raise ValueError()
    except (ValueError, json.JSONDecodeError, aiohttp.ClientResponseError):
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
    fn, args, kwargs, timeout, cleanup = _transform(req, **user_kw)

    if _proxy:
        kwargs['proxy'] = _proxy[0]
        if len(_proxy) > 1:
            kwargs['proxy_auth'] = aiohttp.BasicAuth(*_proxy[1])

    try:
        if timeout is None:
            async with fn(*args, **kwargs) as r:
                return await _parse(r)
        else:
            try:
                with async_timeout.timeout(timeout):
                    async with fn(*args, **kwargs) as r:
                        return await _parse(r)

            except asyncio.TimeoutError:
                raise exception.TelegramError('Response timeout', 504, {})

    except aiohttp.ClientConnectionError:
        raise exception.TelegramError('Connection Error', 400, {})

    finally:
        if cleanup:
            cleanup()  # e.g. closing one-time session

def download(req):
    session = _create_onetime_pool()
    return session, session.get(_fileurl(req), timeout=_timeout)
    # Caller should close session after download is complete
