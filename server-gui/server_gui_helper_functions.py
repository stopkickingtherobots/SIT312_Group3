from multiprocessing import Process, Queue # Used for multiprocessing
import time
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile
from tinydb import TinyDB, Query
import pyaudio      # Connects with Portaudio for audio device streaming
import wave         # Used to save audio to .wav files
import collections  # Used for Double ended Queue (deque) structure
from scipy import signal
import numpy
import datetime

from pydub import AudioSegment

# DB functions -----------------------------------------------------------
#
def init_db():

    device_db = TinyDB('db/device.json')
    message_db = TinyDB('db/message.json')
    audio_sent_db = TinyDB('db/audio_sent.json')
    audio_recv_db = TinyDB('db/audio_recv.json')

    return device_db, message_db, audio_sent_db, audio_recv_db

def insert_message(db, device_id, datetime, message):

    return db.insert({'device_id': device_id, 'datetime': datetime, 'message': message}) - 1

def insert_device(db, device_id, name, notes):
    return db.insert({'device_id': device_id, 'name': name, 'notes': notes}) - 1

def insert_audio(db, device_id, datetime, filename, description):
    return db.insert({'device_id': device_id, 'datetime':datetime, 'filename': filename, 'description': description}) - 1
#
# ------------------------------------------------------------------------

def record_10_seconds():

    # Define Audio characteristics
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000
    CHUNK = 1024
    RECORD_SECONDS = 2
    path = 'audio/'
    MP3_OUTPUT_FILENAME = str(datetime.datetime.timestamp(datetime.datetime.now())) + '.mp3'

    audio = pyaudio.PyAudio()
    
    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,rate=RATE, input=True,frames_per_buffer=CHUNK)
                    
    print ('recording...')

    data = stream.read(int(RATE/CHUNK) * CHUNK * RECORD_SECONDS)

    print ('finished recording')

    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Pydub addition - will export raw audio - data - into specified formats.
    recording = AudioSegment(data, sample_width=2, frame_rate=RATE, channels=1)
    recording.export(path + MP3_OUTPUT_FILENAME, format="mp3")     # Raw audio at 161KB per 10 seconds

    return path + MP3_OUTPUT_FILENAME

device_db = TinyDB('db/device.json')
message_db = TinyDB('db/message.json')