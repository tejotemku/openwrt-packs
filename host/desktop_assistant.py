from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QPushButton, QFrame
import sys, threading, pickle, time
from datetime import datetime as dt, timedelta
from ConnectionHandlerServer import ConnectionHandlerServer

global server
server = None
mutex_server = threading.Lock()

class Window(QMainWindow):
    popup_alarm_signal = pyqtSignal(str)
    remove_signal = pyqtSignal(str)
    add_alarm_signal = pyqtSignal(dict)
    add_note_signal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(QMainWindow, self).__init__(*args, **kwargs)

        # ładowanie danych
        self.alarms, self.notes = self.load_data()
        self.save_data()

        # tworzenie okna i ustawianie stylów
        self.setGeometry(200, 200, 960, 720)
        self.setWindowTitle("Asystent Desktopowy")
        try:
            self.setStyleSheet(open("style.qss", "r").read())
        except:
            raise Exception('style.qss not found')
        # GŁÓWNA RAMA
        frame = QFrame()
        self.setCentralWidget(frame)
        MenuLayout = QtWidgets.QHBoxLayout(frame)
        # menu i rama kontentu w gółwnej ramie
        self.menu = QFrame()
        self.menu.setStyleSheet("padding: 0px; margin: 0px")
        self.menu.setMaximumHeight(self.height())
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("background-color: #e8ebd1")
        self.content = QFrame()
        ContentFrameLayout = QtWidgets.QVBoxLayout(self.content_frame)
        ContentFrameLayout.addWidget(self.content)
        MenuLayout.addWidget(self.menu, 1)
        MenuLayout.addWidget(self.content_frame, 100)

        # MENU
        MenuLayout = QtWidgets.QVBoxLayout(self.menu)
        # notatki
        self.note_list_widget = MenuOptionHiddenList(self, self.notes, "Notatki", self.display_notes)
        MenuLayout.addWidget(self.note_list_widget, 1)
        # alarmy
        self.alarm_list_widget = MenuOptionHiddenList(self, self.alarms.keys(), "Alarmy", self.display_alarms)
        MenuLayout.addWidget(self.alarm_list_widget, 1)
        MenuLayout.addStretch()

        # KONTENT
        ContentLayout = QtWidgets.QVBoxLayout(self.content)
        # zawartość alarmów lub notatek
        self.content_label = QLabel('')
        self.content_label.setAlignment(Qt.AlignTop)
        font = QFont('Times', 18)
        self.content_label.setFont(font)
        ContentLayout.addWidget(self.content_label, 100)
        ContentLayout.addStretch()
        # usuwanie alarmów lub notatek
        self.remove_button = QPushButton("Usuń")
        self.remove_button.clicked.connect(self.remove_selected)
        ContentLayout.addWidget(self.remove_button, 1)

    def start(self):
        self.content.hide()
        self.note_list_widget.hideList()
        self.alarm_list_widget.hideList()
        # signals
        self.popup_alarm_signal[str].connect(self.popup_alarm)
        self.remove_signal[str].connect(self.remove_alarm)
        self.add_alarm_signal[dict].connect(self.add_alarm)
        self.add_note_signal[str].connect(self.add_note)
        # wątek zegara zarządzającego alarmami w tle
        self.start_clock()
        # wątek pobierania danych
        self.start_collector()
        self.show()

    def event(self, event):
        if event.type() == QEvent.Resize:
            self.menu.setMaximumHeight(self.height())
        return super().event(event)

    def popup_alarm(self, label:str=None):
        QtWidgets.QMessageBox.about(self, 'Alarm', label)

    def save_data(self):
        itemlist = {'alarms': self.alarms, 'notes': self.notes}
        with open('outfile', 'wb') as fp:
            pickle.dump(itemlist, fp)

    def load_data(self):
        try:
            with open ('outfile', 'rb') as fp:
                itemlist = pickle.load(fp)
            return itemlist['alarms'], itemlist['notes']
        except:
            return dict(), list()

    def display_alarms(self, alarm_label):
        self.displayed_info_type = 'alarm'
        alarm = self.alarms[alarm_label]
        self.content_label.setText(f"ALARM: \n\ntytuł: {alarm_label}\ndzień - {alarm.day:02d}.{alarm.month:02d}\
.{alarm.year}\ngodzina - {alarm.hour:02d}:{alarm.minute:02d}")
        self.content.show()

    def display_notes(self, notes):
        self.displayed_info_type = 'note'
        self.content_label.setText(f"NOTATKA: \n\n{notes}")
        self.content.show()


    def remove_selected(self):
        try:
            if self.displayed_info_type == 'alarm':
                selected_list_widget = self.alarm_list_widget
                selected_func = self.remove_alarm
            else:
                selected_list_widget = self.note_list_widget
                selected_func = self.remove_note

            selected_item = selected_list_widget.items_list.selectedItems()[0].get_full_text()
            selected_func(selected_item)
        except:
            pass

    def start_clock(self):
        self.clock_thread =threading.Thread(target=clock, args=(self.popup_alarm_signal, self.remove_signal, self.alarms, ))
        self.clock_thread.daemon = True
        self.clock_thread.start()

    def start_collector(self):
        self.collector_thread =threading.Thread(target=collect_data, args=(self.add_alarm_signal, self.add_note_signal, ))
        self.collector_thread.daemon = True
        self.collector_thread.start()

    def restart_collector(self):
        self.collector_thread = None
        self.collector_thread =threading.Thread(target=collect_data, args=(self.add_alarm_signal, self.add_note_signal, ))
        self.collector_thread.daemon = True
        self.collector_thread.start()

    def add_alarm(self, data):
        onlyHour = False
        year = data['year']
        month = data['month']
        day = data['day']
        hours = data['hours']
        minutes = data['minutes']
        label = data['label']
        if month == None:
            onlyHour = True
            today = dt.today()
            year = today.year
            month = today.month
            day = today.day
        new_date = dt(year=year, month=month, day=day, hour=hours, minute=minutes)
        if onlyHour and new_date < dt.today():
            new_date += timedelta(days=1)
        if label == None:
            label = str(new_date)
        self.alarms.update({label: new_date})
        self.alarm_list_widget.newItem(label)
        self.save_data()

    def remove_alarm(self, name):
        self.alarms.pop(name, None)
        self.alarm_list_widget.resetList()
        self.save_data()

    def add_note(self, data):
        self.notes.append(data)
        self.note_list_widget.resetList()
        self.save_data()


    def remove_note(self, name):
        self.notes.remove(name)
        self.note_list_widget.resetList()
        self.save_data()

class MenuOptionHiddenList(QtWidgets.QFrame):
    def __init__(self, window, items, name, func, *args, **kwargs):
        super(MenuOptionHiddenList, self).__init__(*args, **kwargs)
        self.win = window
        self.items = items
        self.layout = QtWidgets.QVBoxLayout(self)
        self.items_btn = QPushButton(name)
        self.items_list = ListWidget(func)
        self.items_list.itemClicked.connect(self.items_list.clicked)
        self.fillList()
        self.setAttribute(Qt.WA_Hover)
        self.items_list.setStyleSheet("background-color: transparent; border: none")
        self.layout.addWidget(self.items_btn)
        self.layout.addWidget(self.items_list)
        self.layout.addStretch()

    def event(self, event):
        if event.type() == QEvent.HoverEnter:
            self.showList()
        elif event.type() == QEvent.HoverLeave:
            self.hideList()
        return super().event(event)

    def fillList(self):
        for i in self.items:
            self.newItem(i)

    def showList(self):
        window_height = self.win.height()
        list_height = min(0.03625 * min(int(0.03125 * window_height), self.items_list.count()) *  window_height, 0.7 * window_height - 65)
        self.items_list.setFixedHeight(int(list_height))
        self.setFixedHeight(65 + self.items_list.height())

    def hideList(self):
        self.items_list.setFixedHeight(0)
        self.setFixedHeight(65)

    def newItem(self, item_data):
        if len(item_data) > 15:
            item_short_name = item_data[:12] + '...'
        else:
            item_short_name =item_data[:15]
        item = ListWidgetItem(item_short_name)
        item.set_full_text(item_data)
        self.items_list.insertItem(0, item)
        self.showList()

    def resetList(self):
        self.items_list.clear()
        self.fillList()

class ListWidgetItem(QtWidgets.QListWidgetItem):
    def set_full_text(self, text):
        self.full_text = text

    def get_full_text(self):
        return self.full_text

class ListWidget(QtWidgets.QListWidget):
    def __init__(self, func, *args, **kwargs):
        super(ListWidget, self).__init__(*args, **kwargs)
        self.func = func

    def clicked(self, item):
        self.func(item.get_full_text())

def clock(func_popup, func_remove, alarm_list):
    pop_list = []
    while True:
        try:
            for p in pop_list:
                alarm_list.pop(p, None)
                func_remove.emit(p)
                pop_list.remove(p)
            for key, value in alarm_list.items():
                if value < dt.today():
                    func_popup.emit(key)
                    pop_list.append(key)
        except:
            pass

#main data collection from the client
def collect_data(func_add_alarm, func_add_note):
    global server
    while True:
        if server is not None and server.get_connection() is not None:
            try:
                received_data = server.receive()
            except:
                exit()
            print(received_data)
            if received_data == {}:
                print("PONGED")
            if 'type' in received_data and 'data' in received_data:
                type = received_data["type"]
                data = received_data["data"]
                if type == 'note':
                    func_add_note.emit(data)
                elif type == 'alarm':
                    func_add_alarm.emit(data)

#starts new server socket
def server_start():
    global server
    HOST = '127.0.0.1'
    PORT = 22222
    print("Starting server...")
    with mutex_server:
        if server is None:
            server = ConnectionHandlerServer(HOST, PORT)
        is_started, addr = server.start()
    print('Connected with: ', addr)
    return is_started

#sends client 1 byte payload every 5s to make sure it is still connected
def ping_client(window):
    global server
    while True:
        if server is None:
            return False
        try:
            is_sent = server.ping()
        except:
            print("SOCKET PING FAILED")
            return
        if not is_sent:
            print("PING FAILED")
            reload_server(window)
        print("PING SUCCESS")
        time.sleep(5)

# responsible for reloading server after connection was lost
def reload_server(window):
    if server_start():
        print("Server restarted")
        window.restart_collector()
        return True
    return False

app = QApplication(sys.argv)
w = Window()
w.start()
server_start()
t_ping = threading.Thread(target=ping_client, args=(w,))
t_ping.daemon = True
t_ping.start()
sys.exit(app.exec_())
