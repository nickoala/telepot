import time
import asyncio
import telepot.aio

def handle(msg):
    print(msg)

bot = telepot.aio.Bot('abc')
qu = asyncio.Queue();

def u(update_id):
    return { 'update_id': update_id, 'message': update_id }

sequence = [
    u(1),  # initialize
    u(2),  # no buffering

    u(4),  # 1-gap
    u(3),  # clear 2

    u(7),  # 2-gap
    u(5),  # return, leave 1-gap
    u(6),  # clear 2

    u(10),  # 2-gap
    u(9),   # 1-gap
    u(8),   # clear 3

    u(15),
    u(12),
    u(13),
    u(11),
    u(14),

    u(17),
    u(18),
    u(21),
    u(20),
    u(19),
    u(16),

    u(22),  # no buffering

    u(24),
    9,  # skip id=23

    u(23),  # discard

    u(26),
    u(27),
    9,  # skip id=25

    u(25),  # discard

    u(30),
    u(29),
    5,
    u(32),
    u(33),
    2,  # clear 29,30, skip 28
    u(31),  # clear 31,32,33

    u(39),
    u(36),
    2,
    u(37),
    7,  # clear 36,37,39

    u(28),  # discard
    u(38),  # discard

    u(40),  # return
]

async def queue_put():
    for update in sequence:
        if type(update) is dict:
            await qu.put(update)
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(update)


loop = asyncio.get_event_loop()
loop.create_task(bot.message_loop(handle, source=qu, maxhold=8))
loop.create_task(queue_put())
loop.run_forever()
