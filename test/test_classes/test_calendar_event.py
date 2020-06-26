import sys
import os.path
import datetime

sys.path.append(  # import from 2 directories above
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from classes.gcal_event import Event


def test_make_better___empty_event():
    """
    Tests `Event.make_better()` with a "null" event, e.i. an event that just acts as a placeholder,
    and it only has an individual date. These are so the event list can be complete
    """
    empty_event = Event.make_empty(datetime.datetime(2020, 1, 1))

    assert empty_event.title == "No Events"
    assert empty_event.start == datetime.datetime(2020, 1, 1)
    assert empty_event.start_day == "Wednesday"


def test_make_better___date_event():
    """
    Tests Event.make_better()` with an event that only has a date as opposed to a date and time.
    """
    event_with_date = Event(calendar_name="Test Calendar",
                            event_name="Test Event",
                            start=datetime.datetime(2020, 1, 1, 1),
                            end=datetime.datetime(2020, 1, 2, 1),
                            description="This is an event for testing")

    assert event_with_date.title == "Test Event"
    assert event_with_date.start == datetime.datetime(2020, 1, 1, 1)
    assert event_with_date.start_date == datetime.date(2020, 1, 1)
    assert event_with_date.start_day == "Wednesday"
    assert event_with_date.description == "This is an event for testing"


def test_make_better___datetime_event():
    """
    Tests Event.make_better()` with an event that has a date and time, as opposed to just a date.
    """
    event_with_datetime = Event(calendar_name="Test Calendar",
                                event_name="Test Event",
                                start=datetime.datetime(2020, 1, 1, 1),
                                end=datetime.datetime(2020, 1, 1, 1, 30),
                                has_time=True,
                                description="This is an event for testing")
    assert event_with_datetime.title == "Test Event"
    assert event_with_datetime.start == datetime.datetime(2020, 1, 1, 1)
    assert event_with_datetime.start_time == datetime.time(1)
    assert event_with_datetime.start_date == datetime.date(2020, 1, 1)
    assert event_with_datetime.start_day == "Wednesday"
    assert event_with_datetime.end == datetime.datetime(2020, 1, 1, 1, 30)
    assert event_with_datetime.end_time == datetime.time(1, 30)
    assert event_with_datetime.end_date == datetime.date(2020, 1, 1)
    assert event_with_datetime.end_day == "Wednesday"
    assert event_with_datetime.description == "This is an event for testing"
