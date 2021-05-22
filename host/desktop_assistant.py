from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QPushButton, QFrame
import sys, threading, pickle
from datetime import datetime as dt, timedelta
from ConnectionHandlerServer import ConnectionHandlerServer

server = None

class Window(QMainWindow):
    popup_alarm_signal = pyqtSignal(str)
    remove_signal = pyqtSignal(int)
    add_alarm_signal = pyqtSignal(dict)
    add_note_signal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(QMainWindow, self).__init__(*args, **kwargs)

        # loading data
        self.alarms, self.notes = self.load_data()
        self.save_data()

        # generating window and loading style sheet
        self.setGeometry(200, 200, 960, 720)
        self.setWindowTitle("Asystent Desktopowy")
        self.setStyleSheet(open("style.qss", "r").read())

        # MAIN FRAME
        frame = QFrame()
        self.setCentralWidget(frame)
        menu_layout = QtWidgets.QHBoxLayout(frame)
        # menu and content frame in window space
        self.menu = QFrame()
        self.menu.setStyleSheet("padding: 0px; margin: 0px")
        self.menu.setMaximumHeight(self.height())
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("background-color: #e8ebd1")
        self.content = QFrame()
        content_frame_layout = QtWidgets.QVBoxLayout(self.content_frame)
        content_frame_layout.addWidget(self.content)
        menu_layout.addWidget(self.menu, 1)
        menu_layout.addWidget(self.content_frame, 100)

        # MENU
        menu_layout = QtWidgets.QVBoxLayout(self.menu)
        # notes
        self.note_list_widget = MenuOptionHiddenList(self, "notes", self.notes, "Notes", self.display_notes)
        menu_layout.addWidget(self.note_list_widget, 1)
        # alarms
        self.alarm_list_widget = MenuOptionHiddenList(self, "alarms",self.alarms, "Alarms", self.display_alarms)
        menu_layout.addWidget(self.alarm_list_widget, 1)
        menu_layout.addStretch()
        # server connection indicator
        indicator_layout_frame = QFrame()
        indicator_layout = QtWidgets.QHBoxLayout(indicator_layout_frame)
        server_connection_label = QLabel("Server connection status: ")
        self.server_connection_indicator = QLabel()
        font = QFont('Times', 18)
        self.server_connection_indicator.setFont(font)
        self.server_connection_indicator.setText("⬤")
        indicator_layout.addWidget(server_connection_label)
        indicator_layout.addWidget(self.server_connection_indicator)
        menu_layout.addWidget(indicator_layout_frame)

        # CONTENT
        content_layout = QtWidgets.QVBoxLayout(self.content)
        # frame to display alarm's or note's content
        self.content_label = QLabel('')
        self.content_label.setAlignment(Qt.AlignTop)
        font = QFont('Times', 18)
        self.content_label.setFont(font)
        self.content_label.setWordWrap(True)
        content_layout.addWidget(self.content_label, 100)
        content_layout.addStretch()
        # deleting alarms or notes
        self.remove_button = QPushButton("Delete")
        self.remove_button.clicked.connect(self.remove_selected)
        content_layout.addWidget(self.remove_button, 1)

    def start(self):
        # preparing GUI
        self.hide_content()
        self.note_list_widget.hide_list()
        self.alarm_list_widget.hide_list()
        # signals
        self.popup_alarm_signal[str].connect(self.popup_alarm)
        self.remove_signal[int].connect(self.remove_alarm)
        self.add_alarm_signal[dict].connect(self.add_alarm)
        self.add_note_signal[str].connect(self.add_note)
        # background clock thread
        self.start_clock()
        # data collection thread
        self.start_collector()
        # server connection indicator reset
        self.server_not_connected()
        self.show()

    def event(self, event):
        # window resize handling
        if event.type() == QEvent.Resize:
            self.menu.setMaximumHeight(self.height())
        return super().event(event)

    def popup_alarm(self, label:str=None):
        # creating a popup window with an alarm
        QtWidgets.QMessageBox.about(self, 'Alarm', label)

    def save_data(self):
        # saving data to file
        itemlist = {'alarms': self.alarms, 'notes': self.notes}
        with open('data', 'wb') as fp:
            pickle.dump(itemlist, fp)

    def load_data(self):
        # loading data from file
        try:
            with open ('data', 'rb') as fp:
                itemlist = pickle.load(fp)
            return itemlist['alarms'], itemlist['notes']
        except:
            return dict(), dict()

    def display_alarms(self, id):
        # displaying info about alarm in content frame
        self.displayed_info_type = 'alarm'
        alarm = self.alarms[id]['date']
        alarm_label= self.alarms[id]['label']
        self.content_label.setText(f"ALARM: \n\ntytuł: {alarm_label}\ndzień - {alarm.day:02d}.{alarm.month:02d}\
.{alarm.year}\ngodzina - {alarm.hour:02d}:{alarm.minute:02d}")
        self.content.show()

    def display_notes(self, id):
        # displaying a note in content frame
        self.displayed_info_type = 'note'
        self.content_label.setText(f"NOTATKA: \n\n{self.notes[id]}")
        self.content.show()


    def remove_selected(self):
        # remove currently selected alarm or note
        try:
            if self.displayed_info_type == 'alarm':
                selected_list_widget = self.alarm_list_widget
                selected_func = self.remove_alarm
            else:
                selected_list_widget = self.note_list_widget
                selected_func = self.remove_note

            selected_item = selected_list_widget.items_list.selectedItems()[0].get_full_data()
            selected_func(selected_item)
        except:
            pass

    def start_clock(self):
        # starting background clock thread that manages alarms
        self.clock_thread = threading.Thread(target=clock, args=(self.popup_alarm_signal, self.remove_signal, self.alarms, ))
        self.clock_thread.daemon = True
        self.clock_thread.start()

    def start_collector(self):
        # starting data collecion thread
        self.collector_thread = threading.Thread(target=collect_data, args=(self.add_alarm_signal, self.add_note_signal, ))
        self.collector_thread.daemon = True
        self.collector_thread.start()

    def add_alarm(self, data):
        # reating a alarm and saving to file
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
        if self.alarms.keys():
            id = max(self.alarms.keys()) + 1
        else:
            id = 1
        self.alarms.update({id: {'label':label, 'date': new_date}})
        self.alarm_list_widget.reset_list()
        self.save_data()

    def remove_alarm(self, id):
        # removing an alarm from aplication and file
        self.alarms.pop(id, None)
        self.alarm_list_widget.reset_list()
        self.hide_content()
        self.save_data()

    def add_note(self, data):
        # creating a note and saving to file
        if self.notes.keys():
            id = max(self.notes.keys()) + 1
        else:
            id = 1
        self.notes.update({id: data})
        self.note_list_widget.reset_list()
        self.save_data()


    def remove_note(self, id):
        # removing a note from aplication and file
        self.notes.pop(id, None)
        self.note_list_widget.reset_list()
        self.hide_content()
        self.save_data()

    def hide_content(self):
        # clearing the content 
        self.content_label.setText("")
        self.content.hide()

    def server_not_connected(self):
        # changing server connection indicator to red
        self.server_connection_indicator.setStyleSheet("color: #800000")

    def server_connected(self):
         # changing server connection indicator to green
        self.server_connection_indicator.setStyleSheet("color: green")
        
        

class MenuOptionHiddenList(QtWidgets.QFrame):
    # custom list viewer
    def __init__(self, window, type, items, name, func, *args, **kwargs):
        super(MenuOptionHiddenList, self).__init__(*args, **kwargs)
        self.win = window
        self.type = type
        self.items = items
        self.layout = QtWidgets.QVBoxLayout(self)
        self.items_btn = QPushButton(name)
        self.items_list = ListWidget(func)
        self.items_list.itemClicked.connect(self.items_list.clicked)
        self.fill_list()
        self.setAttribute(Qt.WA_Hover)
        self.items_list.setStyleSheet("background-color: transparent; border: none")
        self.layout.addWidget(self.items_btn)
        self.layout.addWidget(self.items_list)
        self.layout.addStretch()

    def event(self, event):
        # handling QEvents
        if event.type() == QEvent.HoverEnter:
            self.show_list()
        elif event.type() == QEvent.HoverLeave:
            self.hide_list()
        return super().event(event)

    def fill_list(self):
        # add items to list widget
        for i in self.items:
            self.new_item(i)

    def show_list(self):
        # display list content
        window_height = self.win.height()
        list_height = min(0.03625 * min(int(0.03125 * window_height), self.items_list.count()) *  window_height, 0.7 * window_height - 65)
        self.items_list.setFixedHeight(int(list_height))
        self.setFixedHeight(65 + self.items_list.height())

    def hide_list(self):
        # hide list content
        self.items_list.setFixedHeight(0)
        self.setFixedHeight(65)

    def new_item(self, item_id):
        # add new item to list and show new list
        if self.type == 'alarms':
            item_dict = self.items[item_id]
            label = item_dict['label']
        elif self.type == 'notes':
            label = self.items[item_id]
        if len(label) > 24:
            item_short_name = label[:21] + '...'
        else:
            item_short_name = label[:24]
        item = ListWidgetItem(item_short_name)
        item.set_full_data(item_id)
        self.items_list.insertItem(0, item)
        self.show_list()

    def reset_list(self):
        # reset item list content
        self.items_list.clear()
        self.fill_list()

class ListWidgetItem(QtWidgets.QListWidgetItem):
    # custom ListWidgetItem that holds additional data
    def set_full_data(self, data):
        # add aditional data
        self.full_data = data

    def get_full_data(self):
        # get data that Item holds
        return self.full_data

class ListWidget(QtWidgets.QListWidget):
    # custom ListWidgetItemWidget which Items call function 
    def __init__(self, func, *args, **kwargs):
        super(ListWidget, self).__init__(*args, **kwargs)
        self.func = func

    def clicked(self, item):
        # Item call function and pass its data
        self.func(item.get_full_data())

def clock(func_popup, func_remove, alarm_list):
    # background clock that manages alarms
    pop_list = []
    while True:
        try:
            for p in pop_list:
                alarm_list.pop(p, None)
                func_remove.emit(p)
                pop_list.remove(p)
            for key, value in alarm_list.items():
                if value['date'] < dt.today():
                    func_popup.emit(value['label'])
                    pop_list.append(key)
        except:
            pass

def collect_data(func_add_alarm, func_add_note):
    # listen and collect data from server
    while True:
        if server.get_connection() is not None:
            try:
                received_data = server.receive()
            except:
                exit()
            print(received_data)
            if 'type' in received_data and 'data' in received_data:
                type = received_data["type"]
                data = received_data["data"]
                if type == 'note':
                    func_add_note.emit(data)
                elif type == 'alarm':
                    func_add_alarm.emit(data)

HOST = '127.0.0.1'
PORT = 22222
server = ConnectionHandlerServer(HOST, PORT)
is_started, addr = server.start()
print('Connected with: ', addr)
server_connection = server.get_connection()
app = QApplication(sys.argv)
w = Window()
w.start()
sys.exit(app.exec_())
