import datetime
import pickle
from typing import List

from googleapiclient.discovery import build
from google.auth.transport.requests import Request

from classes.gcal_event import Event
import tokens

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_LOCATION = 'tokens/calendar-token.pickle'
CREDS_LOCATION = 'tokens/calendar-credentials.json'


def get_service():
    """
    Starts the Google Calendar API.
    The file token.pickle stores the user's access and refresh tokens, and is
    created automatically when the authorization flow completes for the first
    time.
    """
    creds = tokens.read_google_token()

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = tokens.read_calendar_credentials(SCOPES)
            creds = flow.run_local_server()

        with open(TOKEN_LOCATION, 'wb+') as token:  # Save the credentials for the next run
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


def get_all_events_until(service, days=0):
    start = datetime.datetime.utcnow()
    end = (start + datetime.timedelta(days=days)).date()
    grouped_events = []

    for calendar_raw in service.calendarList().list().execute().get('items'):
        calendar = service.events().list(calendarId=calendar_raw.get('id'),
                                         timeMin=start.isoformat() + 'Z',
                                         singleEvents=True,
                                         orderBy='startTime').execute()
        for event in calendar['items']:
            event: dict
            has_time = event['start'].get("dateTime") is not None
            event_d = Event(
                calendar_name=calendar["summary"],
                event_name=event['summary'],
                start=datetime.datetime.fromisoformat(event['start']['dateTime'] if has_time else event['start']['date']),
                end=datetime.datetime.fromisoformat(event['end']['dateTime'] if has_time else event['end']['date']),
                has_time=has_time,
                description=event.get('description', "")
            )
            if event_d.start_date <= end:
                if len(grouped_events) == 0:
                    grouped_events.append([event_d])
                elif event_d.start_date == grouped_events[-1][0].start_date:
                    grouped_events[-1].append(event_d)
                else:
                    grouped_events.append([event_d])
    return sorted([sorted(e, key=lambda x: x.start_date) for e in add_empties(grouped_events, start, days)], key=lambda x: x[0].start_date)


def add_empties(grouped_events: List[List[Event]], start: datetime.datetime, days: int):
    empties = [[Event.make_empty(start + datetime.timedelta(days=i))] for i in range(days + 1)]
    for i, empt in enumerate(empties):
        events = list(filter(lambda x: x[0].start_date == empt[0].start_date, grouped_events))
        if events:
            empties[i] = events[0]
    return empties
