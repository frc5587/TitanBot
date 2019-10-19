import discord
from discord.ext import commands
import random
import asyncio
import datetime

import event_utils
import extras
import checks
import polls
import admin
from math_equ import math_main


def read_token():
    """
    reads token.txt, it contains the client secret that the bot needs to connect

    :return: str
    """
    with open("tokens/discord-token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()


token = read_token()
bot = commands.Bot(command_prefix=['-', './'], case_insensitive=True)
bot.remove_command("help")

# listing commands for the help command

extras.Commands('Die', 'Kills the bot', '-die', 'Dev')
extras.Commands('MakePoll', 'Make a reaction style poll, you add in options after you send the -makepoll command', '-makepoll', 'Dev, Admin, FRC Leadership')
extras.Commands('Events', 'Displays events from the team calendar for today unless specified for how many days', '-events <O: num days>', 'None')
extras.Commands('Channels', 'Lets you know which channels are subscribed to the auto announcements', '-channel', 'Dev')
extras.Commands('Setup', 'Starts the auto announcement system', '-setup', 'Dev, Admin, FRC Leadership')
extras.Commands('Math', "Solves math equations/expressions, use the flag '-v' to specify the variable that you may want to solve for",
                '-math <expression/equation> O: -v <variable to solve for>', 'None')
extras.Commands('Test', 'Used to check if bot is running, says "Confirmed." if so', '-test', 'None')
extras.Commands('SetAlarm', "Sets an alarm to happen at time specified by '-t' (HH:MM, 24 hour clock) and to ping "
                            "anything specified by '-p', if you want to ping multiple people use '-p' multiple times,"
                            "\nPlease note 12am, which would be 24:00 is expressed as 00:00, ",
                '-setalarm -t <HH:MM> -p <@mention>', 'None')
extras.Commands('Help', "Shows the help box, if you want specific help, do '-help <command>", '-help O: <command>', 'None')


# ------------- Start of commands ------------


@checks.is_dev()
@bot.command(name="die")
async def die(ctx):
    """
    Kills bot

    Permissions needed: Being Max

    :param ctx: context object
    :return: None
    """
    await ctx.channel.send('Ok, bye bye')
    raise SystemExit("Used command '-die'")


@checks.is_admin('FRC Leadership')
@bot.command(name='makepoll')
async def make_poll(ctx):
    try:
        """
        Makes a poll that assigns a role for reacting and a reaction specific role, it can only be ended by the author of
        the poll

        permissions needed: Admin, FRC Leadership

        :param ctx: context
        :return: None
        """
        await ctx.channel.send('Name your poll, then list out the options, one per message, send `done` when you are finished')

        def message_check(m):
            return m.channel == ctx.channel and m.author == ctx.message.author

        msg = await bot.wait_for('message', check=message_check)  # blocking

        action_list = await polls.get_roles(bot, ctx, message_check)
        poll = polls.Poll([emoji for role, emoji in action_list], [role for role, emoji in action_list], msg.author, msg.content)
        embed, poll = await polls.create_poll_embed(poll)
        poll.message = await ctx.channel.send(content=None, embed=embed)
        await poll.add_reactions()
        await poll.reaction_watch_loop(bot)

    except Exception as E:
        await ctx.channel.send(E)


@bot.command(name='events')
async def events(ctx):
    """
    Calls the calendar api and read the calendar and gets the events happening within the amount of days specified,
    sends them within an embed

    Permissions needed: None

    :param ctx: context object
    :return: None
    """
    await ctx.channel.trigger_typing()
    try:
        if len(ctx.message.content) >= 9:
            event_embed, event_list = await event_utils.events_by_day(ctx=ctx)
        else:
            event_embed, event_list = await event_utils.events_today(ctx=ctx)
    except ValueError:
        return
    for event in event_list:  # iteratively adds events to embed
        if event.start_time is None:  # for events without a time
            event_embed.add_field(name=event.date.strftime("%A (%m/%d/%y)"),
                                  value=f"{event.title}\n{event.description}",
                                  inline=False)
        else:  # for events with a time
            event_embed.add_field(name=event.date.strftime("%A (%m/%d/%y)"),
                                  value=f"{event.title}\n{event.description}"
                                        f"\t*{event.start_time.strftime('%I:%M %p')} till "
                                        f"{event.end_time.strftime('%I:%M %p')}*",
                                  inline=False)
        await ctx.channel.send(content=None, embed=event_embed)
    # for i in range(len(event_dict)):
    #     if event_dict[i].get('end') is None:
    #         event_embed.add_field(name=f"{event_dict[i].get('day')} - {event_dict[i].get('date')}",
    #                               value=event_dict[i].get('real_event'),
    #                               inline=False)
    #     else:
    #         event_embed.add_field(name=f"{event_dict[i].get('day')} - {event_dict[i].get('date')}",
    #                               value=f"{event_dict[i].get('real_event')}\nGoing from "
    #                               f"{event_dict[i].get('start')} until {event_dict[i].get('end')}",
    #                               inline=False)
    # await ctx.channel.send(content=None, embed=event_embed)


@checks.is_dev()
@bot.command(name='channels')
async def channel_test(ctx):
    """
    Debugging command, sends a message to every channel writen to channels.txt

    Permissions needed: being Max

    :param ctx: context object
    :return: context object
    """

    await admin.channels(bot, ctx)


@checks.is_admin('FRC Leadership')
@bot.command(name='setup')
async def setup(ctx):
    """
    If the process is successful then it reads the channel id and writes it to channels.txt

    Permissions needed: FRC Leadership, admin

    :param ctx: context object
    :return: None
    """
    await event_utils.setup(ctx, bot)


@bot.command(name='Math')
async def math(ctx):
    """
    Solves either a math equation or expression, it can hang if the expression is too complex, e.g. 5587^5587^5587

    Permissions needed: None

    :param ctx: context
    :return: None
    """
    await ctx.channel.trigger_typing()
    try:
        answers, equ = math_main(ctx.message.content)
        math_embed = discord.Embed(
            title=f"`{equ}`",
            color=discord.Color.from_rgb(67, 0, 255),
            description=''.join(answers)
        )
        await ctx.channel.send(content=None, embed=math_embed)
    except Exception as e:
        await ctx.channel.send(f"Well, You did something wrong\n`{e}`")


@bot.command(name='test')
async def test(ctx):
    """
    Confirmation that the bot is up, and local time

    Permissions needed: None

    :param ctx: context object
    :return: None
    """
    await ctx.channel.send(f"Confirmed.\nLocal Time: {datetime.datetime.now().strftime('%H:%M:%S')}")


@bot.command(name='setalarm')
async def setalarm(ctx):
    """
    Creates and alarm that pings people specified, and at the time (24hr clock) specified, currectly only works for the
    current day set, it can't do any days in advance

    Permissions needed: None

    :param ctx: context object
    :return: None
    """
    message_list = ctx.message.content.split()[1:]
    static_message_list = message_list
    pings = ""
    time = None
    for i in static_message_list:
        if i == '-t':
            index = message_list.index(i)+1
            time = message_list[index]
            message_list[index-1] = None
            message_list[index] = None
        elif i == '-p':
            index = message_list.index(i)+1
            pings += f"{message_list[index]} "
            message_list[index - 1] = None
            message_list[index] = None
    time, pings = events.check_for_errors(ctx, time, pings)
    reminder = ""
    for i in message_list:
        if i is not None:
            reminder += f"{i} "
    bot.loop.create_task(events.alarm(time, reminder, ctx, pings))


@bot.command(name='help')
async def helper(ctx):
    """
    Sends the help embed, can also give specific help of a given command

    Permissions needed: None

    :param ctx: context object
    :return: None
    """
    try:
        await extras.helper(ctx)
    except Exception as e:
        print(e)


# ---------- End of commands -------------


@bot.event
async def on_command_error(ctx, error):
    """
    called when some uses the prefix on something that isn't a command

    :param ctx: context object
    :param error: class Exception, commands.errors.CommandNotFound
    :return: None
    """
    if isinstance(error, commands.errors.CommandNotFound):
        await extras.command_error(ctx, '404', 'command not found')


async def server_list():
    """
    lists all the servers the bot is on every 10 hours

    :return: None (loops)
    """
    await bot.wait_until_ready()
    while not bot.is_closed():
        print("Current servers:")
        for server in bot.guilds:
            print(server.name)
        print("-----------------")
        print("Logged in as " + bot.user.name)
        print("-----------------")
        await asyncio.sleep(36000)


async def game_presence():
    """
    Every 10 seconds it randomly changes what "game" the bot is playing

    :return: None
    """
    await bot.wait_until_ready()
    games = ["-help for help", "Official bot of Team 5587", "when you're not looking"]
    while not bot.is_closed():
        try:
            status = random.choice(games)
            await bot.change_presence(activity=discord.Game(status))
            await asyncio.sleep(10)
        except Exception:  # I'm too lazy to figure out which one is crashing the bot
            continue

bot.loop.create_task(event_utils.auto_announcements(bot))
bot.loop.create_task(game_presence())
bot.loop.create_task(server_list())
bot.run(token)
