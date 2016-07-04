# Webhook Examples

Traditional version using **[Flask](http://flask.pocoo.org/)** as web server:

```
$ python2.7 flask_skeleton.py <token> <listening_port> https://<domain>/abc
$ python3.5 flask_counter.py <token> <listening_port> https://<domain>/abc
```

Async version using **[aiohttp](http://aiohttp.readthedocs.org/en/stable/)** as web server:

```
$ python3.5 aiohttp_skeletona.py <token> <listening_port> https://<domain>/abc
$ python3.5 aiohttp_countera.py <token> <listening_port> https://<domain>/abc
```

Remember you will have to set up the **webhook URL, SSL certificate, and web server** on your own.

## Telepot's Webhook Interface

Setting up a **[webhook](https://core.telegram.org/bots/api#setwebhook)** is
more complicated than using `getUpdates()` because:

1. You have to obtain an URL
2. You have to obtain and set up an SSL certificate for the URL
3. You have to set up a web server to handle the POST requests coming from Telegram servers

Webhook also presents a subtle problem: closely bunched updates may arrive out of order.
That is, update_id `1000` may arrive ahead of update_id `999`, if the two are issued by
Telegram servers very closely. Unless a bot absolutely doesn't care about update order,
it will have to re-order them in some way.

Telepot has a mechanism to interface with web applications, and it takes care of re-ordering
for you. The mechanism is simple: you call `message_loop()` as usual, but supply an additional
parameter `source`, which is a queue.

```python
# for Python 2 and 3
try:
    from Queue import Queue
except ImportError:
    from queue import Queue

def handle(msg):
    # ......

bot = telepot.Bot(TOKEN)
update_queue = Queue()

# get updates from queue, not from Telegram servers
bot.message_loop(handle, source=update_queue)
```

The web application, upon receiving a POST request, dumps data into the queue
for the bot to retrieve at the other end. The bot will re-order the updates if necessary.
Using [Flask](http://flask.pocoo.org/) as the web application framework:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook_path', methods=['GET', 'POST'])
def pass_update():
    update_queue.put(request.data)  # dump data to queue
    return 'OK'
```
