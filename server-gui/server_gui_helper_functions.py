from multiprocessing import Process, Queue # Used for multiprocessing
import time
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile
from tinydb import TinyDB, Query

# DB functions -----------------------------------------------------------
#
def init_db():
    device_db = TinyDB('db/device.json')
    message_db = TinyDB('db/message.json')

    return device_db, message_db

def insert_message(db, device_id, datetime, message):

    return db.insert({'device_id': device_id, 'datetime': datetime, 'message': message}) - 1

def insert_device(db, device_id, name, notes):
    return db.insert({'device_id': device_id, 'name': name, 'notes': notes}) - 1
#
# ------------------------------------------------------------------------

device_db = TinyDB('db/device.json')
message_db = TinyDB('db/message.json')