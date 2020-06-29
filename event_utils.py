"""
this file contains any bot command or method that controls the auto-announcements and the alarm
logic
"""
import datetime
import asyncio
from typing import List, Union

import discord

import extras
from classes.setup_poll import SetupPoll
# from classes.calendar_api import CalendarAPI
# from classes.calendar import EventCalendar
from classes.gcal_api import get_all_events_until, get_service
from classes.gcal_event import Event


# when this method is completed it with write the channel id to channels.txt
async def setup(ctx, bot) -> None:
    """
    Uses a reaction poll to determine if the person wants to subscribe or unsubscribe from the
    announcements

    :param ctx: context object for the message
    :type ctx: Object
    :param bot: client connection to discord
    :type bot: Object
    """
    setup_poll = SetupPoll(ctx.message.author, bot)
    await setup_poll.start(ctx.channel)
    await setup_poll.loop()


async def alarm(time: datetime.time, content: str, ctx, pings: str):
    """
    This method is called inside of a loop, and it will continue to loop until the destination time
    is reached, then it
    will send out the alarm message (embed) and stop

    this gets looped to inside of an event loop

    :param time: time that the alarm with go off
    :type time: datetime.time object
    :param content: content of the message
    :type content: str
    :param ctx: context object for the message
    :type ctx: Object
    :param pings: comma separated list of pings
    :type pings: str
    """
    await ctx.channel.send("Alarm set!")
    while True:
        # checks if time is within 5 secs of scheduled time
        if time <= datetime.datetime.now().time() <= \
                datetime.time(time.hour, time.minute + 5, time.second):
            break
        else:
            await asyncio.sleep(30)
    alarm_embed = discord.Embed(  # creates embed
        title=f"Alarm at {time.strftime('%H:%M')}",
        description=f"{content}",
        color=discord.Color.from_rgb(67, 0, 255))
    alarm_embed.set_footer(text=f"Scheduled by: {ctx.message.author.nick}")
    await ctx.channel.send(pings)
    await ctx.channel.send(content=None, embed=alarm_embed)


def create_event_embed(is_today: bool, num_days: int = None) -> discord.Embed:
    """
    Creates the correct embed depending on the values for is_today and events_exist

    is_today and events_exist: embed for is_today with events
    is_today and not events_exist: embed for is_today without events
    not is_today and events_exist: embed for more then one day containing events
    not is_today and not events_exist: embed for more then one day, without events

    :param is_today: True if the events are only for today
    :type is_today: bool
    :param num_days: number of days the events are for
    :type num_days: int
    :return: embed for the message
    :rtype: discord.Embed
    """
    if is_today:
        embed = discord.Embed(
            title="Events Today",
            color=extras.Colors.purple)
    else:
        unit = "days"
        unit1 = "tomorrow"
        if num_days % 7 == 0:
            num_days //= 7
            unit = "weeks"
            unit1 = "this week"
        embed = discord.Embed(
            title=f"Events happening through "
                  f"{f'the next {num_days} {unit}' if num_days != 1 else unit1}",
            color=extras.Colors.purple)
    return embed


def get_events(days: int) -> List[List[Event]]:
    """
    First it sets up the api, then it gets the events from it, organizes the events by date, indexes
    the calendar by date, returns the events that are happening in the next `days` days, if you want
    events for today `days` should equal 0

    :param days: number of days the events cover
    :type days: int
    :return: list of events within the days specified
    :rtype: List[List[Event]]
    """
    service = get_service()
    events = get_all_events_until(service, days)
    return events


def events_by_day(days: int) -> (discord.Embed, List[List[Event]]):
    """
   Gets the events for the next `days` days and generates the correct embed.

    :param days: days as imputed by user
    :type days: int
    :return: embed for message, list of events
    :rtype: discord.Embed, List[List[Event]]
    """
    if days == 0:
        return events_today()
    event_list = get_events(days)
    event_embed = create_event_embed(False, num_days=days)
    return event_embed, event_list


def events_today() -> (discord.Embed, List[List[Event]]):
    """
    Gets the events for today and generates the embed that is correct

    :return: embed for events, list of events
    :rtype: discord.Embed, List[List[Event]]
    """
    event_list = get_events(0)
    event_embed = create_event_embed(True)
    return event_embed, event_list


def WHAT_TIME_IS_IT(question_mark: str) -> bool:
    """
    Checks if it is 9:30, returns True if it is, it is at 13:30 because it runs on a Heroku server
    that is in a timezone 4 hours behind EST

    :param question_mark: literally just exists so when its called there is a question mark
    :type question_mark: str (useless)
    :return: whether its 9:30
    :rtype: bool
    """
    return datetime.datetime.strptime('13:30', '%H:%M').time() <= datetime.datetime.now().time() \
           <= datetime.datetime.strptime('13:36', '%H:%M').time()


async def manage_events(bot, today: bool = False, days: int = 14, auto: bool = True,
                        channels: List[int] = None) -> Union[discord.Embed, None]:
    """
    Gets basic embed then either appends the events to it and sends it or sends an empty one saying
    that there are no events happening, it then iterates through all of the channels, creating the
    channel object from the channel ids and sends them to all of the channels saved in channels.txt

    :param today: if True then it send an embed that only contains today's events
    :type today: bool
    :param channels: list of strings of the channels that the announcement must be sent to
    :type channels: list[int]
    :param bot: client connection to discord
    :type bot: Object
    :param days: amount of days the data is for
    :type days: str (int)
    :param auto: True if this is being called by the auto-announcements
    :type auto: bool
    """
    if today:  # get events for today
        event_embed, event_list = events_today()
    else:  # gets events for the next week
        event_embed, event_list = events_by_day(days)

    for events in event_list:  # iteratively adds events to embed
        event_embed: discord.Embed
        event_embed.add_field(
            name=f"**{events[0].start_day} ({events[0].start_date.strftime('%m/%d')})**",
            value="\n".join([event.str() for event in events]),
            inline=False)

    event_embed.set_field_at(0, name="**Today**", value=event_embed.fields[0].value, inline=False)

    if not auto:
        return event_embed
    for channel in channels:
        channel = bot.get_channel(channel)
        await channel.send(content=None, embed=event_embed)


async def auto_announcements(bot):
    """
    Loops inside of event loop, first it checks if it is 9:00 and if it is, it checks is it is
    sunday, on sundays it sends out a message covering events for the whole week, if is is just any
    other day, it will send out the message only covering that day. It will also create the channel
    cache if it does not already exist.

    :param bot: client connection to discord
    :type bot: Object
    """
    last_day = datetime.datetime.today() + datetime.timedelta(days=-1)
    # creates a variable representing yesterday
    last_day = last_day.weekday()
    await bot.wait_until_ready()
    while not bot.is_closed():  # loops as long as the bot is connected to discord
        if WHAT_TIME_IS_IT('?'):  # True if it is 9:30
            this_day = datetime.datetime.today().weekday()
            try:
                # if it is sunday and it hasn't already sent a message
                if datetime.datetime.today().weekday() == 6 and this_day != last_day:
                    await manage_events(bot, today=False, channels=extras.SYSTEM_CONFIG['channels'])
                    last_day = this_day
                    await asyncio.sleep(9999)
                elif this_day != last_day:  # if it is not sunday and hasn't already sent a message
                    await manage_events(bot, days=3, channels=extras.SYSTEM_CONFIG['channels'])
                    last_day = this_day
                    await asyncio.sleep(9999)
            except ValueError:
                continue
        await asyncio.sleep(60)
