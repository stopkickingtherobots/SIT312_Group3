from multiprocessing import Process, Queue # Used for multiprocessing
import time
import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile, QThread, Signal, Slot, QObject
import server_gui_helper_functions as helper
from sit312_portal import Ui_MainWindow
from PySide2.QtCore import Qt as Qt
from multiprocessing import Process, Queue
import queue

from dataclasses import dataclass

@dataclass
class Data_Segment:
    data_type: str
    sequence: int
    total_sequence: int
    data: list

class Distress_Object(QObject):

    aSignal = Signal(Data_Segment)

    def __init__(self, distress_queue):
        super(Distress_Object, self).__init__()
        self.distress_queue = distress_queue
        self.isRunning = True

    def run(self):
        #print('Begin RUN')
        if not self.isRunning:
            self.isRunning = True
        while(self.isRunning):
            try:
                distress_msg = self.distress_queue.get()
                if distress_msg is not None:
                    #print('emitting signal')
                    self.aSignal.emit(distress_msg)
                    continue
            except queue.Empty:
                pass
                #print('empty')

class Audio_Object(QObject):

    bSignal = Signal(Data_Segment)

    def __init__(self, audio_queue_in):
        super(Audio_Object, self).__init__()
        self.audio_queue_in = audio_queue_in
        self.isRunning = True

    def run(self):
        if not self.isRunning:
            self.isRunning = True
        while(self.isRunning):
            try:
                audio_msg = self.audio_queue_in.get()
                print('Got something off audio_in queue')
                if audio_msg is not None:
                    print('got audio in server_gui.py: {0:}'.format(audio_msg))
                    self.bSignal.emit(audio_msg)
                    print('Finished emitting audio_msg signal')
                    continue
            except queue.Empty:
                pass
           
class MainWindow(QMainWindow):
    def __init__(self, device_db, message_db, audio_sent_db, audio_recv_db, audio_queue_out, audio_queue_in, message_queue):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow(device_db, message_db, audio_sent_db, audio_recv_db, audio_queue_out, audio_queue_in, message_queue)
        self.ui.setupUi(self)
        
        #self.distress_queue = distress_queue
        
def main(distress_queue, message_queue, audio_queue_out, audio_queue_in):

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    print('Begin server gui')

    device_db, message_db, audio_sent_db, audio_recv_db = helper.init_db()

    app = QApplication(sys.argv)

    window = MainWindow(device_db, message_db, audio_sent_db, audio_recv_db, audio_queue_out, audio_queue_in, message_queue)
    
    distress_reciever = window.ui.insert_distress_message
    distress_worker = Distress_Object(distress_queue)
    distress_worker.aSignal.connect(distress_reciever)
    distress_thread = QThread()
    distress_worker.moveToThread(distress_thread)
    distress_thread.started.connect(distress_worker.run)
    distress_thread.start()
    
    audio_reciever = window.ui.insert_audio_recieved
    audio_worker = Audio_Object(audio_queue_in)
    audio_worker.bSignal.connect(audio_reciever)
    audio_thread = QThread()
    audio_worker.moveToThread(audio_thread)
    audio_thread.started.connect(audio_worker.run)
    audio_thread.start()

    window.show()
    
    sys.exit(app.exec_())

    print('End server gui')
