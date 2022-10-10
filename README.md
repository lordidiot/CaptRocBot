# CaptRocBOT

A utility telegram bot for ROC!
Provides some admin features for things around the house.

## Features

Current feature set:
1. Lounge booking management

Future possible features (Make a [PR!](#contributing)):
- Laundry management (Indicate/check in-use)

## Setup

You'll need:
- [python3](https://www.python.org/downloads/)


### 1. Clone repository

```bash
git clone https://github.com/lordidiot/CaptRocBot.git
cd CaptRocBot
```

### 2. Set-up virtual environment

This is not necessary but good practice, learn more [here](https://docs.python.org/3/library/venv.html).

```bash
python3 -m venv env
. env/bin/activate
```

### 3. Install dependencies

```bash
(env) pip install -r requirements.txt
```

### 4. Run the bot!

You'll need to replace `<redacted>` with your own telegram bot api key.
You can get this by following instructions [here](https://core.telegram.org/bots/features#botfather)

```bash
TG_API_KEY=<redacted> python3 bot.py
```

## Contributing

Feel free to contribute with PRs!
Code is quite bad atm, sorry.

Here are some useful resources to get you started if you would like to try contributing:

### Working with Github
- [Creating a pull request from a fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork)

### Working with python-telegram-bot
- [Introduction to the API](https://github.com/python-telegram-bot/v13.x-wiki/wiki/Introduction-to-the-API)
- [Tutorial - Your first bot](https://github.com/python-telegram-bot/v13.x-wiki/wiki/Extensions-%E2%80%93-Your-first-Bot)
- [python-telegram-bot v13.x wiki](https://github.com/python-telegram-bot/v13.x-wiki/wiki)
- [python-telegram-bot v13.13 documentation](https://docs.python-telegram-bot.org/en/v13.13/)