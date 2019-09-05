from multiprocessing import Process, Queue # Used for multiprocessing
import time
import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile
import server_gui_helper_functions as helper
from sit312_portal import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self, device_db, message_db):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow(device_db, message_db)
        self.ui.setupUi(self)       

def main(distress_queue, message_queue):

    print('Begin server gui')

    device_db, message_db = helper.init_db()

    app = QApplication(sys.argv)

    window = MainWindow(device_db, message_db)

    window.show()

    '''
    while(True):  

        # Potential pseudocode ...
        #msg = distress_queue.get()
        #device_id = msg.data[0]
        #datetime = msg.data[1]
        #message = msg.data[2]
        
        device_id = 'Test ID'
        datetime = '1230h 03MAR19'
        message = 'Test Message from queue'

        # The following two lines no longer work. Need to add discrete
        # window.ui.insert_message_queue() functions
        #index = helper.insert_message(message_db, device_id, datetime, message) 
        #window.ui.insert_message(window, device_id, datetime, message)
        break
    '''
    sys.exit(app.exec_())

    print('End server gui')