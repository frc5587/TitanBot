import datetime


class Event:

    def __init__(self,
                 calendar_name: str = None,
                 event_dict: dict = None,
                 empty: bool = False,
                 date: datetime.date = None):
        """
        Represents an individual event in a calendar, once make_better() is called it
        organizes all of the dat for easy access

        :param calendar_name: The name of the calendar this event was from
        :type calendar_name: str
        :param event_dict: The dictionary that all of the data is stored in
        :type event_dict: dict
        """
        self.calendar_name = calendar_name
        self.event_dict = event_dict
        self.empty = empty
        self.date = date  # datetime.datetime
        self.day = None  # str
        self.title = None  # str
        self.description = None  # str
        self.end_time = None  # datetime.time
        self.start_time = None  # datetime.time
        self.date_time = None  # datetime.datetime

    def make_better(self):
        """
        Changes the DooDoo style Google event dicts into some nice OOP for your convenience
        """
        if self.empty:

            self.title = "No Events"
            self.date_time = datetime.datetime(self.date.year, self.date.month,
                                               self.date.day)
            self.day = self.date.strftime('%A')
            return self

        self.date = self.event_dict.get('start').get('date')

        if self.date is not None:

            self.title = self.event_dict.get("summary")  # title of event
            self.date_time = datetime.datetime.strptime(self.event_dict.get('start').get('date'),
                                                        '%Y-%m-%d')
            self.date = self.date_time.date()
            self.day = self.date.strftime("%A")
            self.description = self.event_dict.get("description")

        else:

            self.title = self.event_dict.get("summary")  # title of event
            self.date_time = datetime.datetime.strptime(
                self.event_dict.get('start').get('dateTime')[:19],
                '%Y-%m-%dT%X')
            self.date = self.date_time.date()
            self.day = self.date.strftime("%A")
            self.description = self.event_dict.get("description")

            self.start_time = self.date_time.time()
            self.end_time = datetime.datetime.strptime(
                self.event_dict.get('end').get('dateTime')[11:19], "%X").time()

        return self

    def __repr__(self) -> str:
        """
        Represents all of the data contained in this with some nice formatting

        :return: The str to represent the Event object
        :rtype: str
        """
        date = self.date.strftime('%x')
        day = self.date.strftime('%A')
        start_time = self.start_time.strftime(
            '%I:%M %p') if self.start_time is not None else None
        end_time = self.end_time.strftime(
            '%I:%M %p') if self.end_time is not None else None

        return f"Calendar:        {self.calendar_name}\n" \
               f"Event Name:      {self.title}\n" \
               f"Description:     {self.description}\n"\
               f"Date:            {date}\n" \
               f"Day of the Week: {day}\n" \
               f"Start Time:      {start_time}\n" \
               f"End Time:        {end_time}\n"
