## Migration Guide to telepot 7.0

Prior to 7.0, telepot's method naming has taken on two styles:

- CamelCase, e.g. `sendMessage`, `getUpdates`, `notifyOnMessage`, `messageLoop`
- underscore_separated, e.g. `on_chat_message`, `on_inline_query`, `set_routing_table`

Rationale behind this inconsistency has not been clear.

From 7.0 on, mixing of two styles remains, but I have decided on a clear boundary:

- CamelCase is reserved for methods that strictly wrap the identically-named methods on Bot API
    - e.g. `sendMessage`, `getUpdates`
- All other methods are underscore_separated:
    - e.g. `message_loop`, `download_file`, `on_chat_message`

This separation makes it clear where to look for information. I don't believe telepot has to hide the Bot API. There is no substitute for understanding the Bot API itself.

I am also taking this opportunity to reverse some not-so-good decisions. They are not huge changes, but I apologise for any inconvenience. Without further ado, here are what you need to do to move to telepot 7.0:

1. Flavor `normal` becomes `chat`  
    What to do :scream: : Search for the string `normal`, then replace with the string `chat`

2. Method `notifyOnMessage` becomes `message_loop`  
    :scream: What to do: Search for the method `notifyOnMessage`, then change the method name to `message_loop`

3. Method `messageLoop` becomes `message_loop`  
    What to do :scream: : Search for the method `messageLoop`, then change the method name to `message_loop`

4. Method `downloadFile` becomes `download_file`  
    :scream: What to do: Search for the method `downloadFile`, then change the method name to `download_file`

5. Function `telepot.namedtuple.namedtuple` was removed. Create namedtuples using their constructors directly, by unpacking a dict into keyword arguments.  
    What to do :scream: : Where you did this before:

    ```python
    import telepot.namedtuple

    obj = telepot.namedtuple.namedtuple(msg, 'Message')
    ```

    You do this now:

    ```python
    import telepot.namedtuple

    obj = telepot.namedtuple.Message(**msg)
    ```

6. Function `telepot.glance2` was removed. Use `telepot.glance`.  
    :scream: What to do: Search for the function `glance2`, then change the function name to `glance`

7. Content type `new_chat_participant` becomes `new_chat_member`  
    What to do :scream: : Search for the string `new_chat_participant`, then replace with the string `new_chat_member`

8. Content type `left_chat_participant` becomes `left_chat_member`  
    :scream: What to do: Search for the string `left_chat_participant`, then replace with the string `left_chat_member`

Note: (7) and (8) are actually dictated by Bot API 2.0, not telepot.

I apologise again. Good luck. Thanks for using telepot.
