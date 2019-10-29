# TitanBot

The Discord bot for Titan Robotics, FRC 5587

This bot has a couple of integrations particular important for our team, namely:

1. Auto-announcements from Google Calendar
2. Polls taken through reactions
3. A simple equation solver

## Getting Started

First, from the base of the this repository, install all of the dependencies for this project using the included `requirements.txt` file:

```bash
pip3 install -r requirements.txt
```

Then, to start the bot, use (python >3.5 required)

```bash
python3 bot.py
```
Because this bot decrypts the tokens with a bash script, that is called with `./` it is only compatible with linux; unless your tokens are 
not encrypted, then it will work fine on Windows.

## Setting up for Heroku

A Procfile is provided if you are deploying to Heroku.

![]
