"""
this file contains any bot command or method that controls the auto-announcements and the alarm logic
"""
import ***REMOVED***
import discord

import extras
import asyncio
import calendar_api


empty_list = []


async def setup(ctx, bot):  # when this method is completed it with write the channel id to channels.txt
    """
    A question response dialogue with someone try to set up the auto-announcement system on a channel, when this is
    completed with a confirmation, it writes the channel id to channels.txt, and stores it for future announcements

    :param ctx: context object
    :param bot: object that represents the connection to discord
    :return: None
    """
    await ctx.channel.send("Do you want this channel to receive announcements? [Y/N]")
    while True:  # breaks when it receives a message for the right channel
        msg = await bot.wait_for('message')
        if msg.channel.id == ctx.channel.id:
            break
    msg = msg.content.upper()
    if msg != 'Y':
        await ctx.channel.send("Run '-setup' in the channel you want the announcements to be in")
        return
    with open('Xtras/channels.txt', 'r') as f:  # reads all current ids on the text file (list)
        channel_id_list = f.readlines()
    if str(ctx.channel.id) in channel_id_list:   # checks if channels is already in the list
        await ctx.channel.send("This channel is already going to get announcements")
        return
    with open('Xtras/channels.txt', 'a') as f:  # writes the channels id to text file
        f.write("\n" + str(ctx.channel.id))
    await ctx.channel.send("This channel has now been added to the list")


async def alarm(time, content, ctx, pings):  # this gets looped to inside of an event loop
    """
    This method is called instide of a loop, and it will continue to loop until the destination time is reached, then it
    will send out the alarm message (embed) and stop

    :param time: ***REMOVED***.time object
    :param content: str, content of message
    :param ctx: context object
    :param pings: str, comma separated list of pings
    :return: None
    """
    await ctx.channel.send("Alarm set!")
    while True:
        if time <= ***REMOVED***.***REMOVED***.now().time() <= ***REMOVED***.time(time.hour, time.minute+5, time.second, time.microsecond):  # checks if time is within 5 secs of scheduled time
            break
        else:
            await asyncio.sleep(30)
    alarm_embed = discord.Embed(           # creates embed
        title=f"Alarm at {time.strftime('%H:%M')}",
        description=f"{content}",
        color=discord.Color.from_rgb(67, 0, 255))
    alarm_embed.set_footer(text=f"Scheduled by: {ctx.message.author.nick}")
    await ctx.channel.send(pings)
    await ctx.channel.send(content=None, embed=alarm_embed)


async def check_for_errors(ctx, time, pings):
    """
    This take all of the args given by the human on discord and checks them for errors, if there is and error it calls
    the command_error method to notify the human what they have messed up, if it succeds then this wil take the time str
    and convert it to a ***REMOVED***.time object the parent method continues on normally

    :param ctx: context object
    :param time: str
    :param pings: str, comma separated list of pings
    :return: ***REMOVED***.time, pings (str)
    """
    if time is None:
        await extras.command_error(ctx, '505', "Missing arg '-t'", missing_args='-t')
        return
    elif pings == "":
        await extras.command_error(ctx, '505', "Missing arg '-p'", missing_args='-p')
        return
    try:
        time = ***REMOVED***.***REMOVED***.strptime(time, "%H:%M").time()
    except TypeError:
        await extras.command_error(ctx, '707', "Bad input, '-t' arg must be in format: HH:MM")
        return
    return time, pings


def create_event_embed(today_bool, yes_bool, num_days=None):
    """
    Creates the correct embed depending on the values for today_bool and yes_bool

    today_bool and yes_bool: embed for today only with events
    today_bool and not yes_bool: embed for today without events
    not today_bool and yes_bool: embed for more then one day containing events
    not today_bool and not yes_bool: embed for more then one day, with out events

    :param today_bool: bool
    :param yes_bool: bool
    :param num_days: int
    :return: embed
    """
    if yes_bool and today_bool:
        embed = discord.Embed(
            title="List of upcoming events",
            description=f"These are the events today",
            color=discord.Color.from_rgb(67, 0, 255))
    elif today_bool and not yes_bool:
        embed = discord.Embed(
            title=f'There are no events today',
            color=discord.Color.from_rgb(67, 0, 255))
    elif not today_bool and yes_bool:
        embed = discord.Embed(
            title="List of upcoming events",
            description=f"These are the events happening in the next {num_days} day(s)",
            color=discord.Color.from_rgb(67, 0, 255))
    else:
        embed = discord.Embed(
            title=f'There are no events in the next {num_days} day(s)',
            color=discord.Color.from_rgb(67, 0, 255))
    return embed


async def events_by_day(days=None, ctx=None, yes=False):
    """
    This creates an embed for any amount of days, and then returns it to the parent method to have the actual events
    added in, it raises a ValueError as a shortcut back, it also generates the list of events that the parent method
    will add to the embed

    :param days: str
    :param ctx: context
    :param yes: bool
    :return: discord.Embed, list
    """
    if ctx is not None:
        days = ctx.message.content.split()[1]
    if days.isdigit():
        event_list = calendar_api.main(int(days), False)
        if event_list == empty_list:
            no_events = create_event_embed(False, False, num_days=days)
            if yes:
                return no_events, None
            await ctx.channel.send(content=None, embed=no_events)
            raise ValueError
        event_embed = create_event_embed(False, True, num_days=days)
        return event_embed, event_list
    await extras.command_error(ctx, '707', 'Days specified is not a number')
    raise ValueError


async def events_today(ctx=None, yes=False):
    """
    This creates an embed for only events happening today, and then returns it to the parent method to have the actual
    events added in, it raises a ValueError as a shortcut back, it also generates the list of events that the parent
    method will add to the embed

    :param yes: bool, whether it is called from auto-announcements
    :param ctx: context object
    :return: discord.Embed, list
    """
    event_list = calendar_api.main(1, True)
    if event_list == empty_list:
        no_events = create_event_embed(True, False)
        if yes:
            return no_events, None
        await ctx.channel.send(content=None, embed=no_events)
        raise ValueError
    event_embed = create_event_embed(False, True)
    return event_embed, event_list


def WHAT_TIME_IS_IT(question_mark):
    """
    Checks if it is 9:30, returns True if it is

    :param question_mark: literally just exists so when its called there is a question mark (str)
    :return: bool
    """
    return ***REMOVED***.***REMOVED***.strptime('9:30', '%H:%M').time() <= ***REMOVED***.***REMOVED***.now().time() <= \
        ***REMOVED***.***REMOVED***.strptime('9:36', '%H:%M').time()


async def manage_events(channels, bot, today=False):
    """
    Gets basic embed then either appends the events to it and sends it or sends an empty one saying that there are no
    events happening, it then iterates through all of the channels, creating the channel object from the channel ids and
    sends them to all of the channels saved in channels.txt

    :param today: bool, if True then it send an embed that only contains today's events
    :param channels: list (str), list of strings representing all of the channels that the announcement must be sent to
    :param bot: connection to discord
    :return: None
    """
    if today:  # get events for today
        event_embed, event_list = await events_today(yes=True)
    else:  # gets events for the next week
        event_embed, event_list = await events_by_day(days='7', yes=True)
    if event_list is not None:  # if the event_list is None it will just send the embed saying that there are no events
        for i in range(len(event_list)):  # iteratively adds events to embed
            if event_list[i].get('end') is None:  # for events without a time
                event_embed.add_field(name=event_list[i].get('date'), value=event_list[i].get('real_event'),
                                      inline=False)
            else:  # for events with a time
                event_embed.add_field(name=event_list[i].get('date'),
                                      value=f"{event_list[i].get('real_event')}\nGoing from "
                                      f"{event_list[i].get('start')} until {event_list[i].get('end')}",
                                      inline=False)
    for channel in channels:
        channel = bot.get_channel(int(channel))
        await channel.send(content=None, embed=event_embed)


def read_channels():
    """
    returns a list of all of the channel ids saved to channels.txt

    :return: list (str)
    """
    with open('Xtras/channels.txt', 'r') as f:  # reads channels.txt
        channels = f.readlines()
        channels.pop(0)
    return channels


async def auto_announcements(bot):
    """
    Loops inside of event loop, first it checks if it is 9:00 and if it is, it checks is it is sunday, on sundays it
    sends out a message covering events for the whole week, if is is just any other day, it will send out the message
    only covering that day

    :param bot: connection to discord
    :return: None (just loops)
    """
    last_day = ***REMOVED***.***REMOVED***.today() + ***REMOVED***.timedelta(days=-1)  # creates a variable representing yesterday
    last_day = last_day.weekday()
    await bot.wait_until_ready()
    while not bot.is_closed():  # loops as long as the bot is connected to discord
        if WHAT_TIME_IS_IT('?'):  # True if it is 9:30
            this_day = ***REMOVED***.***REMOVED***.today().weekday()
            channels = read_channels()  # reads channel ids
            if ***REMOVED***.***REMOVED***.today().weekday() == 6 and this_day != last_day:  # if it is sunday and it hasn't already sent a message
                await manage_events(channels, bot)
                last_day = this_day
                await asyncio.sleep(9999)
            elif this_day != last_day:  # if it is not sunday and hasn't alread sent a message
                await manage_events(channels, bot, today=True)
                last_day = this_day
                await asyncio.sleep(9999)
        await asyncio.sleep(60)
