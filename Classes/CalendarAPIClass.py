import datetime
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

from Classes.EventCalendarClass import EventCalendar
import tokens


class CalendarAPI:

    def __init__(self):

        self.scopes = ['https://www.googleapis.com/auth/calendar.readonly']
        self.token_location = 'tokens/calendar-token.pickle'
        self.credentials_location = 'tokens/calendar-credentials.json'
        self.creds = None
        self.service = None
        self.calendars = []

    def start_api(self):
        """
        Starts the Google Calendar API.
        The file token.pickle stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first
        time.

        :return: CalendarAPI
        """
        creds = tokens.read_google_token()

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            else:
                flow = tokens.read_calendar_credentials(self.scopes)
                creds = flow.run_local_server()

            with open(self.token_location, 'wb+') as token:  # Save the credentials for the next run
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)
        return self

    def get_calendars(self):
        """
        Creates and organizes all of the calendars with EventCalendar and then keeps a list of them

        :return: CalendarAPI
        """
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        for calendar_raw in self.service.calendarList().list().execute().get('items'):
            calendar = self.service.events().list(calendarId=calendar_raw.get('id'), timeMin=now, singleEvents=True,
                                                  orderBy='startTime').execute()
            self.calendars.append(EventCalendar(calendar, self.service).organize())
        return self
