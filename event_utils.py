"""
this file contains any bot command or method that controls the auto-announcements and the alarm logic
"""
import datetime
import asyncio
from typing import List, Union

import discord

import extras
from admin import clear_and_find_channels
from classes.SetupPollClass import SetupPoll
from classes.calendar_api import CalendarAPI
from classes.calendar import EventCalendar
from classes.calendar_event import Event


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
    setup_poll = SetupPoll(['✅', '❌'], ctx.message.author, 'Auto-announcements')
    await setup_poll.create_poll_embed()
    setup_poll.message = await ctx.channel.send(embed=setup_poll.embed, content=None)
    await setup_poll.add_reactions()
    await setup_poll.sub_to_auto_announcements(bot, ctx)  # blocking


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
                datetime.time(time.hour, time.minute+5, time.second):
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


async def check_for_errors(ctx, time: str, pings: str) -> (datetime.time, str):
    """
    This take all of the args given by the human on discord and checks them for errors, if there is
    and error it calls the command_error method to notify the human what they have messed up, if it
    succeeds then this wil take the time str and convert it to a datetime.time object the parent
    method continues on normally

    :param ctx: context object for the message
    :type ctx: Object
    :param time: time that will be converted into a datetime object
    :type time: str
    :param pings: comma separated list of pings
    :type pings: str
    :return: time of alarm, comma separated list of pings
    :rtype: datetime.time, str
    """
    if time is None:
        await extras.command_error(ctx, '505', "Missing arg '-t'", missing_args='-t')
        return
    elif pings == "":
        await extras.command_error(ctx, '505', "Missing arg '-p'", missing_args='-p')
        return
    try:
        time = datetime.datetime.strptime(time, "%H:%M").time()
    except TypeError:
        await extras.command_error(ctx, '707', "Bad input, '-t' arg must be in format: HH:MM")
        return
    return time, pings


def create_event_embed(is_today: bool, events_exist: bool, num_days: int = None) -> discord.Embed:
    """
    Creates the correct embed depending on the values for is_today and events_exist

    is_today and events_exist: embed for is_today with events
    is_today and not events_exist: embed for is_today without events
    not is_today and events_exist: embed for more then one day containing events
    not is_today and not events_exist: embed for more then one day, without events

    :param is_today: True if the events are only for today
    :type is_today: bool
    :param events_exist: True if there are events in the list
    :type events_exist: bool
    :param num_days: number of days the events are for
    :type num_days: int
    :return: embed for the message
    :rtype: discord.Embed
    """
    if events_exist and is_today:
        embed = discord.Embed(
            title="**Events Today**",
            color=discord.Color.from_rgb(67, 0, 255))
    elif is_today and not events_exist:
        embed = discord.Embed(
            title=f'There are no events today',
            color=discord.Color.from_rgb(67, 0, 255))
    elif not is_today and events_exist:
        embed = discord.Embed(
            title=f"**Events happening through "
                  f"{f'the next {num_days} days' if num_days != 1 else 'tomorrow'}**",
            color=discord.Color.from_rgb(67, 0, 255))
    else:
        embed = discord.Embed(
            title=f"**There are no events happening through "
                  f"{f'the next {num_days} days' if num_days != 1 else 'tomorrow'}**",
            color=discord.Color.from_rgb(67, 0, 255))
    return embed


def get_events(days: int = None) -> List[Event]:
    """
    First it sets up the api, then it gets the events from it, organizes the events by date, indexes
    the calendar by date, returns the events that are happening in the next `days` days, if you want
    events for today `days` should equal 0

    :param days: number of days the events cover
    :type days: int
    :return: list of events within the days specified
    :rtype: List[Event]
    """
    api = CalendarAPI()
    api.start_api()
    api.get_calendars()
    big_calendar = api.calendars[0].combine(api.calendars[1:])

    big_calendar.sort(key=lambda x: x.date_time)
    massive_calendar = EventCalendar(list_of_events=big_calendar)
    massive_calendar.find_empty_days()
    sliced_calendar = massive_calendar[datetime.datetime.today().date() +
                                       datetime.timedelta(days=days)]
    return sliced_calendar


async def events_by_day(ctx=None,
                        days: int = None,
                        events_exist: bool = False) -> (discord.Embed, Union[List, None]):
    """
    This creates an embed for any amount of days, and then returns it to the parent method to have
    the actual events added in, it raises a ValueError as a shortcut back, it also generates the
    list of events that the parent method will add to the embed

    :param ctx: context object for the message
    :type ctx: Object
    :param days: days as imputed by user
    :type days: int
    :param events_exist: whether there are events for the time specified
    :type events_exist: bool
    :return: embed for message, list of events
    :rtype: discord.Embed, List[Event]
    """
    event_list = get_events(days)
    if event_list == list():
        no_events = create_event_embed(False, False, num_days=days)
        if events_exist:
            return no_events, None
        await ctx.channel.send(content=None, embed=no_events)
        raise ValueError
    event_embed = create_event_embed(False, True, num_days=days)
    return event_embed, event_list


async def events_today(ctx=None, events_exist: bool = False) -> (discord.Embed, Union[List, None]):
    """
    This creates an embed for only events happening today, and then returns it to the parent method
    to have the actual events added in, it raises a ValueError as a shortcut back, it also generates
    the list of events that the parent method will add to the embed

    :param events_exist: whether there are events
    :type events_exist: bool
    :param ctx: context object for the message
    :type ctx: Object
    :return: embed for events, list of events
    :rtype: discord.Embed, List[Event]
    """
    event_list = get_events(0)
    if event_list == list():
        no_events = create_event_embed(True, False)
        if events_exist:
            return no_events, None
        await ctx.channel.send(content=None, embed=no_events)
        raise ValueError
    event_embed = create_event_embed(True, True)
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


async def manage_events(bot, ctx=None, today: bool = False, days: int = 14, auto: bool = True,
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
    :param ctx: context object for the message
    :type ctx: Object
    :param days: amount of days the data is for
    :type days: str (int)
    :param auto: True if this is being called by the auto-announcements
    :type auto: bool
    """
    if today:  # get events for today
        event_embed, event_list = await events_today(events_exist=True)
    else:  # gets events for the next week
        event_embed, event_list = await events_by_day(ctx=ctx, days=days, events_exist=True)

    # if the event_list is None it will just send the embed saying that there are no events
    if event_list is not None:
        for num, event in enumerate(event_list):  # iteratively adds events to embed

            # for events that are on the same day of the previous one
            if event.date == event_list[num - 1].date and len(event_list) > 1:
                index = len(event_embed.fields) - 1
                value = event_embed.fields[index].value

                if event.start_time is None:   # for events without a time
                    add = f"➤ {event.title} "\
                          f"{f'- {event.description}' if event.description is not None else ''}"

                else:  # for events with a time
                    add = f"➤ {event.title} "\
                          f"{f'- {event.description}' if event.description is not None else ''}\n"\
                          f"━➤ *{event.start_time.strftime('%I:%M %p')} to "\
                          f"{event.end_time.strftime('%I:%M %p')}*"

                event_embed.set_field_at(index,
                                         name=event.date.strftime("%A (%m/%d/%y)"),
                                         value=f"{value}\n{add}", inline=False)
                continue

            elif event.start_time is None:  # for events without a time
                event_embed.add_field(name=event.date.strftime("%A (%m/%d/%y)"),
                                      value=f"➤ {event.title} "
                                            f"{f'- {event.description}' if event.description is not None else ''}",
                                      inline=False)

            else:  # for events with a time
                event_embed.add_field(name=event.date.strftime("%A (%m/%d/%y)"),
                                      value=f"➤ {event.title} "
                                            f"{f'- {event.description}' if event.description is not None else ''}\n"
                                            f"━➤ *{event.start_time.strftime('%I:%M %p')} to "
                                            f"{event.end_time.strftime('%I:%M %p')}*",
                                      inline=False)
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
                channels = clear_and_find_channels()  # reads channel ids
                # if it is sunday and it hasn't already sent a message
                if datetime.datetime.today().weekday() == 6 and this_day != last_day:
                    await manage_events(bot, today=False, channels=channels)
                    last_day = this_day
                    await asyncio.sleep(9999)
                elif this_day != last_day:  # if it is not sunday and hasn't already sent a message
                    await manage_events(bot, days=3, channels=channels)
                    last_day = this_day
                    await asyncio.sleep(9999)
            except ValueError:
                continue
        await asyncio.sleep(60)
