# TitanBot

The Discord bot for Titan Robotics, FRC 5587

This bot has a couple of integrations particularly important for our team, namely:

1. Auto-announcements from Google Calendar
2. Polls taken through reactions
3. A powerful equation solver

## Getting Started


1. Install [Python and pip](https://www.makeuseof.com/tag/install-pip-for-python/) and clone this repository

2. Then, from the root of the this repository, install all of the dependencies for this project using the included `requirements.txt` file:
    ```bash
    pip3 install -r requirements.txt
    ```

3. Next, delete all the files within `tokens/` and replace them with all of the appropriate tokens, as detailed in the [Getting Credentials Set Up Section](#Getting-Credentials-Set-Up)

4. Finally, to start the bot:

    ```bash
    python3 bot.py
    ```

One thing you are probably going to want to do is add yourself as a dev to the bot. This will allow you to use any dev-based commands like `-die`, which ends the bot. To do this, simply...

In `config.json` replace our discord IDs with your own and anyone else's who you want to have dev permissions

Also, at any time, you can run `-help` to see a list of commands, and `-help <specific command>` to see any details on that command

## Getting Credentials Set Up

### Discord Token

Making the discord bot is pretty simple, you just have to follow these steps.

1. Log onto the [Discord Developer Portal](https://discordapp.com/login?redirect_to=%2Fdevelopers%2Fapplications%2F) with whatever account you want to own the bot
2. Hit "New Application" on the top right corner
    1. Name your app, this does not really matter, only you will see it
    2. On the left sidebar, click `Bot`, then `Add Bot` and confirm it
    3. You can now change the bot's username
    4. Now copy the token, and make a file in `tokens/` called `discord-token.txt`
3. Add the bot to your server
    1. Find your bot's ID in the Discord Developer portal, found under "Client ID"
    2. Go to the following link in your web browser, with `<BOT_ID>` replaced with your bot's ID. This link should contain all of the permissions necessary for the bot to work.

    ```plaintext
    https://discordapp.com/api/oauth2/authorize?client_id=<BOT_ID>&permissions=1342401600&scope=bot
    ```

4. Then have someone with the `Manage Server` permission on your Discord server use the link to add the bot to your sever
    * Make sure that you allow it all of the permissions

### Google Credentials

1. Open the [Google Calendar API](https://developers.google.com/calendar/quickstart/python) with the Google account that owns the Google Calendar that you want the bot to access
2. Click `Enable the Google Calendar API`
    1. Name the project, and confirm
    2. Download the Client Configuration
    3. Move the the downloaded file (`credentials.json`) to `.tokens/`
    4. Rename the file to `calendar-credentials.json`

### Generating Google OAuth

At this point you must run the bot local to your computer to generate the OAuth tokens

1. With the bot running, send `-test` either in a DM or a server with the bot and confirm that it sends a response. If it does, send `-events`. Otherwise, ensure that the bot is running and try again
2. It should open up a page on your web browser for you, but if it doesn't simply copy/paste the link printed in the terminal into your web browser
3. Select the correct Google account (if you are logged in to multiple)
4. It will probably say "This app isn't verified" but just ignore that, and click `advanced`, then `Go to <name of API>(unsafe)` (its not actually unsafe, don't worry)
5. Confirm the next couple of prompts
6. If it says "The authentication flow has completed, you may close this window." then you succeeded, otherwise just restart the bot and do the steps again

## Securely Storing Tokens

If you are publicly posting or hosting the code for this bot, you don't want to publish your unencrypted credentials and tokens. Both Google and Discord have web scrapers looking for unencrypted tokens, and they will deactivate your token if they notice the security breach, plus it's also just dumb.

To address this, you can encrypt your credentials and tokens with `gpg` and store them in your code. If you want to use this feature, read the following guide, but note that support for this feature is currently limited to Linux environments.

1. Install [gpg](http://blog.ghostinthemachines.com/2015/03/01/how-to-use-gpg-command-line/) on your computer
2. Place your unencrypted credentials in the `credentials/` directory if you have not done so already (see [Getting Credentials Set Up Section](#Getting-Credentials-Set-Up) for more information)
3. From the root of this repository, run

    ```bash
    ./scripts/encrypt-tokens.sh all "<password you want to encrypt them with>"
    ```

4. To be safe, delete all the files in `tokens/` that don't end in a `.gpg`

From here, you can push your code to your SCM.

## Deploying to Heroku

For a detailed setup guide as to hosting the bot with Heroku (which our team does), see below. Note that a Profile and a `requirements.txt` file are already included in this repository.

1. Put all of your code with credentials and tokens in a GitHub repository. If the repository is public, make sure you have followed the [Securely Storing Tokens](##Securely-Storing-Tokens) section!
2. Make a Heroku account, then download the Heroku CLI from [here](https://devcenter.heroku.com/articles/heroku-cli#download-and-install)
3. Follow along with [this guide](https://www.youtube.com/watch?v=BPvg9bndP1U) where needed (again, a Procfile and `requiremements.txt` are already included, so most of the setup is already done for you)

If you didn't store this bot in a public repository, then you are done (yay!). However, if your code is in a public repository, keep going through to set up the decryption of tokens and credentials:

4. In the Heroku website, go to your bot, under the `Deploy` tab hit the GiHub button, and add your repository
5. Finally, configure your config variables
    1. Go to the `Settings` tab and hit `Reveal Config Vars`
    2. In the `KEY` parameter put `TOKEN_DECRYPT_PASS`
    3. In the `VALUE` parameter put the exact same password you used to encrypt the tokens and credentials
6. Set your bot to run and bathe in its majestic glory!

> If you have any problems with any of these steps you can make an issue on the TitanBot repository or DM `Johnny Wobble#1085`