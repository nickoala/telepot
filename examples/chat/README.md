# Chat Examples

### Message Counter

Counts number of messages a user has sent. Starts over if silent for 10 seconds.
Illustrates the basic usage of `DelegateBot` and `ChatHandler`.

**[Traditional »](counter.py)**  
**[Async »](countera.py)**

### Guess a number

1. Send the bot anything to start a game.
2. The bot randomly picks an integer between 0-99.
3. You make a guess.
4. The bot tells you to go higher or lower.
5. Repeat step 3 and 4, until guess is correct.

**[Traditional »](guess.py)**  
**[Async »](guessa.py)**

### Chatbox - a Mailbox for Chats

1. People send messages to your bot.
2. Your bot remembers the messages.
3. You read the messages later.

It accepts the following commands from you, the owner, only:

- `/unread` - tells you who has sent you messages and how many
- `/next` - read next sender's messages

This example can be a starting point for **customer support** type of bots.
For example, customers send questions to a bot account; staff answers questions
behind the scene, makes it look like the bot is answering questions.

It further illustrates the use of `DelegateBot` and `ChatHandler`, and how to
spawn delegates differently according to the role of users.

This example only handles text messages and stores messages in memory.
If the bot is killed, all messages are lost. It is an *example* after all.

**[Traditional »](chatbox_nodb.py)**  
**[Async »](chatboxa_nodb.py)**
