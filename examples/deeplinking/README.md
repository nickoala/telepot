# Deep Linking Examples

```
$ python2.7 flask_deeplinking.py <bot_username> <token> <listening_port> https://<domain>/abc
```

1. Open browser, visit: `https://<domain>/link`
2. Click on the link
3. On Telegram conversation, click on the `START` button
4. Bot should receive a message `/start ghijk`, where `ghijk` is the payload embedded in the link.
   You may use this payload to identify the user, then his Telegram `chat_id`.

## Deep Linking Explanation

Telegram's introduction to [deep linking](https://core.telegram.org/bots#deep-linking)
may be a bit confusing. I try to give a clearer explanation here.

1. You have a database of users. Each user has an ID. Suppose you want your Telegram bot
   to communicate with user `123`, but you don't know his Telegram `chat_id`
   (which the bot needs in order to send messages to him).
   How do you "entice" him to talk to the bot, thus revealing his `chat_id`?
   You put a link on a web page.

2. But the link has to be "personalized". You want each user to press on a slightly
   different link in order to distinguish them. One way to do that is to embed user ID
   in the link. However, user IDs are *not* something you want to expose, so you generate
   a (temporary) *key* associated with a user ID, and *embed that key in the link*.
   If user `123` has the key `abcde`, his personalized link will be:

    ```
    https://telegram.me/<bot_username>?start=abcde
    ```

3. Someone clicks on the link, and is led to a conversation with your bot.
   When he presses the `START` button, your bot will receive a message:

    ```
    /start abcde
    ```

4. On receiving that message, the bot sees that `abcde` is associated with user `123`.
   Telegram `chat_id` can also be extracted from the message.
   Knowing user `123`'s `chat_id`, the bot can send him messages afterwards.

Telegram's introduction refers often to "Memcache", by which they only mean a datastore
that remembers key-user ID associations. In a simple experiment, a dictionary will do.
In real world, you may use Memcached (the memory caching software) or a database table.
