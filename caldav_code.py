import logging
import caldav
from datetime import datetime
from datetime import datetime as dt
from datetime import timedelta
from datetime import timezone
import hashlib
import time


class ParsedEvent:
    """
    This class represents a parsed event. The parsed event objects are used to be able
    to work in Mycroft dialogs with nice, clear attributes for the dialog outputs.
    """

    def __init__(self, summary, start, end):
        self.summary = summary
        self.start = start
        self.end = end
        self.date_response = None
        self.time = None


class CalDavCalendar:
    # set up caldav url https://<Your-Nextcloud-Domain>/remote.php/dav/
    CALDAV_URL = 'https://nextcloud.humanoidlab.hdm-stuttgart.de/remote.php/dav/'
    def __init__(self, username, password):
        self.client = self.create_client(self.CALDAV_URL, username, password)
        self.calendar = self.fetch_calendars(self.client)

    def create_client(self, url, user_name, password):
        """
        This method creates an DAVClient => contains connection details and credentials

        Args :
            :param url: caldav url https://<Your-Nextcloud-Domain>/remote.php/dav/
            :param user_name
            :param password: password

        Returns :
            :return : client
        """
        client = caldav.DAVClient(url=url, username=user_name, password=password)
        return client

    def fetch_calendars(self, client):
        """
        This method fetch principal object and connects to server.
        The principals calendar is fetched. It returns one nextcloud calendar.

        Args:
            :param client: DAVClient

        Returns:
            :return : calendar
        """

        # Fetch principal object, connect to server
        my_principal = client.principal()
        calendar = my_principal.calendars()
        if calendar:

            logging.info(f"Your principal has {len(calendar)} calendars:")
            for c in calendar:
                logging.info(f"- Name: {c.name}  URL: {c.url}")

        else:
            logging.info("Your principal has no calendars")

        return calendar[0]

    def create_event(self, title, begin, end, rule=None, fullday=False):
        """
        Creates an ICal String based on given title, begin, end date and the boolean fullday
        Converts begin and date to local time beforehand to integrate into ical string. The format depends whether it should be
        a fullday event or an event with specific start and end time.
        It is very important that the code for the Ical strings is not changed, because the format has to be exactly how it is,
        for the code to succeed.

        Args:
            :param fullday: Checks if new event should be a full day Event
            :param title: title of the new event
            :param begin: begin datetime of the event
            :param end: end datetime of the event
            :param rule: handles if the event is a series element

        Returns:
            :return: ical string
        """

        tstamp = dt.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%S")  # get current time for timestamp
        _id = hashlib.sha1(bytes(tstamp, 'utf-8')).hexdigest()  # SHA-1 the timestamp to give a unique ID

        if rule is not None:  # by default, no repetition.
            rrule = "FREQ={}\n".format(rule)
        else:
            rrule = ""

        if not fullday:
            start_utc = begin.strftime("%Y%m%dT%H%M%S")
            end_utc = end.strftime("%Y%m%dT%H%M%S")
            s = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Sabre//Sabre VObject 4.3.0//EN
BEGIN:VEVENT
UID:{}
DTSTAMP:{}
DTSTART;TZID=Europe/Berlin:{}        
DTEND;TZID=Europe/Berlin:{}
{}SUMMARY:{}        
END:VEVENT
END:VCALENDAR
"""
        else:
            start_utc = begin.strftime("%Y%m%d")
            end_utc = end.strftime("%Y%m%d")
            s = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Sabre//Sabre VObject 4.3.0//EN
BEGIN:VEVENT
UID:{}
DTSTAMP:{}
DTSTART;VALUE=DATE:{}
DTEND;VALUE=DATE:{}
{}SUMMARY:{}        
END:VEVENT
END:VCALENDAR
"""

        s = s.format(_id, tstamp, start_utc, end_utc, rrule, title)
        logging.info(f"CreateEvent: {s}")
        return s

    def add_event(self, title, begin, end, rule=None, fullday=False):
        """
        This method adds a new event in the connected NextCloud Calendar.
        Args:
            :param fullday: Checks if new event should be a full day Event
            :param title: title of the new event
            :param begin: begin datetime of the event
            :param end: end datetime of the event
            :param rule: handles if the event is an series element
        """
        # create the ical string
        event_string = self.create_event(title, begin, end, rule=rule, fullday=fullday)

        try:
            # send event to Nextcloud calendar
            _ = self.calendar.save_event(event_string)
        except Exception as e:
            logging.error(f"Event could not be created: {e}")

    def remove_events(self, events):
        """
        This method removes events from the NextCloud Calendar.

        Args:
            :param events: a list of events that are removed
        """
        try:
            for event in events:
                event.delete()
                logging.info(f"Your event: {event.data} was deleted")
        except Exception as e:
            logging.error(f"Events could not be deleted: {e}")

    def fetch_events(self, start_time, end_time, reverse_sorted=False):
        """
        This method fetches all events from the NextCloud Calendar in the given time interval.

        Args:
            :param start_time: begin date of the time interval
            :param end_time: end date of the time interval
            :param reverse_sorted: when true the sorting is descending by date

        Returns:
            :return: two lists of sorted events
        """
        logging.info("fetch_events called")
        try:
            events_fetched = self.calendar.date_search(
                start=start_time, end=end_time, expand=True)
            for e in events_fetched:
                logging.info(e.data)
        except:
            logging.info("Your calendar server does apparently not support expanded search")
            events_fetched = self.calendar.date_search(
                start=start_time, end=end_time, expand=False)
            for e in events_fetched:
                logging.info(e.data)

        events = events_fetched
        events = self.get_title_and_time_of_events(events)
        parsed_events = self.create_parsed_date_objects(events, 2)
        sorted_pairs = sorted(zip(parsed_events, events), key=lambda i: datetime.strptime(i[0].start, '%Y%m%dT%H%M%SZ'),
                              reverse=reverse_sorted)
        tuples = zip(*sorted_pairs)
        if len(sorted_pairs) > 0:
            parsed_events, events = [list(tuple) for tuple in tuples]

            logging.info(f"{str(len(events))} events fetched")
            return parsed_events, events
        else:
            logging.info("No events in calender in this time interval")
            return [], []

    def create_datetime_object(self, year, month, day, hour, minute, second):
        tz = timezone(timedelta(hours=0))
        date = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second, tzinfo=tz)
        return date

    def get_title_and_time_of_events(self, events):
        """
        Parses ical string of each event object in events list

        Args:
            :param events: list of events objects

        Returns :
            :return list of events with parsed start, end and summary properties
        """
        parsed_events = []
        for event in events:
            start = None
            end = None
            summary = None

            for line in event.data.split('\n'):
                if "DTSTART" in line:
                    event.start = line.split(":", 1)[1].strip()
                elif "DTEND" in line:
                    event.end = line.split(":", 1)[1].strip()
                elif "SUMMARY" in line:
                    event.summary = line.split(":", 1)[1].strip()
        return events

    def create_parsed_events(self, summary, start_time, end_time):
        start_time = start_time.replace(tzinfo=timezone.utc)
        end_time = end_time.replace(tzinfo=timezone.utc)

        date_start_datetime = start_time.strftime('%Y%m%dT%H%M%SZ')
        date_end_datetime = end_time.strftime('%Y%m%dT%H%M%SZ')
        event = ParsedEvent(summary, date_start_datetime, date_end_datetime)

        parsed_events = self.parse_dates([event])
        parsed_events = self.generate_output_date_string(parsed_events)
        return parsed_events

    def parse_dates(self, events):
        """
        Formats each begin and end string in the event object to a consistent format.
        Full-day-events still need a given time to be able to sort

        Args:
            :param events: list of events

        Returns:
            :return list of events with formatted begin and end date
        """
        for event in events:
            if (len(event.start) == 8) and (len(event.end) == 8):
                event.start = time.strftime('%Y%m%dT%H%M%SZ', time.strptime(event.start, '%Y%m%d'))
                event.end = time.strftime('%Y%m%dT%H%M%SZ', time.strptime(event.end, '%Y%m%d'))
                logging.info(f"Fetch events from {event.start} to {event.end}")
        return events

    def check_ordinal(self, response_string):
        """
        Checks for ordinal numbers in response_string and corrects prefixes

        Args:
            :param response_string: spoken date as string

        Returns :
            :return correct spoken date as string
        """
        if '01th' in response_string:
            response_string = response_string.replace("01th", "1st")
        elif '1th' in response_string:
            response_string = response_string.replace("1th", "1st")
        elif '2th' in response_string:
            response_string = response_string.replace("th", "nd")
        elif '3th' in response_string:
            response_string = response_string.replace("th", "rd")
        return response_string

    def generate_output_date_string(self, events, time_offset=0):
        """
        Iterates through events and computes response_string and eventually a time string for each event.
        The response_string represents the spoken date of the event e.g. "7th of May"
        The time string represents the spoken time of the event e.g. "from 6 pm to 7 pm"

        Args:
            :param events: list of events

        Returns:
            :return list of events with response_string and time properties
        """
        for event in events:
            # if it's a full day event, only return the date (without time!)
            date_start_datetime = datetime.strptime(event.start, '%Y%m%dT%H%M%SZ')
            date_end = time.strptime(event.end, '%Y%m%dT%H%M%SZ')
            date_start = time.strptime(event.start, '%Y%m%dT%H%M%SZ')
            tmp_start = datetime.strptime(event.end, '%Y%m%dT%H%M%SZ') - timedelta(1)
            if tmp_start == date_start_datetime:
                response_string = time.strftime(
                    '%dth of %B', time.localtime(time.mktime(date_start) + 60 * 60 * time_offset))
                response_string = self.check_ordinal(response_string)
                event.date_response = f'on {date_start_datetime.strftime("%A")}, {response_string}'
                event.time = None
            else:
                response_string = time.strftime(
                    '%dth of %B', time.localtime(time.mktime(date_start)))
                start_time = time.strftime(
                    'from %I:%M%p', time.localtime(time.mktime(date_start) + 60 * 60 * time_offset))
                end_time = time.strftime(
                    ' to %I:%M%p', time.localtime(time.mktime(date_end) + 60 * 60 * time_offset))
                response_string = self.check_ordinal(response_string)
                event.date_response = f'on {date_start_datetime.strftime("%A")}, {response_string}'
                event.time = start_time + end_time
        return events

    def fetch_last_n_events(self, n):
        """
            Fetches the last n events from the connected Nextcloud Calendar

        Args:
            :param n: number of events that should be returned

        Returns:
            :return: two lists of events
        """
        logging.info(f"Fetch the next {str(n)} events")
        events_list = []
        parsed_events_list = []
        start_date = datetime.now()
        interval = 100000
        min_end_date = datetime.min + timedelta(interval)
        current_end_date = start_date
        current_start_date = start_date - timedelta(interval)

        # Get the last events for a time interval
        # If n is greater than the count of the fetched events, fetch events from the time interval before
        # Do this until the event count is greater or equals n or until the lowest Date possible
        while current_start_date > min_end_date and len(events_list) < n:
            logging.info(
                f"{str(len(events_list))} event(s) already found from date: {str(current_end_date)} until today")
            parsed_events, events = self.fetch_events(current_start_date, current_end_date, True)
            events_list.extend(events)
            parsed_events_list.extend(parsed_events)
            current_start_date = current_start_date - timedelta(interval)
            current_end_date = current_end_date - timedelta(interval)

        if len(parsed_events_list) >= n:
            # More events were fetched than used
            # Only return the first n events
            logging.info(f"{str(n)} events found.")
            return parsed_events_list[0:n], events_list[0:n]
        elif len(parsed_events_list) > 0:
            # Less events were fetched than the user requested but more than 0
            # Return all fetched events
            logging.info(f"There are only {str(len(parsed_events_list))} events")
            return parsed_events_list, events_list
        else:
            # In the calendar are no events in the past
            # Return empty array
            logging.info("No events were found")
            return [], []

    def rename_event(self, event, new_title):
        """
        Renames existing event

        Args:
            :param event: event to rename
            :param new_title: new title for event
        """
        try:
            old_title = event.vobject_instance.vevent.summary.value
            event.vobject_instance.vevent.summary.value = new_title
            event.save()
            logging.info(f"Renamed {old_title} to {new_title}")
        except:
            logging.error("Could not rename event")

    def create_parsed_date_objects(self, events, time_offset=0):
        parsed_events = []
        for event in events:
            if hasattr(event, 'summary'):
                parsed_event = ParsedEvent(event.summary, event.start, event.end)
                parsed_events.append(parsed_event)

            else:
                parsed_event = ParsedEvent('No Title', event.start, event.end)
                parsed_events.append(parsed_event)

        parsed_events = self.parse_dates(parsed_events)
        parsed_events = self.generate_output_date_string(parsed_events, time_offset)
        return parsed_events

    def fetch_events_for_date(self, date):
        """
        Fetches all events from the connected NextCloud Calendar for a date.

        Args:
            :param date: the date for which the events should be parsed

        Returns:
            :return: two lists of events
        """
        end_date = date + timedelta(hours=23, minutes=59, seconds=59)
        parsed_events, events = self.fetch_events(date, end_date)

        return parsed_events, events

    def fetch_next_n_events(self, n):
        """
        Fetches the next n events from the conntected Nextcloud Calendar

        Args:
            :param n: number of events that should be returned

        Returns:
            :return: two lists of events
        """
        logging.info(f"Fetch the next {str(n)} events")
        events_list = []
        parsed_events_list = []
        start_date = datetime.now()
        interval = 100000
        max_end_date = datetime.max - timedelta(interval)
        current_start_date = start_date
        current_end_date = start_date + timedelta(interval)
        # Get the next events for a time interval
        # If n is greater than the count of the fetched events, fetch events from the next time interval
        # Do this until the event count is greater or equals n or until the highest Date possible
        while current_end_date < max_end_date and len(events_list) < n:
            logging.info(f"{str(len(events_list))} event(s) already found till date: {str(current_end_date)}")
            parsed_events, events = self.fetch_events(current_start_date, current_end_date)
            events_list.extend(events)
            parsed_events_list.extend(parsed_events)
            current_start_date = current_start_date + timedelta(interval)
            current_end_date = current_end_date + timedelta(interval)

        if len(parsed_events_list) >= n:
            # More events were fetched than used
            # Only return the first n events
            logging.info(f"{str(n)} events found.")
            return parsed_events_list[0:n], events_list[0:n]
        elif len(parsed_events_list) > 0:
            # Less events were fetched than the user requested but more than 0
            # Returns all fetched events
            logging.info(f"There are only {str(len(parsed_events_list))} events")
            return parsed_events_list, events_list
        else:
            # In the calendar are no events in the future
            # Return empty array
            logging.info("No events were found")
            return [], []
