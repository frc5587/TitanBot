# TitanBot

The Discord bot for Titan Robotics, FRC 5587

This bot has a couple of integrations particular important for our team, namely:

1. Auto-announcements from Google Calendar
2. Polls taken through reactions
3. A powerful equation solver

## Getting Started

First clone this repository `git clone https://github.com/frc5587/TitanBot.git`

Then, from the root of the this repository, install all of the dependencies for this project using the included `requirements.txt` file:

```bash
pip3 install -r requirements.txt
```

Next, delete all the files within `tokens/`, these are our (encrypted) tokens 

And, to start the bot, python >3.5 required (you must first complete the setup process below)

```bash
python3 bot.py
```
Because this bot decrypts the tokens with a bash script called with `./` it is only compatible with linux (without modifying the code). Unless your tokens are not encrypted, then it will work just fine on Windows. If you store it on a public repository you must encrypt the google and discord tokens/credentials because both have web scrapers looking for unencrypted tokens, and they will deactivate your token if they notice the security breach.

One final thing you ar going to want to do is add yourself as a dev to the bot, this will allow you to use any dev based commands like `-die` which ends the bot
1. Create a folder called `cache` in the root of the project
2. Make a file called `devs.txt`
3. Copy your discord user ID into the file, if you want to add anyone else, just add their IDs as well, each one on a new line

Also at anytime you can run `-help` to see a list of commands, and `-help <specific command>` to see any details on that command

## Setting up the Discord Bot

Making the discord bot is pretty simple, you just have to follow these steps.
1. Log onto the [discord developer portal](https://discordapp.com/login?redirect_to=%2Fdevelopers%2Fapplications%2F) with whatever account you want to own the bot
2. Hit `New Application` on the top right corner
    1. Name your app, this does not really matter, only you will see it
    2. Give it an icon and add a description, if you want
    3. On the left sidebar, click `Bot`, then `Add Bot` and confirm it
    4. You can now change the bot's username
    5. Now copy the token, and make a file in `tokens/` called `discord-token.txt`
3. Add the bot to your server
    1. This link `https://discordapp.com/api/oauth2/authorize?client_id=<BOT_ID>&permissions=1342401600&scope=bot` should contain all of the permissions necessary for the bot to work (as we add more features, it may need more)
    2. Replace `<BOT_ID>` with your bot's ID, you can find it in the `General Information` tab in your bot on the discord developer portal, it's under `Client ID`
4. Then have someone with the `Manage Server` permission on your discord server, use the link to add the bot to you sever
    1. Make sure that you allow allow it of the permissions

## Getting Google Credentials

1. Open the [Google Calendar API](https://developers.google.com/calendar/quickstart/python) with the google account that owns the Google Calendar that you want the bot to access
2. Click `Enable the Google Calendar API`
    1. Name the project, and confirm
    2. Download the Client Configuration
    3. Move the the downloaded file (`credentials.json`) to `.tokens/`
    4. Rename the file to `calendar-credentials.json`
    
## Generating Google OAuth

At this point you must run the bot local to your computer to generate the OAuth tokens

1. In `TitanBot/` run `python bot.py`
2. Start a DM with the bot (or just do this on the server it's in)
3. Over discord send `-test` to see if it works, then if it does send `-events`
4. It should open up a page on your web browser for you, but if it doesn't then copy/paste the link printed out in the terminal into your web browser
5. Select the correct google account (if you are logged in to multiple)
6. It will probably say "This app isn't verified" but just ignore that, and click `advanced`, then `Go to <name of API>(unsafe)` (its not actually unsafe, don't worry)
7. Then confirm the next few prompts
8. If it says "The authentication flow has completed, you may close this window." then you succeeded, otherwise just do the steps again
9. You can now send `-die` to the bot, and that will close the bot process so we can move on to the next step, running it over Heroku (optional)
    
## Deploying to Heroku

We have done most of the configuration necessary for deploying to Heroku, we have a Profile and a requirements file.

1. Make a Heroku account, then download the Heroku CLI from [here](https://devcenter.heroku.com/articles/heroku-cli#download-and-install)
2. Follow along with this [guide](https://www.youtube.com/watch?v=BPvg9bndP1U) where needed (we have done most of the setup already)
3. If you don't want to store this bot on a public repository, then you are done (yay!), otherwise keep going through this so we can show you how to encrypt you tokens and credentials
4. Before you upload this to a public repository, run `./scripts/encrypt-tokens.sh all "<password you want to encrypt them with>"`
5. Within `tokens/`, delete all files that don't end in a `.gpg`
6. Now your code is safe to upload to a public repository, so go and do so
7. Next, in the Heroku website, go to your bot, under the `Deploy` tab hit the GiHub button, and add your repository
8. Finally you must configure your config vars
    1. Go to the `Settings` tab and hit `Reveal Config Vars`
    2. In the `KEY` parameter put `TOKEN_DECRYPT_PASS`
    3. In the `VALUE` parameter put the exact same password you used to encrypt the tokens and credentials
9. You should be good, set your bot to run, and bathe in it's majestic glory!


###### If you have any problems with any of these steps you can make an issue on the TitanBot repository or DM Johnny Wobble#1085
