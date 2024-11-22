import requests
from datetime import datetime
import sys

s = requests.session()


def getToken(user, password):
    try:
        r = s.post("https://lms.utmn.ru/login/token.php", json={"username": user, "password": password, "service": "test"})
        return r.text.split("token")[1][3:-10]

    # connection problems
    except requests.ConnectionError:
        print("getToken: Connection error")
        return (-1)
    # unknown
    except Exception as e:
        print("getToken:", e)
        return (-1)


def getCalendar(token):
    try:
        r = s.post(url="https://lms.utmn.ru/webservice/rest/server.php?wsfunction=core_calendar_get_calendar_upcoming_view&wstoken=" + token + "&moodlewsrestformat=json")
        return r.text

    # connection problems
    except requests.ConnectionError:
        print("getCalendar: Connection error")
        return (-1)
    # empty token
    except TypeError:
        print("getCalendar: Empty token")
        return (-1)
    # unknown
    except Exception as e:
        print("getCalendar:", e)
        return (-1)


def parseValues(raw):
    try:
        # cut the long base64 image part
        courseIndex = raw.find('"courseimage"')
        progressIndex = raw.find('"progress"')
        while courseIndex != -1:
            raw = raw[:courseIndex] + raw[progressIndex:]
            progressIndex = raw.find('"progress"', courseIndex+1)
            courseIndex = raw.find('"courseimage"')

        # replace \/ with /
        slashIndex = raw.find('\\/')
        while slashIndex != -1:
            raw = raw[:slashIndex] + raw[slashIndex+1:]
            slashIndex = raw.find('\\/', slashIndex+1)

        null = "None"
        false = "False"
        true = "True"
        return (eval(raw))  # returns a dictionary

    # no data
    except AttributeError:
        print("parseValues: No data")
        return (-1)
    # unknown
    except Exception as e:
        print("parseValues:", e)
        return (-1)


if __name__ == '__main__':
    try:
        token = getToken(sys.argv[1], sys.argv[2])
    except IndexError:
        print("main: No credentials")
        exit()

    calendarRaw = getCalendar(token)
    calendar = parseValues(calendarRaw)

    try:
        events = calendar['events']  # an array of a dictionaries
        for event in events:
            # replace 01.01.1970 to 0
            start = event['timestart']
            duration = event['timeduration']
            modified = event['timemodified']

            if start == 0:
                start = '0'
            else:
                start = str(datetime.fromtimestamp(start))
            if duration == 0:
                duration = '0'
            else:
                duration = str(datetime.fromtimestamp(duration))
            if modified == 0:
                modified = '0'
            else:
                modified = str(datetime.fromtimestamp(modified))

            print('COURSE:\t\t' + event['course']['fullnamedisplay'],
                  'TASK:\t\t' + event['name'],
                  'DESCRIPTION:\t\t' + event['description'],
                  'EVENT TYPE:\t\t' + event['eventtype'],
                  'START DATE:\t\t' + start,
                  'DURATION DATE:\t\t' + duration,
                  'MODIFICATION TIME:\t\t' + modified,
                  'CALENDAR URL:\t\t' + event['viewurl'],
                  'COURSE URL:\t\t' + event['course']['viewurl'],
                  'HAS PROGRESS?:\t\t' + event['course']['hasprogress'],
                  'PROGRESS:\t\t' + str(event['course']['progress']),
                  sep='\n', end='\n\n')

    except TypeError:
        print("main: No data or certain value")
