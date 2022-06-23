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

## How to use
To use the bot you can either create a new version and try yourself or just send a message to @CohereGoodMorningBot. Currently the bot has the commands:
- Start: start the bot
- Get: get a new good morning message by choosing a mood