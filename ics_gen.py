from icalendar import Calendar, Event
import pytz
from datetime import datetime
import os
from pathlib import Path

def create_ics(data, start_date):
    #times are in UTC
    TIMES_START_HOUR = [16, 18, 20, 23, 2, 5]
    TIMES_START_MINUTE = [0, 30, 30, 0, 30, 0]
    TIMES_END_HOUR = [18, 20, 22, 3, 4, 8]
    TIMES_END_MINUTE = [0, 0, 30, 0, 0, 0]
    ACTIVITIES = ['activity1', 'lunch', 'activity2', 'activity3', 'dinner', 'night']
    DATE = start_date
    count = 0
    day = 0

    cal = Calendar()
    for item in data:
        for activ in ACTIVITIES:
            if item[activ] is None:
                count += 1
                if count % 4 == 0:
                    day += 1
                continue
            else:
                details = item[activ]
                location = details["location"]
                name = details["name"]
                
                event = Event()
                event.add('summary', name)
                event.add('location', location)
                event.add('dtstart', datetime(DATE.year, DATE.month, DATE.day+day, TIMES_START_HOUR[count%6], TIMES_END_MINUTE[count%6], 0, tzinfo=pytz.utc))
                event.add('dtend', datetime(DATE.year, DATE.month, DATE.day+day, TIMES_END_HOUR[count%6], TIMES_END_MINUTE[count%6], 0, tzinfo=pytz.utc))
                cal.add_component(event)
                
                count += 1
                if count % 4 == 0:
                    day += 1
    

    f = open('example.ics', 'wb')
    f.write(cal.to_ical())
    f.close()

if __name__ == "__main__":
    create_ics()
