import sys
import asyncio
import telepot
from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import per_chat_id, create_open, pave_event_space

"""
$ python3.6 alarma.py <token>

Send a number which indicates the delay in seconds. The bot will send you an
alarm message after such a delay. It illustrates how to use the built-in
scheduler to schedule custom events for later.

To design a custom event, you first have to invent a *flavor*. To prevent flavors
from colliding with those of Telegram messages, events are given flavors prefixed
with `_` by convention. Then, follow these steps, which are further detailed by
comments in the code:

1. Customize routing table so the correct function gets called on seeing the event
2. Define event-handling function
3. Provide the event spec when scheduling events
"""

class AlarmSetter(telepot.aio.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(AlarmSetter, self).__init__(*args, **kwargs)

        # 1. Customize the routing table:
        #      On seeing an event of flavor `_alarm`, call `self.on__alarm`.
        # To prevent flavors from colliding with those of Telegram messages,
        # events are given flavors prefixed with `_` by convention. Also by
        # convention is that the event-handling function is named `on_`
        # followed by flavor, leading to the double underscore.
        self.router.routing_table['_alarm'] = self.on__alarm

    # 2. Define event-handling function
    async def on__alarm(self, event):
        print(event)  # see what the event object actually looks like
        await self.sender.sendMessage('Beep beep, time to wake up!')

    async def on_chat_message(self, msg):
        try:
            delay = float(msg['text'])

            # 3. Schedule event
            #      The second argument is the event spec: a 2-tuple of (flavor, dict).
            # Put any custom data in the dict. Retrieve them in the event-handling function.
            self.scheduler.event_later(delay, ('_alarm', {'payload': delay}))
            await self.sender.sendMessage('Got it. Alarm is set at %.1f seconds from now.' % delay)
        except ValueError:
            await self.sender.sendMessage('Not a number. No alarm set.')


TOKEN = sys.argv[1]

bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, AlarmSetter, timeout=10),
])

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())
print('Listening ...')

loop.run_forever()
