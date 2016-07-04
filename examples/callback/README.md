# Callback Query Examples

### A Bot in Love

```
$ python3.5 lover.py <token>   # traditional
$ python3.5 lovera.py <token>  # async
```

1. Send him a message
2. He will ask you to marry him
3. He will keep asking until you say "Yes"

Proposing is a private matter. This bot only works in a private chat.

**[Traditional »](lover.py)**
**[Async »](lovera.py)**

### Referendum Organizer

```
$ python3.5 referendum.py <token>   # traditional
$ python3.5 referenduma.py <token>  # async
```

Add the bot to a group. Then send a command `/vote` to the group. The bot will
organize a referendum.

When all group members have cast a vote or when time expires, it will announce
the result.

**[Traditional »](referendum.py)**
**[Async »](referenduma.py)**

### Date Calculator

```
$ python3.5 datecalc.py <token>   # traditional
$ python3.5 datecalca.py <token>  # async
```

When pondering the date of an appointment or a gathering, we usually think
in terms of "this Saturday" or "next Monday", instead of the actual date.
Yet, for clarity, we eventually want to spell out the actual date to avoid
any chance of misunderstanding. This bot helps you convert weekdays into actual
dates.

1. Go to a private chat or a group chat, perform an inline query by typing
   `@YourBot monday` or any weekday you have in mind.
2. Choose a day from the returned results. In effect, you are proposing that day
   for appointment or gathering. Your friends will have a chance to accept or
   reject your proposal (via an inline keyboard). But the final decision is yours.
3. At the same time, you will receive a private message from the bot asking you
   to make a decision (using a custom keyboard) whether to fix the appointment
   or gathering on that date. You don't have to answer right away.
4. As your friends cast their votes on the proposed date, you will see real-time
   updates of the vote count.
5. When you feel comfortable, use the custom keyboard (sent by the bot in a
   private chat) to make a decision on the date.

**[Traditional »](datecalc.py)**
**[Async »](datecalca.py)**
