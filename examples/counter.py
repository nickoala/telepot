import sys
import telepot
from telepot.delegate import create_run

"""
$ python2.7 count.py <token>

Count number of messages. Start over if silent for 10 seconds.
"""

# Being a subclass of ChatHandler is very useful, for it gives you:
# listener, sender, etc - a lot of facilities.
class MessageCounter(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple):
        super(MessageCounter, self).__init__(*seed_tuple)
        self.listener.timeout = 10
        # conversation ends if no more messages after 10 seconds

    def run(self):
        count = 1
        self.sender.sendMessage(count)
        # `sender` lets you send messages without mentioning chat_id every time

        while 1:
            # wait for user's next message
            msg = self.listener.wait(chat__id=self.chat_id)
            count += 1
            self.sender.sendMessage(count)


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.DelegatorBot(TOKEN, [
    # For each chat id, create a MessageCounter and delegate to its `run()` method
    (lambda msg: msg['chat']['id'], create_run(MessageCounter)),
])
bot.notifyOnMessage(run_forever=True)
