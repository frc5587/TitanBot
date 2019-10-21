import datetime
from typing import Union, List

from classes.calendar_event import Event


class EventCalendar:

    def __init__(self,
                 calendar_dict: dict = None,
                 build=None,
                 list_of_events: List[Event] = None):
        """
        Object representing a list of events from a specific google calendar, you can index it to get events through
        that date or just with ints and slices

        :param calendar_dict: Contains all of the events in the calendar
        :type calendar_dict: dict
        :param build: The object used to interact with the Google API
        :type build: Object
        :param list_of_events: Only used to create a full comprehensive calendar with events already in Event format
        :type list_of_events: List[Event]
        """
        self.calendar_dict = calendar_dict
        self.service = build
        self.list_of_events_raw = []
        self.list_of_events = list_of_events if list_of_events is not None else []

    def organize(self):
        """
        For every DooDoo style Google event dict in self.list_of_events_raw it creates a nice Event class for each one

        :return: EventCalendar
        """
        self.list_of_events_raw = self.calendar_dict.get(
            'items')  # get events in the calendar
        for raw_event in self.list_of_events_raw:
            event = Event(self.calendar_dict.get("summary"), raw_event)
            self.list_of_events.append(event.make_better())
        return self

    def __getitem__(self,
                    item: Union[datetime.date, slice, int]) -> List[Event]:
        """
        Returns all events that happen before and on the date

        :param item: The data contained in the [] around the object
        :type item: Union[datetime.date, slice, int]
        :return: list[Event]
        """
        if type(item) in (slice, int):
            return self.list_of_events[item]
        elif type(item) == datetime.date:
            for num, event in enumerate(self.list_of_events):
                if event.date > item:
                    return self.list_of_events[:num]
        else:
            raise TypeError(
                f"Must be either int, slice, or datetime.date, not {type(item)}"
            )

    def __len__(self) -> int:
        """
        Returns the amount of events in this calendar

        :return: int
        """
        return len(self.list_of_events)

    def combine(self, calendars: list) -> List[Event]:
        """
        Combines this calendar and any others in calendars to make one large list of events, this is an unsorted list

        :param calendars: A list of EventCalendar objects, they all get combined
        :type calendars: List[EventCalendar]
        :return: List[Event]
        """
        big_calender = self.list_of_events
        for calendar in calendars:
            big_calender += calendar.list_of_events
        return big_calender

    def find_empty_days(self):
        """
        Iterates through all of the days in self.list_of_events and find days that don't have events for them, then it
        adds "blank" events stating that there are no events that day

        :return: self
        :rtype: Event
        """
        today = datetime.datetime.today().date() - datetime.timedelta(days=1)
        this_day = today
        for num, event in enumerate(self.list_of_events):
            next_day = self.list_of_events[num].date
            if next_day == today:
                coeff = 0
            else:
                coeff = 1
            date_add = this_day + datetime.timedelta(days=1)
            for day in range((next_day - this_day).days - coeff):
                self.list_of_events.insert(
                    num + day,
                    Event(empty=True, date=date_add).make_better())
                date_add += datetime.timedelta(days=1)
            this_day = next_day
        return self
