import requests
import os

s = requests.session()
url = "https://lms.utmn.ru/login/index.php"


def getToken():
    global url
    global s
    return s.get(url).text.split("logintoken")[1][9:39]
    pass


def saveContent(response, filename):
    with open(filename, "w") as f:
        f.write(response.text)
    pass


def openBrowser(filename):
    os.system("librewolf " + filename)
    pass


def updatePayload():
    global payload
    payload['logintoken'] = getToken()
    pass


payload = {
        "logintoken": getToken(),
        "username": "stud@study.utmn.ru",
        "password": "lorem_ipsum"
        }


if __name__ == "__main__":
    # Auth
    r = s.post(url, data=payload, cookies=s.cookies)
    saveContent(r, "response.html")
    openBrowser("response.html")  # Check the result

