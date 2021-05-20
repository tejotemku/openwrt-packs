from datetime import datetime, timedelta
import speech_recognition as sr
import json
import socket
from ConnectionHandlerClient import ConnectionHandlerClient

connection = None

def set_alarm(cmdt):
    def get_daytime():
        hours = None
        minutes = None
        # sufixes that are responsible for part of day
        sufixes = {'a.m.': 0, 'p.m.': 12, 'in the morning': 0, 'in the evening': 12, 'in the afternoon': 12}
        # parts to cut out of the spoken command
        cuts = []
        # finding daytime represented in hours:minutes format e.g. 10:45, 9:23
        colon_index = cmdt.find(':')
        if colon_index != -1:
            hours = int(cmdt[colon_index - 2 :colon_index])
            minutes = int(cmdt[colon_index + 1 : colon_index + 3])
            cuts.append(cmdt[colon_index - 2 : colon_index + 3])
        # finding daytime represented just by the hour and sufix e.g. 9 p.m.,  4 in the afternoon
        else:
            for suf in sufixes:
                sufix_index = cmdt.find(suf)
                if sufix_index != -1:
                    hours = int(cmdt[sufix_index - 3 :sufix_index])
                    minutes = 0
                    cuts.append(cmdt[sufix_index - 3 :sufix_index])
                    break
        # adding 0 or 12 hours depending of part of the day
        for suf, h in sufixes.items():
            if suf in cmdt:
                hours += h
                cuts.append(suf)
        return hours, minutes, cuts

    def get_date():
        date_substitues = {'today': 0, 'tommorow': 1}
        cuts = []
        day = None
        month = None
        year = None
        # get today's or tommorows date
        for sub, offset in date_substitues.items():
            if sub in cmdt:
                today = datetime.today()
                today += timedelta(days=offset)
                day = today.day
                month = today.month
                year = today.year
                cuts.append(sub)
        # get date represended in format: day(number), month(name), year(number)
        if month == None:
            # get month
            month_words = ['month 0', 'January', 'February', 'March', 'April', 'May', 'June', 'July',
            'August', 'September', 'October', 'November', 'December']
            for m in month_words:
                if m in cmdt:
                    month = month_words.index(m)
                    cuts.append(m)

            # get worded day
            day_words = ['day 0', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh',
            'eight', 'nineth', 'tenth']
            for d in day_words:
                if d in cmdt:
                    day = day_words.index(m)
                    cuts.append(d)

            # get day and year in digits
            numbers = [int(s) for s in cmdt.split() if s.isdigit()]
            for n in numbers:
                if 0 < n < 32:
                    day = n
                if 1970 < n < 3000:
                    year = n
            cuts.append(str(day))
            cuts.append(str(year))
        return day, month, year, cuts

    def cut_command(cuts):
        s = cmdt
        for cut in cuts:
            s = s.replace(cut, ' ')
        return s


    def get_label():
        index = cmdt.find('called')
        if index == -1:
            return None
        label = cmdt[index:]
        label = label.replace('called', '')
        return label.strip()

    label = get_label()
    cmdt = cut_command(['set an alarm for', label, 'called'])
    hours, minutes, cuts = get_daytime()
    cuts.extend(['st of','nd of', 'th of'])
    cmdt = cut_command(cuts)
    day, month, year, cuts = get_date()
    cmdt = cut_command(cuts)
    print(f'{hours:02d}:{minutes:02d}\nday: {day}\nmonth: {month}\nyear: {year}\nlabel: {label}')
    data = {'year': year, 'month': month, 'day': day, 'hours': hours, 'minutes': minutes, 'label': label}
    # TODO: send data
    payload = {'type':'alarm', 'data': data}
    send_data(payload)


def take_note(command_text):
    data = command_text.replace('take a note', '')
    # TODO: send data
    payload = {'type':'note', 'data': data}
    send_data(payload)

def send_data(data):
    print("Sending")
    if connection is not None:
        is_successful = connection.send(data)
        if not is_successful:
            connection.close()
            print("Restarting connection...")
            # connect_server()

def connect_server():
    while True:
        HOST = "127.0.0.1"
        PORT = 22222
        connection = ConnectionHandlerClient(HOST, PORT)
        if not connection.connect():
            print("System could not connect to the server.")
        else:
            return


r = sr.Recognizer()
commands = {'set an alarm for': set_alarm, 'take a note': take_note}
HOST = "127.0.0.1"
PORT = 22222
connection = ConnectionHandlerClient(HOST, PORT)
print(connection.connect())
while True:
    try:
        with sr.Microphone(device_index=0) as source:
            r.adjust_for_ambient_noise(source, duration=0.2)
            print("Listening...")
            audio = r.listen(source)
            print("Got it...")
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            recognizedCommand = False
            for c, fun in commands.items():
                if c in text:
                    recognizedCommand = True
                    fun(text)
            if not recognizedCommand:
                print("Command unrecognised, please try again.")
    except sr.RequestError as e:
        print("Error: ", e)
    except sr.UnknownValueError:
        pass
