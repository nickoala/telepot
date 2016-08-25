# Callback Query Examples

### A Bot in Love

1. Send him a message
2. He will ask you to marry him
3. He will keep asking until you say "Yes"

If you are silent for 10 seconds, he will go away a little bit, but is still
there waiting for you. What a sweet bot!

It statically captures callback query according to the originating chat id.
This is the chat-centric approach.

Proposing is a private matter. This bot only works in a private chat.

**[Traditional »](lover.py)**  
**[Async »](lovera.py)**

### Vote Counter

Add the bot to a group. Then send a command `/vote` to the group. The bot will
organize a ballot.

When all group members have cast a vote or when time expires (30 seconds),
it will announce the result. It demonstrates how to use the scheduler to
generate an expiry event after a certain delay.

It statically captures callback query according to the originating chat id.
This is the chat-centric approach.

**[Traditional »](vote.py)**  
**[Async »](votea.py)**

### Quiz Bot

Send a chat message to the bot. It will give you a math quiz. Stay silent for
10 seconds to end the quiz.

It handles callback query by their origins. All callback query originated from
the same chat message will be handled by one `CallbackQueryOriginHandler`.

**[Traditional »](quiz.py)**  
**[Async »](quiza.py)**

### Date Calculator

When pondering the date of an appointment or a gathering, we usually think
in terms of "this Saturday" or "next Monday", instead of the actual date.
This *inline* bot helps you convert weekdays into actual dates.

1. Go to a group chat. The bot does not need to be a group member. You are
   going to inline-query it.

2. Type `@YourBot monday` or any weekday you have in mind. It will suggest a
   few dates based on it.

3. Choose a day from the returned results. The idea is to propose a date to
   the group. Group members have 30 seconds to vote on the proposed date.

4. After 30 seconds, the voting result is announced.

This example dynamically maps callback query back to their originating
`InlineUserHandler`, so you can do question-asking (sending a message containing
an inline keyboard) and answer-gathering (receiving callback query) in the same
object.

**[Traditional »](datecalc.py)**  
**[Async »](datecalca.py)**
