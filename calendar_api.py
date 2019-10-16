"""
this handles all interactions the google calendar api, and sorting the events that follow
"""
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

date_dict = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}


def date_finder(date_num):
    """
    returns the name of the day of the week

    :param date_num: int (0-6)
    :return: str
    """
    return date_dict.get(date_num)


def setup():
    """
    starts up the api

    :return: build object
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('tokens/calendar-token.pickle'):
        with open('tokens/calendar-token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'tokens/calendar-credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('tokens/calendar-token.pickle', 'wb+') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def call_api(service):  # Call the Calendar API
    """
    Calls the calendar api, iterates thought the calendars, and gets the events. It gets the date, name, and time of
    the events, and goes through a ridiculous amount of ".get()"s (thanks google!)

    :param service: build object
    :return: list, dict
    """
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    event_list = []
    event_list2 = []
    events = None
    for i in service.calendarList().list().execute().get('items'):
        events_result = service.events().list(calendarId=i.get('id'), timeMin=now, singleEvents=True, orderBy='startTime').execute()  # grabs events from one calendar at a time
        event_list.append(events_result)
        events = events_result.get('items', [])  # get events in the calendar
        for event in events:
            if event.get('start').get('date') is not None:
                event_list2.append({'date': datetime.datetime.strptime(event.get('start').get('date'), '%Y-%m-%d').strftime("%m/%d/%Y"),  # just appends all of the important data
                                    'day': date_finder(datetime.datetime.strptime(event.get('start').get('date'), '%Y-%m-%d').weekday()),
                                    'real_event': event.get('summary'),
                                    'time': None})
            else:
                event_list2.append({'date': datetime.datetime.strptime(event.get('start').get('dateTime')[:10], '%Y-%m-%d').strftime("%m/%d/%Y"),  # just appends all of the important data
                                    'day': date_finder(datetime.datetime.strptime(event.get('start').get('dateTime')[:10], '%Y-%m-%d').weekday()),
                                    'real_event': event.get('summary'),
                                    'start': event.get('start').get('dateTime')[11:16],
                                    'end': event.get('end').get('dateTime')[11:16]})
    return event_list2, events


def main(days, today):
    """
    First it sets up the api, then it gets the events from it, organizes the events by date, checks if they fall within
    the dates that it is looking for, returns the events that are happening in the next <days> days

    :param days: int
    :param today: bool
    :return: list
    """
    try:
        service = setup()  # sets up google api service
        event_dict, events = call_api(service)  # returns organized nested dicts
        if not events:
            return False
        event_dict.sort(key=lambda x: datetime.datetime.strptime(x['date'], "%m/%d/%Y"))  # sorts events by date
        final_events = []
        for event in event_dict:
            if today:
                if datetime.datetime.strptime(event.get('date'), "%m/%d/%Y").date() == datetime.datetime.today().date():  # checks if event is happening today (EST)
                    final_events.append(event)
            else:
                if datetime.datetime.strptime(event.get('date'), '%m/%d/%Y').date() <= \
                        datetime.datetime.today().date() + datetime.timedelta(days=days):   # checks if event is within the days param
                    final_events.append(event)
        return final_events
    except Exception as EE:
        print(EE)
