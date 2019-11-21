import random
import asyncio
import datetime
from typing import Union, List

import discord
from discord.ext import commands

import event_utils
import extras
import checks
import polls
import admin
from math_equ import math_main
from tokens import read_discord_token


token = read_discord_token()
bot = commands.Bot(command_prefix=['-', './'], case_insensitive=True)
bot.remove_command("help")

# listing commands for the help command

extras.Commands('Die', 'Kills the bot', '-die', 'Dev')
extras.Commands('MakePoll',
                'Makes a reaction style poll; you add in options '
                'after you send the -makepoll command',
                '-makepoll',
                'Dev, Admin, FRC Leadership')
extras.Commands('Events',
                'Displays events from the team calendar for today '
                'unless an amount of days is specified',
                '-events <O: num days>',
                'None')
extras.Commands('Channels',
                'Lists which channels are subscribed to the auto announcements',
                '-channels',
                'Dev')
extras.Commands('Setup', 'Starts the auto announcement system',
                '-setup',
                'Dev, Admin, FRC Leadership')
extras.Commands('Math',
                "Solves math equations/expressions. "
                "Use the flag '-v' to specify the variable that you want to solve for",
                '-math <expression/equation> O: -v <variable to solve for>',
                'None')
extras.Commands('Test',
                'Used to check if bot is running; says "Confirmed." if so',
                '-test',
                'None')
extras.Commands('SetAlarm',
                "Sets an alarm to happen at the time specified by '-t' (HH:MM, 24 hour clock) and "
                "pings anything specified by ‘-p’. If you want to ping multiple people use '-p' "
                "multiple times.\nPlease note that 12am, which would be 24:00, "
                "is expressed as 00:00",
                '-setalarm -t <HH:MM> -p <@mention>',
                'None')
extras.Commands('Help',
                "Shows the help page. To learn more about specific commands, do '-help <command>'",
                '-help <O: command>',
                'None')


# ------------- Start of commands ------------


@bot.command(name='test')
async def test(ctx):
    """
    Confirmation that the bot is up and local time

    Permissions needed: None

    :param ctx: context object for the message
    :type ctx: Object
    """
    await ctx.channel.send(f"Confirmed."
                           f"\nLocal time: {datetime.datetime.now().strftime('%H:%M:%S')}")


@checks.is_dev()
@bot.command(name="die")
async def die(ctx):
    """
    Kills bot

    Permissions needed: being a dev

    :param ctx: context object for the message
    :type ctx: Object
    """
    await ctx.channel.send('Ok, bye bye')
    raise SystemExit("Used command '-die'")


@checks.is_admin('FRC Leadership')
@bot.command(name='makepoll')
async def make_poll(ctx):
    """
    Makes a poll that assigns a role for reacting and a reaction specific role, it can only be ended
    by the author of the poll

    permissions needed: Admin, FRC Leadership

    :param ctx: context object for the message
    :type ctx: Object
    """
    try:
        await ctx.channel.send('Name your poll, then list out the options, one per message, '
                               'send `done` when you are finished')

        def message_check(m) -> bool:
            return m.channel == ctx.channel and m.author == ctx.message.author

        msg = await bot.wait_for('message', check=message_check)  # blocking

        action_list = await polls.get_roles(bot, ctx, message_check)
        poll = polls.Poll([emoji for role, emoji in action_list],
                          [role for role, emoji in action_list],
                          msg.author, msg.content)
        embed, poll = await polls.create_poll_embed(poll)
        poll.message = await ctx.channel.send(content=None, embed=embed)
        await poll.add_reactions()
        await poll.save(bot)
        await poll.get_compare_reactions()
    except RuntimeError:
        return

    except Exception as E:
        await ctx.channel.send(E)


@bot.command(name='events')
@checks.get_args_in_message(max_args=1, arg_types=[int])
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
    try:
        if len(user_args) == 1:
            embed = await event_utils.manage_events(bot, ctx=ctx, days=user_args[0], auto=False)
        else:  # len(user_args) == 0:
            embed = await event_utils.manage_events(bot, today=True, auto=False)
        await ctx.channel.send(embed=embed, content=None)
    except Exception as eee:  # This is when it sends an error-based message to it can skip back
        print(eee)


@checks.is_dev()
@bot.command(name='channels')
async def channel_test(ctx):
    """
    Debugging command, sends a message to every channel written in channels.txt

    Permissions needed: being a dev

    :param ctx: context object for the message
    :type ctx: Object
    """
    try:
        await admin.channels(bot, ctx)
    except Exception as ee:
        await ctx.channel.send(ee)


@checks.is_admin('FRC Leadership')
@bot.command(name='setup')
async def setup(ctx):
    """
    If the process is successful then it reads the channel id and writes it to channels.txt

    Permissions needed: FRC Leadership, admin

    :param ctx: context object for the message
    :type ctx: Object
    """
    try:
        await event_utils.setup(ctx, bot)
    except Exception as ee:
        await ctx.channel.send(ee)


@bot.command(name='Math')
@checks.get_args_in_message(min_args=1, max_args=9999, arg_types=str)
async def math(ctx, user_args: List[str]):
    """
    Solves either a math equation or expression. It can hang if the expression is too complex, e.g.
    5587^5587^5587

    Permissions needed: None

    :param ctx: context object for the message
    :type ctx: Object
    :param user_args: args that the user passed in
    :type: List[Union[int, float, str]]
    """
    await ctx.channel.trigger_typing()
    try:
        answers, equ = math_main(user_args)
        math_embed = discord.Embed(
            title=f"`{equ}`",
            color=discord.Color.from_rgb(67, 0, 255),
            description=f"```\n{''.join(answers)}\n```"
        )
        await ctx.channel.send(content=None, embed=math_embed)
    except Exception as e:
        await ctx.channel.send(f"Well, You did something wrong\n`{e}`")


@bot.command(name='setalarm')
@checks.get_args_in_message(min_args=4, max_args=99999, arg_types=str)
async def setalarm(ctx, user_args: List[str]):
    """TODO make this function better
    Creates and alarm that pings people specified at the time (24hr clock) specified. Currectly only
    works for the
    current day (it can't do any days in advance)

    Permissions needed: None

    :param ctx: context object for the message
    :type ctx: Object
    :param user_args: args that the user passed in
    :type: List[Union[int, float, str]]
    """
    try:
        static_message_list = user_args
        pings = ""
        time = None
        for i in static_message_list:
            if i == '-t':
                index = user_args.index(i) + 1
                time = user_args[index]
                user_args[index - 1] = None
                user_args[index] = None
            elif i == '-p':
                index = user_args.index(i) + 1
                pings += f"{user_args[index]} "
                user_args[index - 1] = None
                user_args[index] = None
        time, pings = await event_utils.check_for_errors(ctx, time, pings)
        reminder = ""
        for i in user_args:
            if i is not None:
                reminder += f"{i} "
        bot.loop.create_task(event_utils.alarm(time, reminder, ctx, pings))
    except Exception as qw:
        print(qw)


@bot.command(name='help')
@checks.get_args_in_message(max_args=1, arg_types=[str])
async def helper(ctx, user_args: List[str]):
    """
    Sends the help embed, can also give specific help of a given command

    Permissions needed: None

    :param ctx: context object for the message
    :type ctx: Object
    :param user_args: args that the user passed in
    :type: List[Union[int, float, str]]
    """
    try:
        await extras.helper(ctx, user_args)
    except Exception as e:
        print(e)


@bot.event
async def on_command_error(ctx, error):
    """
    called when someone uses the prefix on something that isn't a command

    :param ctx: context object for the message
    :type ctx: Object
    :param error: commands.errors.CommandNotFound will lead to an error message being sent
    :type error: Exception
    """
    if isinstance(error, commands.errors.CommandNotFound):
        await extras.command_error(ctx, '404', 'command not found',
                                   command=ctx.message.content.split()[0][1:])


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
    games = ["-help for help", "Official bot of Team 5587", "when you're not looking"]
    while not bot.is_closed():
        try:
            status = random.choice(games)
            await bot.change_presence(activity=discord.Game(status))
            await asyncio.sleep(10)
        except Exception as exc:  # I'm too lazy to figure out which one is crashing the bot
            print(exc)
            continue


admin.make_cache()
checks.load_devs_config()

bot.loop.create_task(event_utils.auto_announcements(bot))
bot.loop.create_task(game_presence())
bot.loop.create_task(server_list())
bot.loop.create_task(polls.Poll.runall(bot))


bot.run(token)
