"""
this handles all interactions the google calendar api, and sorting the events that follow
"""
import datetime

from calendarAPIClass import CalendarAPI
from eventCalendarClass import EventCalendar


def main(days=None):
    """
    First it sets up the api, then it gets the events from it, organizes the events by date, indexes the calendar by
    date, returns the events that are happening in the next `days` days

    :param days: int
    :param today: bool
    :return: list
    """
    # try:
    api = CalendarAPI()
    api.start_api()
    api.get_calendars()
    big_calendar = api.calendars[0].combine(api.calendars[1:])

    big_calendar.sort(key=lambda x: x.date)
    massive_calendar = EventCalendar(list_of_events=big_calendar)
    sliced_calendar = massive_calendar[datetime.datetime.today().date() + datetime.timedelta(days=days)]
    return sliced_calendar
