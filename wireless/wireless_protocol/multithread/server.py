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
import struct
import lzma
import binascii

@dataclass
class Bytes_Segment:
    data_type: numpy.byte
    sequence: numpy.int16
    total_sequence: numpy.int16
    data: str

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

def build_pickle(segment_arr):
    size = segment_arr[0].total_sequence

    result = numpy.empty(size, dtype=list)
    result = b''

    for i in range(0, len(segment_arr)):
        result += segment_arr[i].data

    decompressed_result = lzma.decompress(result)

    unpickled = pickle.loads(decompressed_result)

    un_hex = binascii.unhexlify(unpickled)

    filename = 'test.mp3'

    fout = open(filename, 'wb')
    fout.write(binascii.unhexlify(unpickled))
    fout.close()

    wave_data = AudioSegment.from_file('test.mp3').get_array_of_samples()

    #print('recv compress length: {0:}'.format(len(result)))
    #print('recv bytes    length: {0:}'.format(len(decompressed_result)))
    #print('Array of samples server: {0:}'.format(len(wave_data)))

    return filename
  
def xbee_1():

    device = XBeeDevice('COM4', 230400)

    remote_addr = '0013A2004155E2A6'
    remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(remote_addr))

    device.open()
    msg = "Test from COM4"
    count = 0
    while(True):
        try:
            device.flush_queues()
            rcv_bytes = device.read_data(1)
            rcv = pickle.loads(rcv_bytes.data)
            print('New message: {0:}'.format(rcv))
            result = []

            if rcv.data_type == b'0x01':   # Audio byte signature
                print('Server recieved Audio')
                result = []
                result.append(rcv)
                for i in range(0, rcv.total_sequence - 1):
                    rcv_bytes = device.read_data(1)
                    rcv = pickle.loads(rcv_bytes.data)
                    result.append(rcv)
                filename = build_pickle(result)
                #print('Server recieved Audio message')
                #print('Sending ACK')
                bytes_obj = pickle.dumps('ACK')
                device.send_data(remote_device, bytes_obj)
                device.flush_queues()
            
            if rcv.data_type == b'0x02':   # Distress byte signature
                print('Server recieved distress')
                #print('Sending ACK')
                bytes_obj = pickle.dumps('ACK')
                device.send_data(remote_device, bytes_obj)

            if rcv.data_type == b'0x03':   # GPS byte signature
                print('Server recieved GPS')
                #print('Sending ACK')
                bytes_obj = pickle.dumps('ACK')
                device.send_data(remote_device, bytes_obj)

            if rcv.data_type == b'0x00':   # Shutdown byte signature
                print('Server recieved shutdown')
                #print('Sending ACK')
                bytes_obj = pickle.dumps('ACK')
                device.send_data(remote_device, bytes_obj)
                
                device.close()
                return

        except TimeoutException:
            #print("Timeout on COM4")
            continue

def main():

    print('Begin server')

    xbee_1()

    print('End server')
