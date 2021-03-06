from datetime import datetime as dt, timedelta
import speech_recognition as sr
import json, socket, time, threading, subprocess
from ConnectionHandlerClient import ConnectionHandlerClient

global connection
connection = None

def set_alarm(cmdt):
    # function to set an alarm
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
        date_substitues = {'today': 0, 'tomorrow': 1}
        cuts = []
        day = None
        month = None
        year = None
        # get today's or tommorows date
        for sub, offset in date_substitues.items():
            if sub in cmdt:
                today = dt.today()
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
        # removing unnecessary parts of string
        s = cmdt
        for cut in cuts:
            if cut:
                s = s.replace(cut, ' ')
        return s

    def get_label():
        # extracting label from string
        index = cmdt.find('called')
        if index == -1:
            return None
        label = cmdt[index:]
        label = label.replace('called', ' ')
        return label.strip()

    label = get_label()
    cmdt = cut_command(['set an alarm for', label, 'called', '-'])
    hours, minutes, cuts = get_daytime()
    cuts.extend(['st ','nd ', 'rd ', 'th '])
    cmdt = cut_command(cuts)
    day, month, year, cuts = get_date()
    cmdt = cut_command(cuts)

    no_year = False
    invalid_date = False
    if month == None or day == None:
        invalid_date = True
        today = dt.today()
        year = today.year
        month = today.month
        day = today.day
    elif year == None:
        year = dt.today().year
        no_year = True
    try:
        new_date = dt(year=year, month=month, day=day, hour=hours, minute=minutes)
    except:
        print('Invalid date, please try again')
        play_error_tone()
        return
    if invalid_date and new_date < dt.today():
        new_date += timedelta(days=1)
        day = new_date.day
        month = new_date.month
        year = new_date.year
    if no_year and new_date < dt.today():
        print('wrong year')
        new_date += timedelta(days=365)
        day = new_date.day
        month = new_date.month
        year = new_date.year

    print(f'{hours:02d}:{minutes:02d}\nday: {day}\nmonth: {month}\nyear: {year}\nlabel: {label}')
    data = {'year': year, 'month': month, 'day': day, 'hours': hours, 'minutes': minutes, 'label': label}
    payload = {'type':'alarm', 'data': data}
    send_data(payload)

def take_note(command_text):
    # function to take a note
    data = command_text.replace('take a note', '')
    data = data.strip()
    if data != '':
        payload = {'type':'note', 'data': data}
        send_data(payload)
        return
    print('Empty note, please try again')
    play_error_tone()

def send_data(data):
    # sends collected data to the server
    global connection
    if connection is not None:
        try:
            is_successful = connection.send(data)
            print('Sending')
        except:
            print('SOCKET PING FAILED')
        if not is_successful:
            connection.close()
            print('Restarting connection...')
            connect_server()
    else:
        print('Server is disconnected')

def connect_server():
    #connects application to the server
    global connection
    while True:
        HOST = '127.0.0.1'
        PORT = 22222
        connection = ConnectionHandlerClient(HOST, PORT)
        if not connection.connect():
            connection = None
            print('System could not connect to the server. Waiting 10s...')
            time.sleep(10)
        else:
            print('Connected')
            return

def play_error_tone():
    # plays tone when some error occured
    try:
        subprocess.call(['play', '-nq', '-t', 'alsa', 'synth', '0.3', 'sine', '240'])
    except:
        print("Error sound failed")

def ping_server():
    # sends server loose header every 5s to make sure it is still connected
    global connection
    while True:
        if connection is None:
            return False
        try:
            is_sent = connection.ping()
        except:
            print('SOCKET PING FAILED')
            connect_server()
            continue
        if not is_sent:
            print('PING FAILED. RESTARTING...')
            connect_server()
        time.sleep(5)

r = sr.Recognizer()
commands = {'set an alarm for': set_alarm, 'take a note': take_note}
connect_server()
t_ping = threading.Thread(target=ping_server, args=())
t_ping.daemon = True
t_ping.start()
while True:
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.2)
            print('Listening...')
            audio = r.listen(source)
            print('Got it...')
            text = r.recognize_google(audio)
            print(f'You said: {text}')
            recognizedCommand = False
            for c, fun in commands.items():
                if c in text:
                    recognizedCommand = True
                    fun(text)
            if not recognizedCommand:
                play_error_tone()
                print("Command unrecognised, please try again.")
    except sr.RequestError as e:
        print('Error: ', e)
    except sr.UnknownValueError:
        pass
