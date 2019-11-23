import sys
import os.path
import datetime

sys.path.append(  # import from 2 directories above
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from classes.calendar_event import Event

google_doodoo_dict = {
    'start': {
        'date': "2020-01-01",
    },
    'end': {

    },
    'summary': "Test Event",
    "description": "This is an event for testing"
}


def test_make_better___empty_event():
    """
    Tests `Event.make_better()` with a "null" event, e.i. an event that just acts as a placeholder,
    and it only has an individual date. These are so the event list can be complete
    """
    empty_event = Event(calendar_name="Test Calendar",
                        empty=True,
                        date=datetime.datetime(2020, 1, 1).date()
                        ).make_better()
    assert empty_event.title == "No Events"
    assert empty_event.date_time == datetime.datetime(2020, 1, 1)
    assert empty_event.day == "Wednesday"


def test_make_better___date_event():
    """
    Tests Event.make_better()` with an event that only has a date as opposed to a date and time.
    """
    event_with_date = Event(calendar_name="Test Calendar",
                            event_dict=google_doodoo_dict
                            ).make_better()

    assert event_with_date.title == "Test Event"
    assert event_with_date.date_time == datetime.datetime(2020, 1, 1)
    assert event_with_date.date == datetime.datetime(2020, 1, 1).date()
    assert event_with_date.day == "Wednesday"
    assert event_with_date.description == "This is an event for testing"


def test_make_better___datetime_event():
    """
    Tests Event.make_better()` with an event that has a date and time, as opposed to just a date.
    """
    google_doodoo_dict['start'].update({"dateTime": "2020-01-01T01:00:00-05:00"})
    google_doodoo_dict['start']['date'] = None
    google_doodoo_dict.update({'end': {
        "dateTime": "2020-01-01T02:00:00-05:00"}
    }
    )

    event_with_datetime = Event(calendar_name="Test Calendar",
                                event_dict=google_doodoo_dict
                                ).make_better()

    assert event_with_datetime.title == "Test Event"
    assert event_with_datetime.date_time == datetime.datetime(2020, 1, 1, 1, 0, 0)
    assert event_with_datetime.date == datetime.datetime(2020, 1, 1).date()
    assert event_with_datetime.day == "Wednesday"
    assert event_with_datetime.description == "This is an event for testing"
    assert event_with_datetime.end_time == datetime.datetime(2020, 1, 1, 2, 0, 0).time()
