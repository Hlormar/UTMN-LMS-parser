import requests
import sys
import json
from datetime import datetime, timedelta


LOGIN_URL = "https://lms.utmn.ru/login/token.php"
CALENDAR_URL = "https://lms.utmn.ru/webservice/rest/server.php"

s = requests.session()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/91.0.4472.124 Safari/537.36"}


def getToken(user, password):  # returns token string
    try:
        r = s.post(
            url = LOGIN_URL,
            json = {"username": user, "password": password, "service": "test"},
            headers = headers)

        token_data = r.json()
        return token_data.get("token", -1)

    # connection problems
    except requests.ConnectionError:
        print("getToken: Connection error")
        return (-1)
    # unknown
    except Exception as e:
        print("getToken:", e)
        return (-1)


def getCalendar(token):  # returns raw calendar response
    try:
        params = {
            'wsfunction': 'core_calendar_get_calendar_upcoming_view',
            'wstoken': token,
            'moodlewsrestformat': 'json'}

        r = s.post(
            url = CALENDAR_URL,
            params = params,
            headers = headers)

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


def formatDict(raw):  # returns json dictioanary
    try:
        raw = raw.replace("\\/", "/")
        null = "null"
        false = "false"
        true = "true"
        return json.loads(raw)

    # no data
    except AttributeError:
        print("formatDict: No data")
        return (-1)
    # invalid JSON
    except json.JSONDecodeError:
        print("formatDict: Invalid JSON format")
        return(-1)
    # unknown
    except Exception as e:
        print("formatDict:", e)
        return (-1)


def buildOutput(calendar):
    # recieves a python dictionary (output of the formatDict())
    try:
        events = calendar.get('events')  # list of a dictionaries
        out = ""
        for event in events:
            start = convertTime(event['timestart'])
            duration = str(timedelta(seconds=event['timeduration']))
            modified = convertTime(event['timemodified'])

            out += (
                f'COURSE:\t\t\t{event["course"]["fullnamedisplay"]}\n'
                f'TASK:\t\t\t{event["name"]}\n'
                f'DESCRIPTION:\t\t{event["description"]}\n'
                f'EVENT TYPE:\t\t{event["eventtype"]}\n'
                f'START TIME:\t\t{start}\n'
                f'DURATION:\t\t{duration}\n'
                f'MODIFICATION DATE:\t{modified}\n'
                f'CALENDAR URL:\t\t{event["viewurl"]}\n'
                f'COURSE URL:\t\t{event["course"]["viewurl"]}\n'
                f'HAS PROGRESS?:\t\t{event["course"]["hasprogress"]}\n'
                f'PROGRESS:\t\t{event["course"]["progress"]}\n\n')
        return out
    except KeyError as ke:
        print("parseValue: Missing key -", ke)
    except TypeError:
        print("parseValue: No data or certain value")
        return (-1)
    except Exception as e:
        print("parseValue:", e)
        return (-1)


def convertTime(timestampStr):
    # replace 01.01.1970 to 0
    if timestampStr == 0:
        return "0"
    return str(datetime.fromtimestamp(int(timestampStr)).strftime("%a, %d %B %Y %H:%M"))


if __name__ == '__main__':
    try:
        token = getToken(sys.argv[1], sys.argv[2])
        if token == -1:
            print("main: Failed to retrieve token")
            exit(-1)
        calendarRaw = getCalendar(token)
        if calendarRaw == -1:
            print("main: Failed to retrieve calendar")
            exit(-1)
        calendarDict = formatDict(getCalendar(token))
        if calendarDict == -1:
            print("main: Failed to format calendar data")
            exit(-1)
        print(buildOutput(calendarDict))

    except IndexError:
        print("main: No credentials")
        exit()
