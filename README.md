# Good-Morning-Bot
Telegram Bot that uses Cohere API to generate good morning messages with different moods.

## How to run
To run the code you need to install the modules by running:
```
pip3 install -r requirements.txt
```

And you need to generate two tokens:
- Cohere API key
- Telegram API key

Then add these tokens to a _.env_ file that should look like:

```
COHERE_API_KEY=YOUR_KEY
TELEGRAM_API_KEY=YOUR_KEY
```

You can also use a Database to store users and messages, and for that you'll also need to add two more things:
- DB_URL
- DB_PASSWORD

## How to use
To use the bot you can either create a new version and try yourself or just send a message to @CohereGoodMorningBot. Currently the bot has the commands:
- Start: start the bot
- Get: get a new good morning message by choosing a mood
- Subscribe: get daily messages
- Unsubscribe: stop receiving daily messages

## Versions:
1. Few-shot with hard-coded examples for some of the categories
2. Few-shot with hard-coded examples for all of the categories
3. Few-shot using previously generated messages
4. Few-shot using previously generated messages for each individual tone
5. Few-shot with feedback from the user
6. [To Do] Fine tune a model
