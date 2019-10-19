import datetime
from typing import Union, List

from eventClass import Event


class EventCalendar:
    def __init__(self, calendar_dict: dict, build):
        self.calendar_dict = calendar_dict
        self.service = build
        self.list_of_events_raw = []
        self.list_of_events = []

    def organize(self):
        """
        For every DooDoo style Google event dict in self.list_of_events_raw it creates a nice Event class for each one

        :return: EventCalendar
        """
        self.list_of_events_raw = self.calendar_dict.get('items')  # get events in the calendar
        for raw_event in self.list_of_events_raw:
            event = Event(self.calendar_dict.get("summary"), raw_event)
            self.list_of_events.append(event.make_better())
        return self

    def __getitem__(self, item: Union[datetime.date, slice, int]) -> List[Event]:
        """
        Returns all events that happen before and on the date

        :param item: datetime.date
        :return: list[Event]
        """
        if type(item) in (slice, int):
            return self.list_of_events[item]
        for num, event in enumerate(self.list_of_events):
            if event.date.date() > item:
                return self.list_of_events[:num - 2]

    def __len__(self) -> int:
        """
        Returns the amount of events in this calendar

        :return: int
        """
        return len(self.list_of_events)
