import sys
import telepot
import telepot.helper
from telepot.delegate import per_chat_id, create_open

class 


TOKEN = sys.argv[1]

bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(, timeout=10))
])
bot.message_loop(run_forever=True)
