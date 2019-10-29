# TitanBot

The Discord bot for Titan Robotics, FRC 5587

This bot has a couple of integrations particular important for our team, namely:

1. Auto-announcements from Google Calendar
2. Polls taken through reactions
3. A powerful equation solver

## Getting Started

First, from the base of the this repository, install all of the dependencies for this project using the included `requirements.txt` file:

```bash
pip3 install -r requirements.txt
```

Then, to start the bot, use (python >3.5 required)

```bash
python3 bot.py
```
Because this bot decrypts the tokens with a bash script called with `./` it is only compatible with linux (without modifying the code). Unless your tokens are not encrypted, then it will work just fine on Windows. If you store it on a public repository you must encrypt the google and discord tokens/credentials because both have web scrapers looking for unencrypted tokens, and they will deactivate your token if they notice the security breach.

## Setting up Discord Bot

Making a discord bot is pretty simple, you just have to follow these steps.
1. Log onto the [discord developer portal](https://discordapp.com/login?redirect_to=%2Fdevelopers%2Fapplications%2F) with whatever account you want to own the bot
2. Hit `new application` on the top right corner
  A. asdfsadf
  B. adfasdf

## Deploying to Heroku

We have done most of the configuration necessary for deploying to Heroku, we have a Profile and a requirements file. Unless you know how to use Heroku and the Heroku CLI, we suggest this [guide](https://www.youtube.com/watch?v=BPvg9bndP1U).

Once you have your account set



A Procfile is provided if you are deploying to Heroku.

![]
