import collections
import warnings
import sys

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
                if oldkey in kwargs:
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

    return sub

"""
Different treatments for incoming and outgoing namedtuples:

- Incoming ones require type declarations for certain fields for deeper parsing.
- Outgoing ones need no such declarations because users are expected to put the correct object in place.
"""

# incoming
User = _create_class('User', [
           'id',
           'first_name',
           'last_name',
           'username'
       ])

# incoming
Chat = _create_class('Chat', [
           'id',
           'type',
           'title',
           'username',
           'first_name',
           'last_name',
           'all_members_are_administrators',
       ])

# incoming
PhotoSize = _create_class('PhotoSize', [
                'file_id',
                'width',
                'height',
                'file_size',
                'file_path',  # undocumented
            ])

# incoming
Audio = _create_class('Audio', [
            'file_id',
            'duration',
            'performer',
            'title',
            'mime_type',
            'file_size'
        ])

# incoming
Document = _create_class('Document', [
               'file_id',
               ('thumb', PhotoSize),
               'file_name',
               'mime_type',
               'file_size',
               'file_path',  # undocumented
           ])

# incoming
Sticker = _create_class('Sticker', [
              'file_id',
              'width',
              'height',
              ('thumb', PhotoSize),
              'emoji',
              'file_size',
          ])

# incoming
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

# incoming
Voice = _create_class('Voice', [
            'file_id',
            'duration',
            'mime_type',
            'file_size'
        ])

# incoming
Contact = _create_class('Contact', [
              'phone_number',
              'first_name',
              'last_name',
              'user_id'
          ])

# incoming
Location = _create_class('Location', [
               'longitude',
               'latitude'
           ])

# incoming
Venue = _create_class('Venue', [
            ('location', Location),
            'title',
            'address',
            'foursquare_id',
        ])

# incoming
File = _create_class('File', [
           'file_id',
           'file_size',
           'file_path'
       ])

def PhotoSizeArray(data):
    return [PhotoSize(**p) for p in data]

def PhotoSizeArrayArray(data):
    return [[PhotoSize(**p) for p in array] for array in data]

# incoming
UserProfilePhotos = _create_class('UserProfilePhotos', [
                        'total_count',
                        ('photos', PhotoSizeArrayArray)
                    ])

# incoming
ChatMember = _create_class('ChatMember', [
                 ('user', User),
                 'status',
             ])

def ChatMemberArray(data):
    return [ChatMember(**p) for p in data]

# outgoing
ReplyKeyboardMarkup = _create_class('ReplyKeyboardMarkup', [
                          'keyboard',
                          'resize_keyboard',
                          'one_time_keyboard',
                          'selective',
                      ])

# outgoing
KeyboardButton = _create_class('KeyboardButton', [
                     'text',
                     'request_contact',
                     'request_location',
                 ])

# outgoing
ReplyKeyboardRemove = _create_class('ReplyKeyboardRemove', [
                          ('remove_keyboard', None, True),
                          'selective',
                      ])

# outgoing
ForceReply = _create_class('ForceReply', [
                 ('force_reply', None, True),
                 'selective',
             ])

# outgoing
InlineKeyboardButton = _create_class('InlineKeyboardButton', [
                           'text',
                           'url',
                           'callback_data',
                           'switch_inline_query',
                           'switch_inline_query_current_chat',
                           'callback_game',
                       ])

# outgoing
InlineKeyboardMarkup = _create_class('InlineKeyboardMarkup', [
                           'inline_keyboard',
                       ])

# incoming
MessageEntity = _create_class('MessageEntity', [
                    'type',
                    'offset',
                    'length',
                    'url',
                    ('user', User),
                ])

# incoming
def MessageEntityArray(data):
    return [MessageEntity(**p) for p in data]

# incoming
GameHighScore = _create_class('GameHighScore', [
                    'position',
                    ('user', User),
                    'score',
                ])

# incoming
Animation = _create_class('Animation', [
                'file_id',
                ('thumb', PhotoSize),
                'file_name',
                'mime_type',
                'file_size',
            ])

# incoming
Game = _create_class('Game', [
           'title',
           'description',
           ('photo', PhotoSizeArray),
           'text',
           ('text_entities', MessageEntityArray),
           ('animation', Animation),
       ])

# incoming
Message = _create_class('Message', [
              'message_id',
              ('from_', User),
              'date',
              ('chat', Chat),
              ('forward_from', User),
              ('forward_from_chat', Chat),
              'forward_from_message_id',
              'forward_date',                     # get around the fact that `Message` is not yet defined
              ('reply_to_message', lambda **kwargs: getattr(sys.modules[__name__], 'Message')(**kwargs)),
              'edit_date',
              'text',
              ('entities', MessageEntityArray),
              ('audio', Audio),
              ('document', Document),
              ('game', Game),
              ('photo', PhotoSizeArray),
              ('sticker', Sticker),
              ('video', Video),
              ('voice', Voice),
              'caption',
              ('contact', Contact),
              ('location', Location),
              ('venue', Venue),
              ('new_chat_member', User),
              ('left_chat_member', User),
              'new_chat_title',
              ('new_chat_photo', PhotoSizeArray),
              'delete_chat_photo',
              'group_chat_created',
              'supergroup_chat_created',
              'channel_chat_created',
              'migrate_to_chat_id',
              'migrate_from_chat_id',
              ('pinned_message', lambda **kwargs: getattr(sys.modules[__name__], 'Message')(**kwargs)),
          ])

# incoming
InlineQuery = _create_class('InlineQuery', [
                  'id',
                  ('from_', User),
                  ('location', Location),
                  'query',
                  'offset',
              ])

# incoming
ChosenInlineResult = _create_class('ChosenInlineResult', [
                         'result_id',
                         ('from_', User),
                         ('location', Location),
                         'inline_message_id',
                         'query',
                     ])

# incoming
CallbackQuery = _create_class('CallbackQuery', [
                    'id',
                    ('from_', User),
                    ('message', Message),
                    'inline_message_id',
                    'chat_instance',
                    'data',
                    'game_short_name',
                ])

# incoming
Update = _create_class('Update', [
             'update_id',
             ('message', Message),
             ('edited_message', Message),
             ('channel_post', Message),
             ('edited_channel_post', Message),
             ('inline_query', InlineQuery),
             ('chosen_inline_result', ChosenInlineResult),
             ('callback_query', CallbackQuery),
         ])

# incoming
def UpdateArray(data):
    return [Update(**u) for u in data]

# incoming
WebhookInfo = _create_class('WebhookInfo', [
                  'url',
                  'has_custom_certificate',
                  'pending_update_count',
                  'last_error_date',
                  'last_error_message',
              ])

# outgoing
InputTextMessageContent = _create_class('InputTextMessageContent', [
                              'message_text',
                              'parse_mode',
                              'disable_web_page_preview',
                          ])

# outgoing
InputLocationMessageContent = _create_class('InputLocationMessageContent', [
                                  'latitude',
                                  'longitude',
                              ])

# outgoing
InputVenueMessageContent = _create_class('InputVenueMessageContent', [
                               'latitude',
                               'longitude',
                               'title',
                               'address',
                               'foursquare_id',
                           ])

# outgoing
InputContactMessageContent = _create_class('InputContactMessageContent', [
                                 'phone_number',
                                 'first_name',
                                 'last_name',
                             ])

# outgoing
InlineQueryResultArticle = _create_class('InlineQueryResultArticle', [
                               ('type', None, 'article'),
                               'id',
                               'title',
                               'input_message_content',
                               'reply_markup',
                               'url',
                               'hide_url',
                               'description',
                               'thumb_url',
                               'thumb_width',
                               'thumb_height',
                           ])

# outgoing
InlineQueryResultPhoto = _create_class('InlineQueryResultPhoto', [
                             ('type', None, 'photo'),
                             'id',
                             'photo_url',
                             'thumb_url',
                             'photo_width',
                             'photo_height',
                             'title',
                             'description',
                             'caption',
                             'reply_markup',
                             'input_message_content',
                         ])

# outgoing
InlineQueryResultGif = _create_class('InlineQueryResultGif', [
                           ('type', None, 'gif'),
                           'id',
                           'gif_url',
                           'gif_width',
                           'gif_height',
                           'thumb_url',
                           'title',
                           'caption',
                           'reply_markup',
                           'input_message_content',
                       ])

# outgoing
InlineQueryResultMpeg4Gif = _create_class('InlineQueryResultMpeg4Gif', [
                                ('type', None, 'mpeg4_gif'),
                                'id',
                                'mpeg4_url',
                                'mpeg4_width',
                                'mpeg4_height',
                                'thumb_url',
                                'title',
                                'caption',
                                'reply_markup',
                                'input_message_content',
                            ])

# outgoing
InlineQueryResultVideo = _create_class('InlineQueryResultVideo', [
                             ('type', None, 'video'),
                             'id',
                             'video_url',
                             'mime_type',
                             'thumb_url',
                             'title',
                             'caption',
                             'video_width',
                             'video_height',
                             'video_duration',
                             'description',
                             'reply_markup',
                             'input_message_content',
                         ])

# outgoing
InlineQueryResultAudio = _create_class('InlineQueryResultAudio', [
                             ('type', None, 'audio'),
                             'id',
                             'audio_url',
                             'title',
                             'caption',
                             'performer',
                             'audio_duration',
                             'reply_markup',
                             'input_message_content',
                         ])

# outgoing
InlineQueryResultVoice = _create_class('InlineQueryResultVoice', [
                             ('type', None, 'voice'),
                             'id',
                             'voice_url',
                             'title',
                             'caption',
                             'voice_duration',
                             'reply_markup',
                             'input_message_content',
                         ])

# outgoing
InlineQueryResultDocument = _create_class('InlineQueryResultDocument', [
                                ('type', None, 'document'),
                                'id',
                                'title',
                                'caption',
                                'document_url',
                                'mime_type',
                                'description',
                                'reply_markup',
                                'input_message_content',
                                'thumb_url',
                                'thumb_width',
                                'thumb_height',
                            ])

# outgoing
InlineQueryResultLocation = _create_class('InlineQueryResultLocation', [
                                ('type', None, 'location'),
                                'id',
                                'latitude',
                                'longitude',
                                'title',
                                'reply_markup',
                                'input_message_content',
                                'thumb_url',
                                'thumb_width',
                                'thumb_height',
                            ])

# outgoing
InlineQueryResultVenue = _create_class('InlineQueryResultVenue', [
                                ('type', None, 'venue'),
                                'id',
                                'latitude',
                                'longitude',
                                'title',
                                'address',
                                'foursquare_id',
                                'reply_markup',
                                'input_message_content',
                                'thumb_url',
                                'thumb_width',
                                'thumb_height',
                         ])

# outgoing
InlineQueryResultContact = _create_class('InlineQueryResultContact', [
                                ('type', None, 'contact'),
                                'id',
                                'phone_number',
                                'first_name',
                                'last_name',
                                'reply_markup',
                                'input_message_content',
                                'thumb_url',
                                'thumb_width',
                                'thumb_height',
                           ])

# outgoing
InlineQueryResultGame = _create_class('InlineQueryResultGame', [
                            ('type', None, 'game'),
                            'id',
                            'game_short_name',
                            'reply_markup',
                        ])

# outgoing
InlineQueryResultCachedPhoto = _create_class('InlineQueryResultCachedPhoto', [
                                   ('type', None, 'photo'),
                                   'id',
                                   'photo_file_id',
                                   'title',
                                   'description',
                                   'caption',
                                   'reply_markup',
                                   'input_message_content',
                               ])

# outgoing
InlineQueryResultCachedGif = _create_class('InlineQueryResultCachedGif', [
                                 ('type', None, 'gif'),
                                 'id',
                                 'gif_file_id',
                                 'title',
                                 'caption',
                                 'reply_markup',
                                 'input_message_content',
                             ])

# outgoing
InlineQueryResultCachedMpeg4Gif = _create_class('InlineQueryResultCachedMpeg4Gif', [
                                      ('type', None, 'mpeg4_gif'),
                                      'id',
                                      'mpeg4_file_id',
                                      'title',
                                      'caption',
                                      'reply_markup',
                                      'input_message_content',
                                  ])

# outgoing
InlineQueryResultCachedSticker = _create_class('InlineQueryResultCachedSticker', [
                                     ('type', None, 'sticker'),
                                     'id',
                                     'sticker_file_id',
                                     'reply_markup',
                                     'input_message_content',
                                 ])

# outgoing
InlineQueryResultCachedDocument = _create_class('InlineQueryResultCachedDocument', [
                                      ('type', None, 'document'),
                                      'id',
                                      'title',
                                      'document_file_id',
                                      'description',
                                      'caption',
                                      'reply_markup',
                                      'input_message_content',
                                  ])

# outgoing
InlineQueryResultCachedVideo = _create_class('InlineQueryResultCachedVideo', [
                                   ('type', None, 'video'),
                                   'id',
                                   'video_file_id',
                                   'title',
                                   'description',
                                   'caption',
                                   'reply_markup',
                                   'input_message_content',
                               ])

# outgoing
InlineQueryResultCachedVoice = _create_class('InlineQueryResultCachedVoice', [
                                   ('type', None, 'voice'),
                                   'id',
                                   'voice_file_id',
                                   'title',
                                   'caption',
                                   'reply_markup',
                                   'input_message_content',
                               ])

# outgoing
InlineQueryResultCachedAudio = _create_class('InlineQueryResultCachedAudio', [
                                   ('type', None, 'audio'),
                                   'id',
                                   'audio_file_id',
                                   'caption',
                                   'reply_markup',
                                   'input_message_content',
                               ])
