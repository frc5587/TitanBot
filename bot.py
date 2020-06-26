#!/usr/bin/env python3
import asyncio
import datetime
from typing import Union, List
import re

import discord
from discord.ext import commands
from websockets import exceptions
import logging

import event_utils
import extras
from tokens import read_discord_token
import bot_commands
from classes import poll

START_TIME = datetime.datetime.now()


token = read_discord_token()
bot = commands.Bot(command_prefix=['-', './'], case_insensitive=True)
bot.remove_command("help")

command_group = extras.CommandGroup(bot)


# ------------- Start of commands ------------


@command_group.new_command(name='test', description='Test to see if the bot is on', syntax='-test',
                           max_args=0)
async def test(ctx, user_args: List[str]):
    """
    Confirmation that the bot is up and local time

    :param ctx: context object for the message
    :type ctx: Object
    :param user_args: args passed in by the user
    :type user_args: List[str]
    """
    seconds = int((datetime.datetime.now() - START_TIME).total_seconds())
    await ctx.channel.send(f"Local time: {datetime.datetime.now().strftime('%H:%M')}\n"
                           f"Uptime: {int(seconds / 60 ** 2)}:{int(seconds / 60) % 60}:{seconds % 60} ")


@command_group.new_command(name="Die", description="Kills the bot", syntax="-die", dev_command=True,
                           max_args=0)
async def die(ctx, user_args: List[str]):
    """
    Kills bot

    Permissions needed: being a dev

    :param ctx: context object for the message
    :type ctx: Object
    """
    await ctx.channel.send('Ok, bye bye')
    raise SystemExit("Used command '-die'")


@command_group.new_command(name="makepoll", description="Makes a reaction-role poll",
                           syntax="-makepoll", max_args=0)
async def make_poll(ctx, user_args):
    """
    Makes a poll that assigns a role for reacting and a reaction specific role, it can only be ended
    by the author of the poll

    :param ctx: context object for the message
    :type ctx: Context Object
    """
    await bot_commands.makepoll(ctx, bot)


@command_group.new_command(name="Events", description='Displays events from the team calendar for '
                                                      'today unless an amount of days is specified',
                           syntax="-events <O: num days>", max_args=1, types=int)
async def events(ctx, user_args: List[Union[int, float, str]]):
    """
    Calls the calendar api and read the calendar and gets the events happening within the amount of
    days specified,
    sends them within an embed

    Permissions needed: None

    :param ctx: context object for the message
    :type ctx: Object
    :param user_args: args that the user passed in
    :type: List[Union[int, float, str]]
    """
    await ctx.channel.trigger_typing()
    if len(user_args) == 1:
        embed = await event_utils.manage_events(bot, days=user_args[0], auto=False)
    else:  # len(user_args) == 0:
        embed = await event_utils.manage_events(bot, today=True, auto=False)
    await ctx.channel.send(embed=embed)


@command_group.new_command(name="Channels", description='Lists which channels are subscribed to the'
                                                        ' auto announcements', syntax="-channels",
                           dev_command=True, max_args=0)
async def channel_test(ctx, user_args):
    """
    Debugging command, sends a message to every channel written in channels.txt

    Permissions needed: being a dev

    :param ctx: context object for the message
    :type ctx: Object
    """
    await bot_commands.channels(ctx, bot)


@command_group.new_command(name="setup", description='Starts the auto announcement system',
                           syntax="-setup", max_args=0, frc_leadership_command=True)
async def setup(ctx, user_args):
    """
    If the process is successful then it reads the channel id and writes it to channels.txt

    Permissions needed: FRC Leadership, admin

    :param ctx: context object for the message
    :type ctx: Object
    """
    await event_utils.setup(ctx, bot)


@command_group.new_command(name='Math', description="Solves math equations/expressions. Use the "
                                                    "flag '-v' to specify the variable that you "
                                                    "want to solve for",
                           syntax='-math <expression/equation> O: [-v <variable to solve for>]',
                           min_args=1)
async def math(ctx, user_args: List[str]):
    """
    Solves either a math equation or expression. It can hang if the expression is too complex, e.g.
    5587^5587^5587

    Permissions needed: None

    :param ctx: context object for the message
    :type ctx: Object
    :param user_args: args that the user passed in
    :type: List[str]
    """
    await bot_commands.math(ctx, user_args)


@command_group.new_command(name="SetAlarm",
                           description="Sets an alarm to happen at the time specified by '-t' "
                                       "(HH:MM, 24 hour clock) and pings anyone in your message. "
                                       "You can add an optional message\n"
                                       "Please note that 12am, which would be 24:00, is "
                                       "expressed as 00:00",
                           syntax="-setalarm -t <HH:MM> <O: @mention...> <O: message>", min_args=4)
async def setalarm(ctx, user_args: List[str]):
    """TODO make this function better
    Creates and alarm that pings people specified at the time (24hr clock) specified. Currently only
    works for the
    current day (it can't do any days in advance)

    Permissions needed: None

    :param ctx: context object for the message
    :type ctx: Object
    :param user_args: args that the user passed in
    :type: List[Union[int, float, str]]
    """
    try:
        t = user_args.index('-t')
    except IndexError:
        await extras.command_error(ctx, '505', missing_args='-t')
        raise

    try:
        time = datetime.datetime.strptime(user_args[t + 1], "%H:%M").time()
    except TypeError:
        await extras.command_error(ctx, '707', extra="'-t' arg must be in format: HH:MM")
        raise
    del user_args[t:t+2]

    message = " ".join(user_args)

    pings = " ".join(re.findall(r"<@.*>", message))
    message = re.sub(r"<@.*>", message, "")

    bot.loop.create_task(event_utils.alarm(time, message, ctx, pings))


@command_group.new_command(name="help", description="Help command", syntax="-help <O: command>",
                           max_args=1)
async def helper(ctx, user_args: List[str]):
    """
    Sends the help embed, can also give specific help of a given command

    :param ctx: context object for the message
    :type ctx: Context Object
    :param user_args: args passed in by the user
    :type user_args: List[str]
    """
    await extras.helper(ctx, user_args, command_group)


@bot.event
async def on_command_error(ctx, error):
    """
    Called when someone uses the prefix on something that isn't a command

    :param ctx: context object for the message
    :type ctx: Context Object
    :param error: commands.errors.CommandNotFound will lead to an error message being sent
    :type error: Exception
    """
    if isinstance(error, commands.errors.CommandNotFound):
        await extras.command_error(ctx, '404', command=ctx.message.content.split()[0][1:])
        return
    raise error


# ---------- End of commands -------------


async def server_list() -> None:
    """
    lists all the servers the bot is on every 24 hours
    This loops for the rest of time
    """
    await bot.wait_until_ready()
    while not bot.is_closed():
        print("Current servers:")
        for server in bot.guilds:
            print(server.name)
        print("-----------------")
        print("Logged in as " + bot.user.name)
        print("-----------------")
        await asyncio.sleep(86400)


async def game_presence() -> None:
    """
    Every 10 seconds it randomly changes what "game" the bot is playing
    It loops forever
    """
    await bot.wait_until_ready()
    games = ["-help for help", "my banjo"]
    while not bot.is_closed():
        try:
            for game in games:
                await asyncio.sleep(10)
                await bot.change_presence(activity=discord.Game(game))
                await asyncio.sleep(10)

        except exceptions.ConnectionClosed as exc:
            print(f"game_presence Exception: {exc}")
            print(f"is_closed(): {bot.is_closed()}")
            continue


def run():
    extras.make_cache()

    logger = logging.getLogger('discord')
    logger.setLevel(logging.ERROR)
    handler = logging.FileHandler(filename='cache/discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    bot.loop.create_task(game_presence())
    bot.loop.create_task(server_list())
    bot.loop.create_task(event_utils.auto_announcements(bot))
    bot.loop.create_task(poll.PollBase.runall(bot))

    bot.run(token)


if __name__ == '__main__':
    run()
