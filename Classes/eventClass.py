import datetime


class Event:
    def __init__(self, calendar_name: str, event_dict: dict, empty: bool = False, date_time: datetime.datetime = None):
        """
        Represents an individual event in a calendar, once make_better() is called it organizes all of the dat for easy
        access

        :param calendar_name: The name of the calendar this event was from
        :type calendar_name: str
        :param event_dict: A massive dictionary representing the event brought to you by Google
        :type event_dict: dict
        :param date_time: The date an time of the event, only use if it is just an empty event
        :type date_time: datetime.datetime
        """
        self.calendar_name = calendar_name
        self.event_dict = event_dict
        self.empty = empty
        self.date = None  # datetime.datetime
        self.day = None  # str
        self.title = None  # str
        self.description = None  # str
        self.end_time = None  # datetime.time
        self.start_time = None  # datetime.time
        self.date_time = date_time

    def make_better(self):
        """
        Changes the DooDoo style Google event dicts into some nice OOP for your convenience

        :return: Event
        """
        self.date = self.event_dict.get('start').get('date')

        if self.date is not None:

            self.title = self.event_dict.get("summary")  # title of event
            self.date = datetime.datetime.strptime(self.event_dict.get('start').get('date'), '%Y-%m-%d')
            self.day = self.date.strftime("%A")
            self.description = self.event_dict.get("description")

        else:

            self.title = self.event_dict.get("summary")  # title of event
            self.date = datetime.datetime.strptime(self.event_dict.get('start').get('dateTime')[:10], '%Y-%m-%d')
            self.day = self.date.strftime("%A")
            self.description = self.event_dict.get("description")

            self.start_time = datetime.datetime.strptime(self.event_dict.get('start').get('dateTime')[11:19], "%X").time()
            self.end_time = datetime.datetime.strptime(self.event_dict.get('end').get('dateTime')[11:19], "%X").time()

        return self

    def __repr__(self) -> str:
        """
        Represents all of the data contained in this with some nice formatting

        :return: str
        """
        return_val = f"\nCalendar:        {self.calendar_name}\n" \
                     f"Event Name:      {self.title}\n" \
                     f"Description:     {self.description}"\
                     f"Date:            {self.date.strftime('%x')}\n" \
                     f"Day of the Week: {self.date.strftime('%A')}\n" \
                     f"Start Time:      {self.start_time.strftime('%I:%M %p') if self.start_time is not None else None}\n" \
                     f"End Time:        {self.end_time.strftime('%I:%M %p') if self.end_time is not None else None}\n"
        return return_val
