import datetime


class Event:
    def __init__(self,
                 calendar_name: str,
                 event_name: str,
                 start: datetime.datetime,
                 end: datetime.datetime,
                 has_time: bool = False,
                 description: str = ""):
        """
        Represents an individual event in a calendar, once make_better() is called it
        organizes all of the dat for easy access

        :param calendar_name: The name of the calendar this event was from
        :type calendar_name: str
        """
        self.calendar_name = calendar_name
        self.title = event_name
        self.start = start
        self.end = end
        self.has_time = has_time
        self.description = description

    @classmethod
    def make_empty(cls, date_time: datetime.datetime):
        date_time = date_time.replace(hour=0, minute=0, second=0, microsecond=0)
        return cls("Empty", "No Events", date_time, date_time + datetime.timedelta(days=1))

    @property
    def start_day(self) -> str:
        return self.start_date.strftime("%A")

    @property
    def end_day(self) -> str:
        return self.end_date.strftime("%A")

    @property
    def start_date(self) -> datetime.date:
        return self.start.date()

    @property
    def start_time(self):
        return self.start.time()

    @property
    def end_date(self):
        return self.end.date()

    @property
    def end_time(self):
        return self.end.time()

    def str(self) -> str:
        if self.has_time:
            string = f"{self.title}\n•  {self.start_time.strftime('%H:%M')} to {self.end_time.strftime('%H:%M')}"
        else:
            string = f"{self.title}"
        if self.description != "":
            return string + "\n•  " + self.description
        return string

    def __repr__(self) -> str:
        """
        Represents all of the data contained in this with some nice formatting

        :return: The str to represent the Event object
        :rtype: str
        """
        return f"\nCalendar:        {self.calendar_name}\n" \
               f"Event Name:      {self.title}\n" \
               f"Description:     {self.description}\n" \
               f"Date:            {self.start_date}\n" \
               f"Day of the Week: {self.start_day}\n" \
               f"Start Time:      {self.start_time}\n" \
               f"End Time:        {self.end_time}\n"
