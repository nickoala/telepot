# Simple Examples

### [Dicey Clock](diceyclock.py)

After **inserting token** in the source code, run it:

```
$ python2.7 diceyclock.py
```

[Here is a tutorial](http://www.instructables.com/id/Set-up-Telegram-Bot-on-Raspberry-Pi/)
teaching you how to setup a bot on Raspberry Pi. This simple bot does nothing
but accepts two commands:

- `/roll` - reply with a random integer between 1 and 6, like rolling a dice.
- `/time` - reply with the current time, like a clock.

### Emodi - an Emoji Unicode Decoder

You send it some emoji, it tells you the unicodes.

**[Traditional version »](emodi.py)**   

But if you really want to put emoji in a string, I recommend using this
**[emoji](https://pypi.python.org/pypi/emoji/)** package.

### Simple Skeleton

```
$ python2.7 skeleton.py <token>   # traditional
$ python3.5 skeletona.py <token>  # async
```

**[Traditional »](skeleton.py)**   
**[Async »](skeletona.py)**  

### Various keyboards and buttons

```
$ python3.5 skeleton_route.py <token>   # traditional
$ python3.5 skeletona_route.py <token>  # async
```

It demonstrates:

- passing a routing table to `MessageLoop` to filter flavors.
- the use of custom keyboard and inline keyboard, and their various buttons.

Remember to `/setinline` and `/setinlinefeedback` to enable inline mode for your bot.

It works like this:

- First, you send it one of these 4 characters - `c`, `i`, `h`, `f` - and it replies accordingly:
    - `c` - a custom keyboard with various buttons
    - `i` - an inline keyboard with various buttons
    - `h` - hide custom keyboard
    - `f` - force reply
- Press various buttons to see their effects
- Within inline mode, what you get back depends on the **last character** of the query:
    - `a` - a list of articles
    - `p` - a list of photos
    - `b` - to see a button above the inline results to switch back to a private chat with the bot

**[Traditional »](skeleton_route.py)**   
**[Async »](skeletona_route.py)**  
