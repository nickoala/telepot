import sys
import time
from pprint import pprint
import telepot
from telepot.namedtuple import StickerSet

TOKEN = sys.argv[1]
USER_ID = long(sys.argv[2])
STICKER_SET = sys.argv[3]

bot = telepot.Bot(TOKEN)

f = bot.uploadStickerFile(USER_ID, open('gandhi.png', 'rb'))
print 'Uploaded Gandhi'

bot.addStickerToSet(USER_ID, STICKER_SET, f['file_id'], u'\U0001f60a')
bot.addStickerToSet(USER_ID, STICKER_SET, open('lincoln.png', 'rb'), u'\U0001f60a')
print 'Added Gandhi and Lincoln to set'

s = bot.getStickerSet(STICKER_SET)
pprint(s)

ss = StickerSet(**s)

for s in ss.stickers:
    bot.deleteStickerFromSet(s.file_id)
    print 'Deleted', s.file_id
    time.sleep(3)  # throttle

s = bot.getStickerSet(STICKER_SET)
pprint(s)
