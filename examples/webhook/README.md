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
for you. It is called `OrderedWebhook`.

```python
from telepot.loop import OrderedWebhook

def handle(msg):
    # ......

bot = telepot.Bot(TOKEN)
webhook = OrderedWebhook(bot, handle)

webhook.run_as_thread()
```

The web application, upon receiving a POST request, feeds data into the webhook
object. It will re-order the updates if necessary.
Using [Flask](http://flask.pocoo.org/) as the web application framework:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook_path', methods=['GET', 'POST'])
def pass_update():
    webhook.feed(request.data)
    return 'OK'
```
