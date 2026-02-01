from .caldav_code import CalDavCalendar
import datetime
from mycroft.util.time import default_timezone
from mycroft.util.parse import extract_datetime, extract_number
from mycroft import MycroftSkill, intent_file_handler
import os
from datetime import timedelta


class SiCalendar(MycroftSkill):
    """
    Contains multiple intent handlers which reflect every skill/feature which our calendar skill should provide.
    Intent and dialog files can be found in the directory /locale/en-us and are connected to each handler.
    """

    def __init__(self):
        MycroftSkill.__init__(self)
        self.caldav_instance = None
        self.timezone = None

    def initialize(self):
        self.timezone = default_timezone()

    @intent_file_handler('connect.calendar.intent')
    def connect_calendar(self, message):
        """
        Creates connection to NextCloud calendar when user calls "Connect my calendar"
        Reads credentials from a text file on the raspberry pi /mycroft-core/credentials
        """
        path = os.path.join(self.file_system.path, "../../../../mycroft-core/credentials")
        path_to_file = os.path.join(path, "nextcloud.txt")
        if os.path.isfile(path_to_file):
            f = open(path_to_file, "r")
            username = f.readline()
            username = username.strip()
            password = f.readline()
            password = password.strip()
        else:
            f = open(path_to_file, "w")
            f.close()
            self.speak_dialog('missing.credentials')

        if not username or not password:
            self.speak_dialog('missing.credentials')
        else:
            self.caldav_instance = CalDavCalendar(username, password)
            self.speak_dialog('connect.successful', {'username': username})
            self.log.info(f"Successfully created CalDavCalendar instance with username {username}")
            self.log.info(self.caldav_instance.calendar)

    @intent_file_handler('calendar.si.next.appointment.intent')
    def get_next_appointment(self, message):
        """
        Handler to get next appointment of the current user.
        """
        event_list, events = self.caldav_instance.fetch_next_n_events(1)
        self.log.info("Next event (list): ", event_list)
        if event_list:
            self.log.info("Summary of next appointment: ", event_list[0].summary)
            date_response = event_list[0].date_response
            self.speak_dialog('calendar.si.next.appointment', {'summary': event_list[0].summary,
                                                               'date_response': date_response})
        else:
            self.speak_dialog('calendar.si.no.planned.events')

    @intent_file_handler('calendar.si.next.appointment.number.intent')
    def get_next_n_appointments(self, message):
        """
        Handler to get the next n appointments of the user.
        e.g. "What are my next six appointments?"
        """
        number = extract_number(message.data.get('number'))
        parsed_events_list, events_list = self.caldav_instance.fetch_next_n_events(number)
        self.log.info(f"Next {number} events (list):  {events_list}")
        if parsed_events_list:
            self.speak_dialog('calendar.si.next.appointment.number', {'number': number})
            for parsed_event in parsed_events_list:
                if parsed_event.time is not None:
                    date_response = f"{parsed_event.time} {parsed_event.date_response}"
                    self.speak_dialog('calendar.si.appointment', {'summary': parsed_event.summary,
                                                                  'date_response': date_response})
                else:
                    self.speak_dialog('calendar.si.appointment', {'summary': parsed_event.summary,
                                                                  'date_response': parsed_event.date_response})
        else:
            self.speak_dialog('calendar.si.no.planned.events')

    @intent_file_handler('calendar.si.appointment.date.intent')
    def get_appointment_date(self, message):
        """
        Handler to get the next appointment on a specific date.
        The given date is parsed with extract_datetime and can be a weekday or a specific date e.g. March, 26th 2022
        """
        self.log.info(f"Calling get_appointment_date")
        input_date = message.data.get('date')
        parsed_date = extract_datetime(input_date)
        while parsed_date is None:
            parsed_date = self.get_response('calendar.si.repeat.date')

        parsed_events, events = self.caldav_instance.fetch_events_for_date(parsed_date[0])
        self.log.info(f"Events on given date: {events}")
        if events:
            self.speak_dialog('calendar.si.appointment.date', {'date': parsed_events[0].date_response})
            for parsed_event in parsed_events:
                if parsed_event.time is not None:
                    self.speak_dialog('calendar.si.appointment', {'summary': parsed_event.summary,
                                                                  'date_response': parsed_event.time})
                else:
                    self.speak_dialog('calendar.si.appointment', {'summary': parsed_event.summary,
                                                                  'date_response': ""})
        else:
            self.speak_dialog('calendar.si.no.planned.events')

    @intent_file_handler('calendar.si.create.event.intent')
    def create_event_mycroft(self, message):
        """
        This method is used to activate the create.event.intent by voice input via Mycroft and execute the dialog
        correctly. The goal is that in the end a new event is created in the connected NextCloud Calendar
        by using caldav based methods.
        It is possible to create a fullday event as well as one for a specific time.
        The attributes title, date, full_day, start_time and end_time can be set by voice input.
        """

        self.log.info("Create_event Dialog startet with message: ", message)
        # asking for the event title
        event_title = self.get_response('calendar.si.ask.title')
        self.log.info(f"Get event title: {event_title}")

        date = None

        # asking for the date when the new event should be created
        while date is None:
            spoken_date = self.get_response('calendar.si.ask.date')
            self.log.info(f"Get Spoken Date: {spoken_date}")
            # extract the datetime with mycrofts extract_datetime() method
            date = extract_datetime(spoken_date, datetime.datetime.today())


        date, date_str = date


        self.log.info(f"Get Parsed Date:{date}")

        # asked if the event should be a fullday event and catch the confirmation
        confirmation_fullday_event = self.ask_yesno('calendar.si.fullday.event')

        # as only yes cannot be used as an Keyboard input, one have to check if it was a yes confirmation or the users keyboard input
        # equals "I confirm"

        if confirmation_fullday_event == 'yes' or confirmation_fullday_event == 'I confirm':
            self.log.info("Fullday Event")
            fullday = True
            begin_time = date
            # calculating end date by adding 1 day for full day event
            end_time = begin_time + timedelta(days=1)

            # create a parsed event object, to use it for the spoken dialog

            events = self.caldav_instance.create_parsed_events(event_title, begin_time, end_time)

            # check if the fullday event should be created

            confirmation = self.ask_yesno('calendar.si.check.event.to.add.fullday',
                                          {'event_title': events[0].summary,
                                           'date_response': events[0].date_response})

        else:
            # if it should not be a fullday event
            fullday = False
            begin_time = None
            end_time = None

            while begin_time is None:
                spoken_begin = self.get_response('calendar.si.ask.begin')
                begin_time = extract_datetime(spoken_begin, date)


            begin_time, begin_str = begin_time

            self.log.info(f"Type of Begin:{type(begin_time)}")
            self.log.info(f"Begin: {begin_time}")

            while end_time is None:
                spoken_end = self.get_response('calendar.si.ask.end')
                end_time = extract_datetime(spoken_end, date)

            end_time, end_str = end_time

            self.log.info(f"End: {end_time}")

            events = self.caldav_instance.create_parsed_events(event_title, begin_time, end_time)

            confirmation = self.ask_yesno('calendar.si.check.event.to.add',
                                          {'event_title': events[0].summary,
                                           'date_response': events[0].date_response,
                                           'time': events[0].time})

        confirm_count = 0

        if confirmation == 'yes' or confirmation == 'I confirm':

            # if confirmation yes => create event in NextCloud Calendar by calling the add_event method
            self.log.info("Create event ")
            self.log.info(f"Type of Begin:{type(begin_time)}")
            self.log.info(f"Type of End:{type(end_time)}")
            self.caldav_instance.add_event(event_title, begin_time, end_time, None, fullday)
            self.speak_dialog('calendar.si.success.add.event')

        elif confirmation == 'no' and confirm_count <= 3:
            self.speak_dialog('calendar.si.no.success.add.event')
            self.create_event_mycroft(message)
            confirm_count += 1

        else:
            self.speak('Sorry i did not understand.')
            self.log.info("I did not catch your answer")

    @intent_file_handler('calendar.si.remove.last.event.intent')
    def remove_last_event_mycroft(self, message):
        """
            Handler to remove the last appointment of the current user
        """
        parsed_events, events = self.caldav_instance.fetch_last_n_events(1)
        if len(events) > 0:
            event = events[0]
            parsed_event = parsed_events[0]
            answer = self.ask_yesno('calendar.si.check.event.to.remove',
                                    {'event_title': parsed_event.summary, 'dateResponse': parsed_event.date_response})
            if answer == "yes" or answer == 'I confirm':
                self.caldav_instance.remove_events([event])
                self.speak_dialog('calendar.si.event.was.removed',
                                  {'event_title': parsed_event.summary, 'dateResponse': parsed_event.date_response})
            else:
                self.speak_dialog('calendar.si.event.was.not.removed')
        else:
            self.speak_dialog('calendar.si.no.planned.events')

    @intent_file_handler('calendar.si.remove.next.event.intent')
    def remove_next_event_mycroft(self, message):
        """
            Handler to remove the next appointment of the current user
        """
        parsed_events, events = self.caldav_instance.fetch_next_n_events(1)
        if len(events) > 0:
            event = events[0]
            parsed_event = parsed_events[0]
            answer = self.ask_yesno('calendar.si.check.event.to.remove',
                                    {'event_title': parsed_event.summary, 'dateResponse': parsed_event.date_response})
            if answer == "yes" or answer == "I confirm":
                self.caldav_instance.remove_events([event])
                self.speak_dialog('calendar.si.event.was.removed',
                                  {'event_title': parsed_event.summary, 'dateResponse': parsed_event.date_response})
            else:
                self.speak_dialog('calendar.si.event.was.not.removed')
        else:
            self.speak_dialog('calendar.si.no.planned.events')

    @intent_file_handler('calendar.si.remove.event.intent')
    def remove_event_date(self, message):
        """
            Handler to remove an appointment of the current user for a specific date
        """
        self.log.info(f"Remove event")

        date = None
        while date is None:
            spoken_date = self.get_response('calendar.si.ask.date.delete')
            self.log.info(f"Get Spoken Date: {spoken_date}")
            date = extract_datetime(spoken_date, datetime.datetime.today())

        date, date_str = date

        self.log.info(f"Get Parsed Date:{date}")
        parsed_events, events = self.caldav_instance.fetch_events_for_date(date)
        self.log.info(f"Events on given date: {events}")
        if events:
            self.speak_dialog('calendar.si.appointment.date', {'date': parsed_events[0].date_response})
            index = 0
            for parsed_event in parsed_events:

                if parsed_event.time is not None:
                    self.speak_dialog('calendar.si.appointment.index', {'summary': parsed_event.summary,
                                                                        'date_response': parsed_event.time,
                                                                        'index': index})
                    index = index + 1
                else:
                    self.speak_dialog('calendar.si.appointment.index', {'summary': parsed_event.summary,
                                                                        'date_response': "",
                                                                        'index': index})
                    index = index + 1
            index = self.get_response('calendar.si.ask.index.delete')
            number = extract_number(index)
            event = events[number]
            parsed_event = parsed_events[number]
            answer = self.ask_yesno('calendar.si.check.event.to.remove',
                                    {'event_title': parsed_event.summary, 'dateResponse': parsed_event.date_response})
            if answer == "yes" or answer == "I confirm":
                self.caldav_instance.remove_events([event])
                self.speak_dialog('calendar.si.event.was.removed',
                                  {'event_title': parsed_event.summary, 'dateResponse': parsed_event.date_response})
            else:
                self.speak_dialog('calendar.si.event.was.not.removed')
        else:
            self.speak_dialog('calendar.si.no.planned.events')

    @intent_file_handler('calendar.si.rename.event.intent')
    def rename_event_date(self, message):
        """
        Handler to rename an existing event in the calendar.
        By saying "Rename event" mycroft will ask about the specific date and list all existing events for this day.
        The user can choose the event by saying the index of the desired event.
        After confirming the new name, the event will be renamed.
        """

        self.log.info(f"Rename event")

        date = None

        # ask for the date, when an event should be updatet

        while date is None:
            spoken_date = self.get_response('calendar.si.ask.date.rename')
            self.log.info(f"Get Spoken Date: {spoken_date}")
            date = extract_datetime(spoken_date, datetime.datetime.today())
            self.log.info(f"Get Parsed Date:{date}")

        # fetch all events for the spoken_date
        date, date_str = date
        parsed_events, events = self.caldav_instance.fetch_events_for_date(date)
        self.log.info(f"Events on given date: {events}")
        if events:
            # mycroft should list all events for the spoken_date by index. So the user can choose the event to rename easily.
            self.speak_dialog('calendar.si.appointment.date', {'date': parsed_events[0].date_response})
            index = 0
            for parsed_event in parsed_events:

                if parsed_event.time is not None:
                    self.speak_dialog('calendar.si.appointment.index', {'summary': parsed_event.summary,
                                                                        'date_response': parsed_event.time,
                                                                        'index': index})
                    index = index + 1
                else:
                    self.speak_dialog('calendar.si.appointment.index', {'summary': parsed_event.summary,
                                                                        'date_response': "",
                                                                        'index': index})
                    index = index + 1

            # asking for the index of the event, which should be renamed
            index = self.get_response('calendar.si.ask.index.rename')
            # extract the number from the index voice input
            number = extract_number(index)
            event = events[number]
            parsed_event = parsed_events[number]

            # check if the right event was chosen to be renamed
            answer = self.ask_yesno('calendar.si.check.event.rename',
                                    {'event_title': parsed_event.summary, 'dateResponse': parsed_event.date_response})
            if answer == "yes" or answer == "I confirm":
                # asking for the new title
                new_title = self.get_response('calendar.si.ask.new.title')

                answer = self.ask_yesno('calendar.si.check.new.title',
                                        {'old_title': parsed_event.summary, 'event_title': new_title})

                if answer == "yes" or answer == "I confirm":
                    self.caldav_instance.rename_event(event, new_title)

                    self.speak_dialog('calendar.si.event.success.renamed')
                else:
                    self.speak_dialog('calendar.si.event.was.not.renamed')
            else:
                self.speak_dialog('calendar.si.event.was.not.renamed')
        else:
            self.speak_dialog('calendar.si.no.planned.events')

    def stop(self):
        pass


def create_skill():
    return SiCalendar()
