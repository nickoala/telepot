try:
    import urllib3.fields

    # Do not encode unicode filename, so Telegram servers understand it.
    def _noencode_filename(fn):
        def w(name, value):
            if name == 'filename':
                return '%s="%s"' % (name, value)
            else:
                return fn(name, value)
        return w

    urllib3.fields.format_header_param = _noencode_filename(urllib3.fields.format_header_param)

except (ImportError, AttributeError):
    pass
