from multiprocessing import Process, Queue # Used for multiprocessing
import serial
import time
import pickle
from digi.xbee.devices import XBeeDevice
from digi.xbee.devices import RemoteXBeeDevice
from digi.xbee.devices import XBee64BitAddress
from digi.xbee.exception import TimeoutException
from pydub import AudioSegment
from numpy import ndarray
import numpy
import sys

from dataclasses import dataclass

@dataclass
class Data_Segment:
    data_type: str
    sequence: int
    total_sequence: int
    data: list

def split_audio(data):
    
    bytes_per_msg = 32

    length = len(data)

    print('data to split length: {0:}'.format(len(data)))

    bytes_in_data = length * 2

    num_segments = int(bytes_in_data / bytes_per_msg)
    print('Num of segments: {0:}'.format(num_segments))
    result_arr = []

    index = 0

    for i in range(0, num_segments):
        a = Data_Segment("audio", i, num_segments, data[index:index+bytes_per_msg])
        index += bytes_per_msg
        result_arr.append(a)

    return result_arr
        
def readlineCR(port):
    rv = ""
    while True:
        ch = port.read()
        if ch==b'\r' or ch==b'':
            return rv

        rv += ch.decode()
        
def xbee_0():
    device = XBeeDevice('COM3', 230400)

    remote_addr = '0013A2004155E2AB'
    remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(remote_addr))

    device.open()
    msg = "Test from COM3"

    recording = AudioSegment.from_file("short.wav").get_array_of_samples()

    recording_arr = split_audio(recording)
    try:
        print('Sending from COM3')
        for i in range(0, len(recording_arr)):        
            bytes_obj = pickle.dumps(recording_arr[i])
            #print('Size: {0:}'.format(sys.getsizeof(bytes_obj)))
            device.send_data(remote_device, bytes_obj)

        rcv_bytes = device.read_data(1)
        rcv = pickle.loads(rcv_bytes.data)
        if rcv is "ACK":
            print('Transfer complete')
        print("COM3 received:" + repr(rcv))
    except TimeoutException:
        print('Timeout from COM3')

def build_data(segment_arr):

    size = segment_arr[0].total_sequence

    result = numpy.empty(size, dtype=list)

    for i in range(0, len(segment_arr)):
        result[segment_arr[i].sequence] = segment_arr[i].data

    final_arr = []

    for i in range(0, len(result)):
        for j in range(0, len(result[i])):
 
            final_arr.append(result[i][j])

    return numpy.asarray(final_arr, dtype=numpy.int16)

def xbee_1():
    device = XBeeDevice('COM4', 230400)

    remote_addr = '0013A2004155E2A6'
    remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(remote_addr))

    device.open()
    msg = "Test from COM4"
    count = 0

    try:
        rcv_bytes = device.read_data(1)
        rcv = pickle.loads(rcv_bytes.data)
        result = []
        print('First rcv: {0:}'.format(rcv))
        print('rcv.data_type: {0:}'.format(rcv.data_type))
        if rcv.data_type == 'audio':
            print('Got "Audio"')
            result = []
            result.append(rcv)
            for i in range(0, rcv.total_sequence - 1):
                rcv_bytes = device.read_data(1)
                rcv = pickle.loads(rcv_bytes.data)
                result.append(rcv)
        print("COM4 received:" + repr(rcv))
     
        result_arr = build_data(result)
        print(result_arr)
        flat_arr = ndarray.flatten(result_arr)
        print(flat_arr)

        newrecording = AudioSegment(flat_arr, sample_width=2, frame_rate=8000, channels=1)
        newrecording.export('file.flac', format = "flac")

        print('Sending from 4')
        bytes_obj = pickle.dumps('ACK')
        device.send_data(remote_device, bytes_obj)
    except TimeoutException:
        print("Timeout on COM4")

if __name__ == "__main__":

    producer = Process(target = xbee_0, args = ())

    consumer = Process(target = xbee_1, args = ())

    producer.start()
    consumer.start()

    # Give the processes time to start/run
    time.sleep(1)

    while producer.is_alive() or consumer.is_alive():
    
        # Sleep reduces CPU load for essential while(true) loop
        time.sleep(2)

    if (producer.is_alive() and consumer.is_alive()):
        
        producer.close()
        consumer.close()

    print('\nProducer and Consumer processes ended -------------------------------------\n')