import sys
import asyncio
from pprint import pprint
import telepot.aio
from telepot.namedtuple import StickerSet

async def test_sticker():
    f = await bot.uploadStickerFile(USER_ID, open('gandhi.png', 'rb'))
    print('Uploaded Gandhi')

    await bot.addStickerToSet(USER_ID, STICKER_SET, f['file_id'], '\U0001f60a')
    await bot.addStickerToSet(USER_ID, STICKER_SET, open('lincoln.png', 'rb'), '\U0001f60a')
    print('Added Gandhi and Lincoln to set')

    s = await bot.getStickerSet(STICKER_SET)
    pprint(s)

    ss = StickerSet(**s)

    for s in ss.stickers:
        await bot.deleteStickerFromSet(s.file_id)
        print('Deleted', s.file_id)
        await asyncio.sleep(3)  # throttle

    s = await bot.getStickerSet(STICKER_SET)
    pprint(s)

TOKEN = sys.argv[1]
USER_ID = int(sys.argv[2])
STICKER_SET = sys.argv[3]

bot = telepot.aio.Bot(TOKEN)
loop = asyncio.get_event_loop()

loop.run_until_complete(test_sticker())
