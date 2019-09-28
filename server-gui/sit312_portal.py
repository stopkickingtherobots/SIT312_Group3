# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sit312-portal.ui',
# licensing of 'sit312-portal.ui' applies.
#
# Created: Thu Sep  5 20:37:02 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets
from PySide2.QtCore import QFile, QThread, Signal, Slot, QObject
import server_gui_helper_functions as helper
import datetime
import time
import sys
import os
from dataclasses import dataclass
from multiprocessing import Process, Queue
import queue
from pygame.mixer import music as pygame_music
import pygame

@dataclass
class Data_Segment:
    data_type: str
    data: str

class Ui_MainWindow(object):

    def __init__(self, device_db, message_db, audio_sent_db, audio_recv_db, audio_queue_out, audio_queue_in, message_queue):
        self.device_db = device_db
        self.message_db = message_db
        self.audio_sent_db = audio_sent_db
        self.audio_recv_db = audio_recv_db
        
        self.device_db_rows = len(device_db)
        self.message_db_rows = len(message_db)
        self.audio_sent_db_rows = len(audio_sent_db)
        self.audio_recv_db_rows = len(audio_recv_db)
        self.message_queue = message_queue
        self.audio_queue_out = audio_queue_out
        self.is_recording = False # Flag for Stop btn operation
        self.is_playing = False
        self.recorded = False
        self.file_to_play = None
        self.cell_clicked_text = None
        
    def update_message_tab(self):

        for i in range(0, self.message_db_rows):

            db_item = self.message_db.get(doc_id= i + 1)
            date_time = db_item.get('datetime')
            datetime_utc = datetime.datetime.utcfromtimestamp(float(date_time))
            time_string = datetime_utc.strftime('%H:%M:%S %d/%m/%Y')           

            item = QtWidgets.QTableWidgetItem()
            item.setText(QtWidgets.QApplication.translate("MainWindow", db_item.get('device_id'), None, -1))
            self.tableWidget.setItem(i, 0, item)

            item = QtWidgets.QTableWidgetItem()
            item.setText(QtWidgets.QApplication.translate("MainWindow", time_string, None, -1))
            self.tableWidget.setItem(i, 1, item)   

            item = QtWidgets.QTableWidgetItem()
            item.setText(QtWidgets.QApplication.translate("MainWindow", db_item.get('message'), None, -1))
            self.tableWidget.setItem(i, 2, item)
        
        for i in range(0, self.device_db_rows):

            db_item = self.device_db.get(doc_id= i + 1)

            self.comboBox.setItemText(i, QtWidgets.QApplication.translate("MainWindow", db_item.get('device_id'), None, -1))

        return ''

    def update_record_tab(self):
        for i in range(0, self.device_db_rows):

            db_item = self.device_db.get(doc_id= i + 1)
            self.comboBox_3.addItem('')

            self.comboBox_3.setItemText(i, QtWidgets.QApplication.translate("MainWindow", db_item.get('device_id'), None, -1))

    
    def update_admin_tab(self):

        for i in range(0, self.device_db_rows):

            db_item = self.device_db.get(doc_id= i + 1)

            item = QtWidgets.QTableWidgetItem()
            item.setText(QtWidgets.QApplication.translate("MainWindow", db_item.get('device_id'), None, -1))
            self.tableWidget_2.setItem(i, 0, item)

            item = QtWidgets.QTableWidgetItem()
            item.setText(QtWidgets.QApplication.translate("MainWindow", db_item.get('name'), None, -1))
            self.tableWidget_2.setItem(i, 1, item)   

            item = QtWidgets.QTableWidgetItem()
            item.setText(QtWidgets.QApplication.translate("MainWindow", db_item.get('notes'), None, -1))
            self.tableWidget_2.setItem(i, 2, item)

        return ''

    def update_map_tab(self):

        # To do

        return ''

    def update_audio_tab(self):

        for i in range(0, self.audio_sent_db_rows):

            db_item = self.audio_sent_db.get(doc_id= i + 1)

            date_time = db_item.get('datetime')
            datetime_utc = datetime.datetime.utcfromtimestamp(float(date_time))
            time_string = datetime_utc.strftime('%H:%M:%S %d/%m/%Y')           

            item = QtWidgets.QTableWidgetItem()
            item.setText(db_item.get('device_id'))
            self.tableWidget_3.setItem(i, 0, item)

            item = QtWidgets.QTableWidgetItem()
            item.setText(time_string)
            self.tableWidget_3.setItem(i, 1, item)
            #print('cell datetime: {0:}'.format(item.text()))   

            item = QtWidgets.QTableWidgetItem()
            item.setText(db_item.get('filename'))
            self.tableWidget_3.setItem(i, 2, item)
            #print('cell filename: {0:}'.format(item.text()))

            item = QtWidgets.QTableWidgetItem()
            item.setText(db_item.get('description'))
            self.tableWidget_3.setItem(i, 3, item)

        for i in range(0, self.audio_recv_db_rows):

            db_item = self.audio_recv_db.get(doc_id= i + 1)

            date_time = db_item.get('datetime')
            datetime_utc = datetime.datetime.utcfromtimestamp(float(date_time))
            time_string = datetime_utc.strftime('%H:%M:%S %d/%m/%Y')           

            item = QtWidgets.QTableWidgetItem()
            item.setText(QtWidgets.QApplication.translate("MainWindow", db_item.get('device_id'), None, -1))
            self.tableWidget_4.setItem(i, 0, item)

            item = QtWidgets.QTableWidgetItem()
            item.setText(QtWidgets.QApplication.translate("MainWindow", time_string, None, -1))
            self.tableWidget_4.setItem(i, 1, item)   

            item = QtWidgets.QTableWidgetItem()
            item.setText(QtWidgets.QApplication.translate("MainWindow", db_item.get('filename'), None, -1))
            self.tableWidget_4.setItem(i, 2, item)

            item = QtWidgets.QTableWidgetItem()
            item.setText(QtWidgets.QApplication.translate("MainWindow", db_item.get('description'), None, -1))
            self.tableWidget_4.setItem(i, 3, item)
        
        return ''

    def insert_message(self, MainWindow, device_id, date_time, message):
        datetime_utc = datetime.datetime.utcfromtimestamp(date_time)
        time_string = datetime_utc.strftime('%H:%M:%S %d/%m/%Y')
        # Insert message (id: datetime: message: )
        item = QtWidgets.QTableWidgetItem()
        item.setText(QtWidgets.QApplication.translate("MainWindow", device_id, None, -1))
        self.tableWidget.setItem(self.message_db_rows - 1, 0, item)

        item = QtWidgets.QTableWidgetItem()
        item.setText(QtWidgets.QApplication.translate("MainWindow", time_string, None, -1))
        self.tableWidget.setItem(self.message_db_rows - 1, 1, item)   

        item = QtWidgets.QTableWidgetItem()
        item.setText(QtWidgets.QApplication.translate("MainWindow", message, None, -1))
        self.tableWidget.setItem(self.message_db_rows - 1, 2, item)

        data_segment = Data_Segment('message', device_id + ',' + str(date_time) + ',' + message)
        #msg_string = device_id + ',' + str(date_time) + ',' + message
        self.publish_message(data_segment)

        return ''

    def publish_message(self, data_segment):
        self.message_queue.put(data_segment)

    def insert_distress_message(self, distress_msg):

        msg_arr = distress_msg.data.split(',')
        device_id = msg_arr[0]
        date_time = msg_arr[1]
        lat_gps = msg_arr[2]
        lon_gps = msg_arr[3]
        datetime_utc = datetime.datetime.utcfromtimestamp(float(date_time))
        time_string = datetime_utc.strftime('%H:%M:%S %d/%m/%Y')

        message =  device_id + ' sent distress from: LAT: ' + lat_gps + ' LON: ' + lon_gps + ' at: ' + time_string
        index = helper.insert_message(self.message_db, 'HOME BASE', date_time, message)  

        self.message_db_rows = index + 1    
        self.tableWidget.setRowCount(self.message_db_rows)

        item = QtWidgets.QTableWidgetItem()
        item.setText(QtWidgets.QApplication.translate("MainWindow", 'HOME BASE', None, -1))
        item.setBackgroundColor('red')
        self.tableWidget.setItem(self.message_db_rows - 1, 0, item)

        item = QtWidgets.QTableWidgetItem()
        item.setText(QtWidgets.QApplication.translate("MainWindow", time_string, None, -1))
        item.setBackgroundColor('red')
        self.tableWidget.setItem(self.message_db_rows - 1, 1, item)   

        item = QtWidgets.QTableWidgetItem()
        item.setText(QtWidgets.QApplication.translate("MainWindow", message, None, -1))
        item.setBackgroundColor('red')
        self.tableWidget.setItem(self.message_db_rows - 1, 2, item)

        self.tabWidget.setCurrentIndex(2)

        return ''

    def insert_device(self, MainWindow, device_id, name, notes):
        item = QtWidgets.QTableWidgetItem()
        item.setText(QtWidgets.QApplication.translate("MainWindow", device_id, None, -1))
        self.tableWidget_2.setItem(self.device_db_rows - 1, 0, item)

        item = QtWidgets.QTableWidgetItem()
        item.setText(QtWidgets.QApplication.translate("MainWindow", name, None, -1))
        self.tableWidget_2.setItem(self.device_db_rows - 1, 1, item)   

        item = QtWidgets.QTableWidgetItem()
        item.setText(QtWidgets.QApplication.translate("MainWindow", notes, None, -1))
        self.tableWidget_2.setItem(self.device_db_rows - 1, 2, item)
        
    def enrol_device(self, window):
        device_id = self.comboBox_2.currentText()
        name = self.plainTextEdit_3.toPlainText()
        notes = self.plainTextEdit_4.toPlainText()
        index = helper.insert_device(self.device_db, device_id, name, notes)
        self.device_db_rows = index + 1
        self.tableWidget_2.setRowCount(self.device_db_rows)
        self.insert_device(self, device_id, name, notes)

    def recorder_record_click(self):

        if not self.recorded:
            record_file = helper.record_10_seconds()

            self.current_recording = record_file # = record_obj

            self.recorded = True

        else:
            self.recorder_reset_click()
            record_file = helper.record_10_seconds()

            self.current_recording = record_file # = record_obj

            self.recorded = True

    def recorder_stop_click(self):
        if self.recorded:
            # Probably not required
            return ''

    def recorder_play_click(self):
        if self.file_to_play is not None:
            pygame.mixer.pre_init(48000,-16,2, 1024)
            pygame.mixer.init()
            pygame.mixer.music.load(self.file_to_play)
            pygame.mixer.music.play()
            self.is_playing = True
            self.cell_clicked_text = False

        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            # Set text 'Play'

        elif not self.is_playing:
            pygame.mixer.pre_init(48000,-16,2, 1024)
            pygame.mixer.init()
            pygame.mixer.music.load(self.current_recording)
            pygame.mixer.music.play()
            self.is_playing = True
            # Set text 'Pause'

    def recorder_reset_click(self):
        self.is_playing = False
        self.is_recording = False
        self.recorded = False
        self.file_to_play = None
        pygame.mixer.pre_init(48000,-16,2, 1024)
        pygame.mixer.init()
        try:
            pygame.mixer.music.unload()
        except AttributeError:
            pass

    def recorder_cancel_click(self):
        self.file_to_play = None
        self.is_playing = False
        self.is_recording = False
        self.recorded = False
        try:
            pygame.mixer.music.unload()
        except AttributeError:
            pass
        # tab switch
        self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.tab_4))

        # recorder tab cancel
        self.tabWidget.setTabEnabled(self.tabWidget.indexOf(self.tab_5), False)

    def recorder_send_click(self):

        if self.recorded:
            self.file_to_play = None
            self.is_playing = False
            self.is_recording = False
            try:
                pygame.mixer.music.unload()
            except pygame.error:
                pass
            except AttributeError:
                pass

            device_id = self.comboBox_3.currentText()
            description = self.plainTextEdit_5.toPlainText()
            x = self.current_recording.split('/')
            filename = x[1]
            y = filename.split('.')
            datetime = y[0] + '.' + y[1]

            #db.insert_recording
            print('inserting: {0:}, {1:}, {2:}, {3:}'.format(self.current_recording, datetime, device_id, description))
            index = helper.insert_audio(self.audio_sent_db, device_id, datetime, self.current_recording, description)
            
            self.audio_sent_db_rows +=  1

            self.insert_audio_sent(device_id, datetime, self.current_recording, description)

            segment = Data_Segment('audio', self.current_recording)
            self.audio_queue_out.put(segment)
            
            # tab switch
            self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.tab_4))

            # recorder tab cancel
            self.tabWidget.setTabEnabled(self.tabWidget.indexOf(self.tab_5), False)

    def insert_audio_sent(self, device_id, datetime, filename, description):

        self.tableWidget_3.setRowCount(self.audio_sent_db_rows)

        item = QtWidgets.QTableWidgetItem()
        item.setText(device_id)
        self.tableWidget_3.setItem(self.audio_sent_db_rows - 1, 0, item)

        item = QtWidgets.QTableWidgetItem()
        item.setText(datetime)
        self.tableWidget_3.setItem(self.audio_sent_db_rows - 1, 1, item)   

        item = QtWidgets.QTableWidgetItem()
        item.setText(filename)
        self.tableWidget_3.setItem(self.audio_sent_db_rows - 1, 2, item)

        item = QtWidgets.QTableWidgetItem()
        item.setText(description)
        self.tableWidget_3.setItem(self.audio_sent_db_rows - 1, 3, item)

    def insert_audio_recieved(self, data_segment):
        print('Inserting received audio')
        msg = data_segment.data
        msg_arr = msg.split(',')

        device_id = msg_arr[0]
        date_time = msg_arr[1]
        datetime_utc = datetime.datetime.utcfromtimestamp(float(date_time))
        time_string = datetime_utc.strftime('%H:%M:%S %d/%m/%Y')
        filename = msg_arr[2]
        description = 'Audio message received remotely, inserting into GUI'

        index = helper.insert_audio(self.audio_recv_db, device_id, date_time, filename, description)
        
        self.audio_recv_db_rows = index + 1
        self.tableWidget_4.setRowCount(self.audio_recv_db_rows)

        item = QtWidgets.QTableWidgetItem()
        item.setText(QtWidgets.QApplication.translate("MainWindow", device_id, None, -1))
        self.tableWidget_4.setItem(self.audio_sent_db_rows - 1, 0, item)

        item = QtWidgets.QTableWidgetItem()
        item.setText(QtWidgets.QApplication.translate("MainWindow", time_string, None, -1))
        self.tableWidget_4.setItem(self.audio_sent_db_rows - 1, 1, item)   

        item = QtWidgets.QTableWidgetItem()
        item.setText(QtWidgets.QApplication.translate("MainWindow", filename, None, -1))
        self.tableWidget_4.setItem(self.audio_sent_db_rows - 1, 2, item)

        item = QtWidgets.QTableWidgetItem()
        item.setText(QtWidgets.QApplication.translate("MainWindow", description, None, -1))
        self.tableWidget_4.setItem(self.audio_sent_db_rows - 1, 3, item)

        self.tabWidget.setCurrentIndex(3)

    def audio_record_click(self):

        # tab enable
        self.tabWidget.setTabEnabled(self.tabWidget.indexOf(self.tab_5), True)

        # tab switch
        self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.tab_5)) # 

        return ''

    def audio_cell_clicked(self, row, column):

        item = self.tableWidget_3.item(row, column)
        self.cell_clicked_text = item.text()
        print('Cell text: {0:}'.format(self.cell_clicked_text))

    def audio_play_click(self):

        if self.cell_clicked_text is not None:
            pygame.mixer.pre_init(8000,-16,1, 1024)
            pygame.mixer.init()
            pygame.mixer.music.load(self.cell_clicked_text)
            pygame.mixer.music.play()

        return ''

    def broadcast_message(self, window):
        message = self.plainTextEdit.toPlainText()
        date_time = datetime.datetime.timestamp(datetime.datetime.now())
        index = helper.insert_message(self.message_db, 'BROADCAST', date_time, message)
        self.message_db_rows = index + 1    
        self.tableWidget.setRowCount(self.message_db_rows)
        self.insert_message(self, 'BROADCAST', date_time, message)

    def direct_message(self, window):
        message = self.plainTextEdit_2.toPlainText()
        device_id = self.comboBox.currentText()
        date_time = datetime.datetime.timestamp(datetime.datetime.now())
        index = helper.insert_message(self.message_db, device_id, date_time, message)
        self.message_db_rows = index + 1    
        self.tableWidget.setRowCount(self.message_db_rows)
        self.insert_message(self, device_id, date_time, message)

    def setupUi(self, MainWindow):

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "MainWindow - Portal", None, -1))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(20, 10, 761, 551))
        self.tabWidget.setTabBarAutoHide(False)
        self.tabWidget.setObjectName("tabWidget")


        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
    
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        
        self.menuMain = QtWidgets.QMenu(self.menubar)
        self.menuMain.setObjectName("menuMain")  
        self.menubar.addAction(self.menuMain.menuAction())
        self.menuMain.setTitle(QtWidgets.QApplication.translate("MainWindow", "Main", None, -1))

        MainWindow.setCentralWidget(self.centralwidget)
        MainWindow.setStatusBar(self.statusbar)
        MainWindow.setMenuBar(self.menubar)

        # Admin tab ---------------------------------------------------------------
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tabWidget.addTab(self.tab, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtWidgets.QApplication.translate("MainWindow", "Admin", None, -1))
        
        # Admin tab -> Enrolled Devices table
        self.tableWidget_2 = QtWidgets.QTableWidget(self.tab)
        self.tableWidget_2.setGeometry(QtCore.QRect(300, 80, 431, 321))
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setColumnCount(3)
        self.tableWidget_2.setRowCount(self.device_db_rows)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(0, 2, item)
        self.tableWidget_2.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget_2.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_2.horizontalHeader().setDefaultSectionSize(120)

        self.tableWidget_2.horizontalHeaderItem(0).setText(QtWidgets.QApplication.translate("MainWindow", "ID", None, -1))
        self.tableWidget_2.horizontalHeaderItem(1).setText(QtWidgets.QApplication.translate("MainWindow", "Customer", None, -1))
        self.tableWidget_2.horizontalHeaderItem(2).setText(QtWidgets.QApplication.translate("MainWindow", "Notes", None, -1))
        __sortingEnabled = self.tableWidget_2.isSortingEnabled()
        self.tableWidget_2.setSortingEnabled(False)
        self.tableWidget_2.setSortingEnabled(__sortingEnabled)

        # Admin tab -> Device enrolment groupbox
        self.groupBox = QtWidgets.QGroupBox(self.tab)
        self.groupBox.setGeometry(QtCore.QRect(20, 80, 251, 321))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(185, 185, 185))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(185, 185, 185))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(185, 185, 185))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(185, 185, 185))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.groupBox.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.groupBox.setFont(font)
        self.groupBox.setAutoFillBackground(True)
        self.groupBox.setObjectName("groupBox")

        self.groupBox.setTitle(QtWidgets.QApplication.translate("MainWindow", "Device Enrolment", None, -1))

        # Admin tab -> D.E. groupbox -> Device ID label
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(10, 50, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")

        self.label_5.setText(QtWidgets.QApplication.translate("MainWindow", "Device ID:", None, -1))

         # Admin tab -> D.E. groupbox -> Device dropdown menu
        self.comboBox_2 = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_2.setGeometry(QtCore.QRect(80, 50, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.comboBox_2.setFont(font)
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")

        self.comboBox_2.setItemText(0, QtWidgets.QApplication.translate("MainWindow", "0013A2004155E2AB", None, -1))
        self.comboBox_2.setItemText(1, QtWidgets.QApplication.translate("MainWindow", "0013A2004155E2A6", None, -1))

        # Admin tab -> D.E. groupbox -> name label
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setGeometry(QtCore.QRect(10, 90, 211, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")

        self.label_6.setText(QtWidgets.QApplication.translate("MainWindow", "Name", None, -1))

        # Admin tab -> D.E. groupbox -> name textbox
        self.plainTextEdit_3 = QtWidgets.QPlainTextEdit(self.groupBox)
        self.plainTextEdit_3.setGeometry(QtCore.QRect(10, 110, 231, 41))
        self.plainTextEdit_3.setObjectName("plainTextEdit_3")

        self.plainTextEdit_3.setToolTip(QtWidgets.QApplication.translate("MainWindow", "<html><head/><body><p>Enter text</p></body></html>", None, -1))

        # Admin tab -> D.E. groupbox -> notes label
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setGeometry(QtCore.QRect(10, 160, 131, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")

        self.label_7.setText(QtWidgets.QApplication.translate("MainWindow", "Notes", None, -1))

        # Admin tab -> D.E. groupbox -> notes textbox
        self.plainTextEdit_4 = QtWidgets.QPlainTextEdit(self.groupBox)
        self.plainTextEdit_4.setGeometry(QtCore.QRect(10, 190, 231, 71))
        self.plainTextEdit_4.setObjectName("plainTextEdit_4")

        self.plainTextEdit_4.setToolTip(QtWidgets.QApplication.translate("MainWindow", "<html><head/><body><p>Enter text</p></body></html>", None, -1))

        # Admin tab -> D.E. groupbox -> submit button
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_3.setGeometry(QtCore.QRect(20, 282, 211, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")

        self.pushButton_3.setText(QtWidgets.QApplication.translate("MainWindow", "Submit", None, -1))
        
        self.pushButton_3.clicked.connect(self.enrol_device)
        
        # Admin tab -> enrolled devices label
        self.label_12 = QtWidgets.QLabel(self.tab)
        self.label_12.setGeometry(QtCore.QRect(300, 50, 431, 20))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_12.setFont(font)
        self.label_12.setAlignment(QtCore.Qt.AlignCenter)
        self.label_12.setObjectName("label_12")

        self.label_12.setText(QtWidgets.QApplication.translate("MainWindow", "Enrolled Devices", None, -1))

        #----------------------------------------------------------------

        # Map tab ------------------------------------------------------
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtWidgets.QApplication.translate("MainWindow", "Map", None, -1))
        

        #self.widget = QtWidgets.QWidget(self.tab_3)
        self.widget = QtWebEngineWidgets.QWebEngineView(self.tab_3)
        self.widget.setGeometry(QtCore.QRect(0, 0, 751, 521))
        self.widget.setAutoFillBackground(True)
        self.widget.load(QtCore.QUrl().fromLocalFile(os.path.split(os.path.abspath(__file__))[0]+r'\html\plot_points_to_map.html'))
        self.widget.show()
        self.widget.setObjectName("widget")
        #---------------------------------------------------------------

        # Messages tab ------------------------------------------------
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtWidgets.QApplication.translate("MainWindow", "Messages", None, -1))
        
        # Messages tab -> message table
        self.tableWidget = QtWidgets.QTableWidget(self.tab_2)
        self.tableWidget.setGeometry(QtCore.QRect(0, 211, 751, 311))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(self.message_db_rows)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(0, 2, item)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(160)

        self.tableWidget.horizontalHeaderItem(0).setText(QtWidgets.QApplication.translate("MainWindow", "To", None, -1))
        self.tableWidget.horizontalHeaderItem(1).setText(QtWidgets.QApplication.translate("MainWindow", "DateTime", None, -1))
        self.tableWidget.horizontalHeaderItem(2).setText(QtWidgets.QApplication.translate("MainWindow", "Message", None, -1))

        # Messages tab -> broadcast send button
        self.pushButton = QtWidgets.QPushButton(self.tab_2)
        self.pushButton.setGeometry(QtCore.QRect(240, 130, 71, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")

        self.pushButton.setText(QtWidgets.QApplication.translate("MainWindow", "Send", None, -1))

        self.pushButton.clicked.connect(self.broadcast_message)

        # Messages tab -> direct send button
        self.pushButton_2 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_2.setGeometry(QtCore.QRect(630, 130, 71, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")

        self.pushButton_2.setText(QtWidgets.QApplication.translate("MainWindow", "Send", None, -1))

        self.pushButton_2.clicked.connect(self.direct_message)

        # Messages tab -> direct device id dropdown
        self.comboBox = QtWidgets.QComboBox(self.tab_2)
        self.comboBox.setGeometry(QtCore.QRect(540, 40, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.comboBox.setFont(font)
        self.comboBox.setIconSize(QtCore.QSize(16, 16))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")

        self.comboBox.setCurrentText(QtWidgets.QApplication.translate("MainWindow", "", None, -1))

        # Messages tab -> broadcast message textbox
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.tab_2)
        self.plainTextEdit.setGeometry(QtCore.QRect(43, 80, 271, 41))
        self.plainTextEdit.setObjectName("plainTextEdit")

        self.plainTextEdit.setToolTip(QtWidgets.QApplication.translate("MainWindow", "<html><head/><body><p>Enter text</p></body></html>", None, -1))

        # Messages tab -> direct message textbox
        self.plainTextEdit_2 = QtWidgets.QPlainTextEdit(self.tab_2)
        self.plainTextEdit_2.setGeometry(QtCore.QRect(420, 80, 281, 41))
        self.plainTextEdit_2.setPlaceholderText("")
        self.plainTextEdit_2.setObjectName("plainTextEdit_2")

        self.plainTextEdit_2.setToolTip(QtWidgets.QApplication.translate("MainWindow", "<html><head/><body><p>Tool tip: Enter text</p></body></html>", None, -1))

        # Messages tab -> broadcast label
        self.label_2 = QtWidgets.QLabel(self.tab_2)
        self.label_2.setGeometry(QtCore.QRect(40, 40, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        self.label_2.setText(QtWidgets.QApplication.translate("MainWindow", "Broadcast Message", None, -1))

        # Messages tab -> direct label
        self.label_3 = QtWidgets.QLabel(self.tab_2)
        self.label_3.setGeometry(QtCore.QRect(420, 40, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")

        self.label_3.setText(QtWidgets.QApplication.translate("MainWindow", "Direct Message", None, -1))

        # Messages tab -> Message history label
        self.label_4 = QtWidgets.QLabel(self.tab_2)
        self.label_4.setGeometry(QtCore.QRect(0, 180, 751, 21))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")

        self.label_4.setText(QtWidgets.QApplication.translate("MainWindow", "Message History", None, -1))

        #-----------------------------------------------------------------------------

        # Audio tab ------------------------------------------------------------------
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.tabWidget.addTab(self.tab_4, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QtWidgets.QApplication.translate("MainWindow", "Audio", None, -1))
    
        # audio tab -> sent table
        self.tableWidget_3 = QtWidgets.QTableWidget(self.tab_4)
        self.tableWidget_3.setGeometry(QtCore.QRect(0, 90, 751, 181))
        self.tableWidget_3.setRowCount(self.audio_sent_db_rows)
        self.tableWidget_3.setObjectName("tableWidget_3")
        self.tableWidget_3.setColumnCount(4)
        self.tableWidget_3.setRowCount(self.audio_sent_db_rows)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_3.setHorizontalHeaderItem(3, item)
        self.tableWidget_3.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget_3.horizontalHeader().setDefaultSectionSize(120)
        self.tableWidget_3.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_3.verticalHeader().setStretchLastSection(False)

        self.tableWidget_3.horizontalHeaderItem(0).setText(QtWidgets.QApplication.translate("MainWindow", "To", None, -1))
        self.tableWidget_3.horizontalHeaderItem(1).setText(QtWidgets.QApplication.translate("MainWindow", "DateTime", None, -1))
        self.tableWidget_3.horizontalHeaderItem(2).setText(QtWidgets.QApplication.translate("MainWindow", "Filename", None, -1))
        self.tableWidget_3.horizontalHeaderItem(3).setText(QtWidgets.QApplication.translate("MainWindow", "Description", None, -1))

        self.tableWidget_3.cellClicked.connect(self.audio_cell_clicked)

        # audio tab -> sent label
        self.label_8 = QtWidgets.QLabel(self.tab_4)
        self.label_8.setGeometry(QtCore.QRect(0, 60, 91, 16))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")

        self.label_8.setText(QtWidgets.QApplication.translate("MainWindow", "Sent", None, -1))

        # audio tab -> recieved table
        self.tableWidget_4 = QtWidgets.QTableWidget(self.tab_4)
        self.tableWidget_4.setGeometry(QtCore.QRect(0, 340, 751, 191))
        self.tableWidget_4.setRowCount(self.audio_recv_db_rows)
        self.tableWidget_4.setObjectName("tableWidget_4")
        self.tableWidget_4.setColumnCount(4)
        self.tableWidget_4.setRowCount(self.audio_recv_db_rows)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_4.setHorizontalHeaderItem(3, item)
        self.tableWidget_4.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget_4.horizontalHeader().setDefaultSectionSize(120)
        self.tableWidget_4.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_4.verticalHeader().setStretchLastSection(False)

        self.tableWidget_4.horizontalHeaderItem(0).setText(QtWidgets.QApplication.translate("MainWindow", "From", None, -1))
        self.tableWidget_4.horizontalHeaderItem(1).setText(QtWidgets.QApplication.translate("MainWindow", "DateTime", None, -1))
        self.tableWidget_4.horizontalHeaderItem(2).setText(QtWidgets.QApplication.translate("MainWindow", "Filename", None, -1))
        self.tableWidget_4.horizontalHeaderItem(3).setText(QtWidgets.QApplication.translate("MainWindow", "Notes", None, -1))

        self.tableWidget_4.cellClicked.connect(self.audio_cell_clicked)

        # audio tab -> recieved label
        self.label_9 = QtWidgets.QLabel(self.tab_4)
        self.label_9.setGeometry(QtCore.QRect(0, 310, 91, 16))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")

        self.label_9.setText(QtWidgets.QApplication.translate("MainWindow", "Recieved", None, -1))

        # audio tab -> record button
        self.pushButton_4 = QtWidgets.QPushButton(self.tab_4)
        self.pushButton_4.setGeometry(QtCore.QRect(620, 40, 131, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setObjectName("pushButton_4")

        self.pushButton_4.setText(QtWidgets.QApplication.translate("MainWindow", "Record", None, -1))

        self.pushButton_4.clicked.connect(self.audio_record_click)

        # audio tab -> play button
        self.pushButton_5 = QtWidgets.QPushButton(self.tab_4)
        self.pushButton_5.setGeometry(QtCore.QRect(620, 290, 131, 41))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_5.setFont(font)
        self.pushButton_5.setObjectName("pushButton_5")

        self.pushButton_5.setText(QtWidgets.QApplication.translate("MainWindow", "Play", None, -1))

        self.pushButton_5.clicked.connect(self.audio_play_click)

        #----------------------------------------------------------------------------------

        # Recorder tab -------------------------------------------------------------------
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.tabWidget.addTab(self.tab_5, "")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QtWidgets.QApplication.translate("MainWindow", "Recorder", None, -1))

        # Recorder tab -> recorder groupbox
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab_5)
        self.groupBox_2.setGeometry(QtCore.QRect(260, 70, 271, 371))

        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(130, 130, 130))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(130, 130, 130))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(130, 130, 130))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(130, 130, 130))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)

        self.groupBox_2.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setAutoFillBackground(True)
        self.groupBox_2.setObjectName("groupBox_2")

        self.groupBox_2.setTitle(QtWidgets.QApplication.translate("MainWindow", "Audio Recorder", None, -1))

        # Recorder tab -> recorder groupbox -> stop button
        self.pushButton_7 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_7.setGeometry(QtCore.QRect(180, 50, 75, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_7.setFont(font)
        self.pushButton_7.setObjectName("pushButton_7")

        self.pushButton_7.setText(QtWidgets.QApplication.translate("MainWindow", "Stop", None, -1))

        self.pushButton_7.clicked.connect(self.recorder_stop_click)

        # Recorder tab -> recorder groupbox -> record button
        self.pushButton_6 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_6.setGeometry(QtCore.QRect(10, 50, 75, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_6.setFont(font)
        self.pushButton_6.setObjectName("pushButton_6")

        self.pushButton_6.setText(QtWidgets.QApplication.translate("MainWindow", "Record", None, -1))

        self.pushButton_6.clicked.connect(self.recorder_record_click)

        # Recorder tab -> recorder groupbox -> play button
        self.pushButton_8 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_8.setGeometry(QtCore.QRect(10, 120, 75, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_8.setFont(font)
        self.pushButton_8.setObjectName("pushButton_8")

        self.pushButton_8.setText(QtWidgets.QApplication.translate("MainWindow", "Play", None, -1))

        self.pushButton_8.clicked.connect(self.recorder_play_click)

        # Recorder tab -> recorder groupbox -> destination label
        self.label_10 = QtWidgets.QLabel(self.groupBox_2)
        self.label_10.setGeometry(QtCore.QRect(10, 170, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")

        self.label_10.setText(QtWidgets.QApplication.translate("MainWindow", "Destination:", None, -1))

        # Recorder tab -> recorder groupbox -> destination id dropdown
        self.comboBox_3 = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_3.setGeometry(QtCore.QRect(100, 165, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.comboBox_3.setFont(font)
        self.comboBox_3.setObjectName("comboBox_3")

        # Recorder tab -> recorder groupbox -> description label
        self.label_11 = QtWidgets.QLabel(self.groupBox_2)
        self.label_11.setGeometry(QtCore.QRect(10, 210, 101, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")

        self.label_11.setText(QtWidgets.QApplication.translate("MainWindow", "Description:", None, -1))

        # Recorder tab -> recorder groupbox -> description textbox
        self.plainTextEdit_5 = QtWidgets.QPlainTextEdit(self.groupBox_2)
        self.plainTextEdit_5.setGeometry(QtCore.QRect(10, 240, 251, 71))
        self.plainTextEdit_5.setObjectName("plainTextEdit_5")

        self.plainTextEdit_5.setToolTip(QtWidgets.QApplication.translate("MainWindow", "<html><head/><body><p>Enter text</p></body></html>", None, -1))

        # Recorder tab -> recorder groupbox -> send button
        self.pushButton_10 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_10.setGeometry(QtCore.QRect(170, 330, 75, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_10.setFont(font)
        self.pushButton_10.setObjectName("pushButton_10")

        self.pushButton_10.setText(QtWidgets.QApplication.translate("MainWindow", "Send", None, -1))

        self.pushButton_10.clicked.connect(self.recorder_send_click)

        # Recorder tab -> recorder groupbox -> reset button
        self.pushButton_9 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_9.setGeometry(QtCore.QRect(180, 120, 75, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_9.setFont(font)
        self.pushButton_9.setObjectName("pushButton_9")

        self.pushButton_9.setText(QtWidgets.QApplication.translate("MainWindow", "Reset", None, -1))

        self.pushButton_9.clicked.connect(self.recorder_reset_click)

        # Recorder tab -> recorder groupbox -> cancel button
        self.pushButton_11 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_11.setGeometry(QtCore.QRect(20, 330, 75, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_11.setFont(font)
        self.pushButton_11.setObjectName("pushButton_11")

        self.pushButton_11.setText(QtWidgets.QApplication.translate("MainWindow", "Cancel", None, -1))

        self.pushButton_11.clicked.connect(self.recorder_cancel_click)

        self.tabWidget.setTabEnabled(self.tabWidget.indexOf(self.tab_5), False)

        #-----------------------------------------------------------------------------
        
        self.tabWidget.setCurrentIndex(0)

        self.update_message_tab()
        self.update_admin_tab()
        self.update_audio_tab()
        self.update_record_tab()

        QtCore.QMetaObject.connectSlotsByName(MainWindow)