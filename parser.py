import requests
import sys
from datetime import datetime, timedelta


s = requests.session()


def getToken(user, password):
    try:
        r = s.post(
            "https://lms.utmn.ru/login/token.php",
            json={"username": user, "password": password, "service": "test"})
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
        r = s.post(url="https://lms.utmn.ru/webservice/rest/server.php?\
                wsfunction=core_calendar_get_calendar_upcoming_view&wstoken="
                   + token + "&moodlewsrestformat=json")
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


def formatDict(raw):
    try:
        """# cut the long base64 image part
        courseIndex = raw.find('"courseimage"')
        progressIndex = raw.find('"progress"')
        while courseIndex != -1:
            raw = raw[:courseIndex] + raw[progressIndex:]
            progressIndex = raw.find('"progress"', courseIndex+1)
            courseIndex = raw.find('"courseimage"')"""

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
        print("formatDict: No data")
        return (-1)
    # unknown
    except Exception as e:
        print("formatDict:", e)
        return (-1)


def parseValues(calendar):
    # recieves a python dictionary (output of the formatDict())
    try:
        events = calendar['events']  # an array of a dictionaries
        out = ""
        for event in events:
            start = convertTime(event['timestart'])
            duration = str(timedelta(seconds=event['timeduration']))
            modified = convertTime(event['timemodified'])


            out += ('COURSE:\t\t\t' + event['course']['fullnamedisplay'] +
                  '\nTASK:\t\t\t' + event['name'] +
                  '\nDESCRIPTION:\t\t' + event['description'] +
                  '\nEVENT TYPE:\t\t' + event['eventtype'] +
                  '\nSTART TIME:\t\t' + start +
                  '\nDURATION:\t\t' + duration +
                  '\nMODIFICATION DATE:\t' + modified +
                  '\nCALENDAR URL:\t\t' + event['viewurl'] +
                  '\nCOURSE URL:\t\t' + event['course']['viewurl'] +
                  '\nHAS PROGRESS?:\t\t' + event['course']['hasprogress'] +
                  '\nPROGRESS:\t\t' + str(event['course']['progress']) + "\n\n")
        return out

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
    except IndexError:
        print("main: No credentials")
        exit()
    calendar = formatDict(getCalendar(token))
    print(parseValues(calendar))
