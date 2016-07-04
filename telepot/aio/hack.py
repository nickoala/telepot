try:
    import aiohttp.multipart
    import aiohttp.hdrs
    from urllib.parse import quote

    # Check if these methods are present
    aiohttp.multipart.BodyPartWriter.set_content_disposition
    aiohttp.multipart.BodyPartWriter.serialize

    class NoEncodeFilenameBodyPartWriter(aiohttp.multipart.BodyPartWriter):
        def set_content_disposition(self, disptype, **params):
            if not disptype or not (aiohttp.multipart.TOKEN > set(disptype)):
                raise ValueError('bad content disposition type {!r}'
                                 ''.format(disptype))
            value = disptype
            if params:
                lparams = []
                for key, val in params.items():
                    if not key or not (aiohttp.multipart.TOKEN > set(key)):
                        raise ValueError('bad content disposition parameter'
                                         ' {!r}={!r}'.format(key, val))

                    ###### Do not encode filename
                    if key == 'filename':
                        qval = val
                    else:
                        qval = quote(val, '')

                    lparams.append((key, '"%s"' % qval))

                sparams = '; '.join('='.join(pair) for pair in lparams)
                value = '; '.join((value, sparams))
            self.headers[aiohttp.hdrs.CONTENT_DISPOSITION] = value

        def serialize(self):
            """Yields byte chunks for body part."""

            has_encoding = (
                aiohttp.hdrs.CONTENT_ENCODING in self.headers and
                self.headers[aiohttp.hdrs.CONTENT_ENCODING] != 'identity' or
                aiohttp.hdrs.CONTENT_TRANSFER_ENCODING in self.headers
            )
            if has_encoding:
                # since we're following streaming approach which doesn't assumes
                # any intermediate buffers, we cannot calculate real content length
                # with the specified content encoding scheme. So, instead of lying
                # about content length and cause reading issues, we have to strip
                # this information.
                self.headers.pop(aiohttp.hdrs.CONTENT_LENGTH, None)

            if self.headers:
                for item in self.headers.items():
                    ###### Treat content disposition with filename differently
                    if item[0] == aiohttp.hdrs.CONTENT_DISPOSITION and 'filename=' in item[1]:
                        yield b': '.join(map(lambda i: i.encode('utf-8'), item)) + b'\r\n'
                    else:
                        yield b': '.join(map(lambda i: i.encode('latin1'), item)) + b'\r\n'

                yield b'\r\n'
            else:
                yield b'\r\n\r\n'

            yield from self._maybe_encode_stream(self._serialize_obj())
            yield b'\r\n'


    # Force it to use my custom BodyPartWriter
    aiohttp.multipart.MultipartWriter.part_writer_cls = NoEncodeFilenameBodyPartWriter

except (ImportError, AttributeError):
    pass
