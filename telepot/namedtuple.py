import collections
import warnings
import sys

_classmap = {}

# Function to produce namedtuple classes.
def _create_class(typename, fields):
    # extract field names
    field_names = [e[0] if type(e) is tuple else e for e in fields]

    # Some dictionary keys are Python keywords and cannot be used as field names, e.g. `from`.
    # Get around by appending a '_', e.g. dict['from'] => namedtuple.from_
    keymap = [(k.rstrip('_'), k) for k in filter(lambda e: e in ['from_'], field_names)]

    # extract (non-simple) fields that need conversions
    conversions = [e[0:2] for e in fields if type(e) is tuple and e[1] is not None]

    # extract default values
    defaults = [e[2] if type(e) is tuple and len(e) >= 3 else None for e in fields]

    # Create the base tuple class, with defaults.
    base = collections.namedtuple(typename, field_names)
    base.__new__.__defaults__ = tuple(defaults)

    class sub(base):
        def __new__(cls, **kwargs):
            # Map keys.
            for oldkey, newkey in keymap:
                kwargs[newkey] = kwargs[oldkey]
                del kwargs[oldkey]

            # Any unexpected arguments?
            unexpected = set(kwargs.keys()) - set(super(sub, cls)._fields)

            # Remove unexpected arguments and issue warning.
            if unexpected:
                for k in unexpected:
                    del kwargs[k]

                s = ('Unexpected fields: ' + ', '.join(unexpected) + ''
                     '\nBot API seems to have added new fields to the returned data.'
                     ' This version of namedtuple is not able to capture them.'
                     '\n\nPlease upgrade telepot by:'
                     '\n  sudo pip install telepot --upgrade'
                     '\n\nIf you still see this message after upgrade, that means I am still working to bring the code up-to-date.'
                     ' Please try upgrade again a few days later.'
                     ' In the meantime, you can access the new fields the old-fashioned way, through the raw dictionary.')

                warnings.warn(s, UserWarning)

            # Convert non-simple values to namedtuples.
            for key, func in conversions:
                if key in kwargs:
                    if type(kwargs[key]) is dict:
                        kwargs[key] = func(**kwargs[key])
                    elif type(kwargs[key]) is list:
                        kwargs[key] = func(kwargs[key])
                    else:
                        raise RuntimeError('Can only convert dict or list')

            return super(sub, cls).__new__(cls, **kwargs)

    # https://bugs.python.org/issue24931
    # Python 3.4 bug: namedtuple subclass does not inherit __dict__ properly.
    # Fix it manually.
    if sys.version_info >= (3,4):
        def _asdict(self):
            return collections.OrderedDict(zip(self._fields, self))
        sub._asdict = _asdict

    sub.__name__ = typename
    _classmap[typename] = sub

    return sub


User = _create_class('User', [
           'id', 
           'first_name', 
           'last_name', 
           'username'
       ])

Chat = _create_class('Chat', [
           'id', 
           'type', 
           'title', 
           'username', 
           'first_name', 
           'last_name'
       ])

PhotoSize = _create_class('PhotoSize', [
                'file_id', 
                'width', 
                'height', 
                'file_size',
                'file_path',  # undocumented
            ])

Audio = _create_class('Audio', [
            'file_id', 
            'duration', 
            'performer', 
            'title', 
            'mime_type', 
            'file_size'
        ])

Document = _create_class('Document', [
               'file_id', 
               ('thumb', PhotoSize), 
               'file_name', 
               'mime_type', 
               'file_size'
           ])

Sticker = _create_class('Sticker', [
              'file_id', 
              'width', 
              'height', 
              ('thumb', PhotoSize), 
              'file_size'
          ])

Video = _create_class('Video', [
            'file_id', 
            'width', 
            'height', 
            'duration', 
            ('thumb', PhotoSize), 
            'mime_type', 
            'file_size',
            'file_path',  # undocumented
        ])

Voice = _create_class('Voice', [
            'file_id', 
            'duration', 
            'mime_type', 
            'file_size'
        ])

Contact = _create_class('Contact', [
              'phone_number', 
              'first_name', 
              'last_name', 
              'user_id'
          ])

Location = _create_class('Location', [
               'longitude', 
               'latitude'
           ])

File = _create_class('File', [
           'file_id', 
           'file_size', 
           'file_path'
       ])

def PhotoSizeArray(data):
    return [PhotoSize(**p) for p in data]

_classmap['PhotoSize[]'] = PhotoSizeArray

def PhotoSizeArrayArray(data):
    return [[PhotoSize(**p) for p in array] for array in data]

_classmap['PhotoSize[][]'] = PhotoSizeArrayArray

UserProfilePhotos = _create_class('UserProfilePhotos', [
                        'total_count', 
                        ('photos', PhotoSizeArrayArray)
                    ])

ReplyKeyboardMarkup = _create_class('ReplyKeyboardMarkup', [
                          'keyboard',
                          'resize_keyboard',
                          'one_time_keyboard',
                          'selective'
                      ])

ReplyKeyboardHide = _create_class('ReplyKeyboardHide', [
                        ('hide_keyboard', None, True),
                        'selective'
                    ])

ForceReply = _create_class('ForceReply', [
                 ('force_reply', None, True),
                 'selective'
             ])

Message = _create_class('Message', [
              'message_id',
              ('from_', User),
              'date',
              ('chat', Chat),
              ('forward_from', User),
              'forward_date',
              ('reply_to_message', lambda **kwargs: _classmap['Message'](**kwargs)),  # get around the fact that `Message` is not yet defined
              'text',
              ('audio', Audio),
              ('document', Document),
              ('photo', PhotoSizeArray),
              ('sticker', Sticker),
              ('video', Video),
              ('voice', Voice),
              'caption',
              ('contact', Contact),
              ('location', Location),
              ('new_chat_participant', User),
              ('left_chat_participant', User),
              'new_chat_title',
              ('new_chat_photo', PhotoSizeArray),
              'delete_chat_photo',
              'group_chat_created',
              'supergroup_chat_created', 
              'channel_chat_created', 
              'migrate_to_chat_id', 
              'migrate_from_chat_id',
          ])

InlineQuery = _create_class('InlineQuery', [
                  'id', 
                  ('from_', User), 
                  'query', 
                  'offset'
              ])

ChosenInlineResult = _create_class('ChosenInlineResult', [
                         'result_id', 
                         ('from_', User), 
                         'query'
                     ])

Update = _create_class('Update', [
             'update_id', 
             ('message', Message),
             ('inline_query', InlineQuery),
             ('chosen_inline_result', ChosenInlineResult),
         ])

def UpdateArray(data):
    return [Update(**u) for u in data]

_classmap['Update[]'] = UpdateArray

InlineQueryResultArticle = _create_class('InlineQueryResultArticle', [
                               ('type', None, 'article'),
                               'id',
                               'title',
                               'message_text',
                               'parse_mode',
                               'disable_web_page_preview',
                               'url',
                               'hide_url',
                               'description',
                               'thumb_url',
                               'thumb_width',
                               'thumb_height',
                           ])

InlineQueryResultPhoto = _create_class('InlineQueryResultPhoto', [
                             ('type', None, 'photo'),
                             'id',
                             'photo_url',
                             'photo_width',
                             'photo_height',
                             'thumb_url',
                             'title',
                             'description',
                             'caption',
                             'message_text',
                             'parse_mode',
                             'disable_web_page_preview',
                         ])

InlineQueryResultGif = _create_class('InlineQueryResultGif', [
                           ('type', None, 'gif'),
                           'id',
                           'gif_url',
                           'gif_width',
                           'gif_height',
                           'thumb_url',
                           'title',
                           'caption',
                           'message_text',
                           'parse_mode',
                           'disable_web_page_preview',
                       ])

InlineQueryResultMpeg4Gif = _create_class('InlineQueryResultMpeg4Gif', [
                                ('type', None, 'mpeg4_gif'),
                                'id',
                                'mpeg4_url',
                                'mpeg4_width',
                                'mpeg4_height',
                                'thumb_url',
                                'title',
                                'caption',
                                'message_text',
                                'parse_mode',
                                'disable_web_page_preview',
                            ])

InlineQueryResultVideo = _create_class('InlineQueryResultVideo', [
                             ('type', None, 'video'),
                             'id',
                             'video_url',
                             'mime_type',
                             'message_text',
                             'parse_mode',
                             'disable_web_page_preview',
                             'video_width',
                             'video_height',
                             'video_duration',
                             'thumb_url',
                             'title',
                             'description',
                         ])


def namedtuple(data, type):
    if type[-2:] == '[]':
        return _classmap[type](data)
    else:
        return _classmap[type](**data)
