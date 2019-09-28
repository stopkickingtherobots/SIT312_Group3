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
import wave
import struct
import lzma
from sys import getsizeof
import math
from pydub import AudioSegment
from scipy import signal
from timeit import default_timer as timer # Used to report processing time
import binascii

@dataclass
class Bytes_Segment:
    data_type: numpy.byte
    sequence: numpy.int16
    total_sequence: numpy.int16
    data: str

def split_pickle(pickled):

    compressed_bytes = lzma.compress(pickled)
    bytes_per_msg = 140
    length = len(compressed_bytes)
    bytes_in_data = length
    num_segments = math.ceil(bytes_in_data / bytes_per_msg)
    result_arr = []
    index = 0
    byte_piece = compressed_bytes[0:bytes_per_msg]
    b = Bytes_Segment(b'0x01', 1, 1, compressed_bytes[index:index+bytes_per_msg])

    for i in range(0, num_segments):
        a = Bytes_Segment(b'0x01', i, num_segments, compressed_bytes[index:index+bytes_per_msg])
        index += bytes_per_msg
        result_arr.append(a)

    #print('bytes    length: {0:}'.format(len(pickled)))
    #print('compress length: {0:}'.format(len(compressed_bytes)))
    #print('num_segments ceil: {0:}'.format(num_segments))
    #print('Byte_piece size: {0:}'.format(getsizeof(byte_piece)))
    #print('Data_Segment size: {0:}'.format(getsizeof(b)))

    return result_arr

def resample_audio(filename):

    wave_file = wave.open(filename, 'r')
    nframes = wave_file.getnframes()
    nchannels = wave_file.getnchannels()
    sample_frequency = wave_file.getframerate()
    read_frames = wave_file.readframes(nframes)
    wave_file.close()
    wave_data = struct.unpack("%ih" % nchannels*nframes, read_frames) # '%ih' is 16-bit format
    
    y = numpy.floor(numpy.log2(len(wave_data)))
    nextpow2  = numpy.power(2, y+1)

    diff = (nextpow2 - len(wave_data)) % 2
    diff_rate = len(wave_data) / nextpow2

    signal_arr = numpy.zeros(int(nextpow2))
    signal_arr[0:len(wave_data)] = wave_data

    start = timer()
    recording_resample = signal.resample(signal_arr, int(len(signal_arr)/6)).astype(numpy.int16)
    end = timer()

    resample_len = int(len(recording_resample) * diff_rate)

    if resample_len % 2 == 1:
        resample_len -= 1
    truncate_arr = numpy.zeros(resample_len)

    truncate_arr = recording_resample[:len(truncate_arr)]

    resamples = b''

    for i in range(0, len(truncate_arr)):
        resamples += (int(truncate_arr[i]/256)).to_bytes(2, byteorder='big', signed=True)

    pydub_audio = AudioSegment(resamples, sample_width=2, frame_rate=8000, channels=1)

    pydub_audio.export("resample.mp3", format = "mp3", codec='libmp3lame')  # ~50% reduction in file size; 91KB per 10 seconds
    
    #print('Length of wav_data: {0:}'.format(len(wave_data)))
    #print('Length of signal_arr: {0:}'.format(len(signal_arr)))
    #print('Begin resampling')
    #print('Finished resampling: {0:} seconds'.format(end-start))

    return 'resample.mp3'

def prepare_audio(filename):

    with open(filename, 'rb') as f:
        content = f.read()
    
    pickled = pickle.dumps(binascii.hexlify(content))

    recording_arr = split_pickle(pickled)

    return recording_arr

def xbee_0():
    device = XBeeDevice('COM3', 230400)

    remote_addr = '0013A2004155E2AB'
    remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(remote_addr))

    device.open()
    msg = "Test from COM3"

    #resamples = resample_audio('30second_48.wav') # Sarah's example; typical - may change

    prepared_audio = prepare_audio('resample.mp3')

    audio_ack = False
    GPS_ack = False
    SOS_ack = False

    while(True):

        try:     
            
            if not audio_ack:
                print('Sending Audio from COM3')
                for i in range(0, len(prepared_audio)):        
                    bytes_obj = pickle.dumps(prepared_audio[i])
                    device.send_data(remote_device, bytes_obj)
                rcv_bytes = device.read_data(1)
                rcv = pickle.loads(rcv_bytes.data)
                #print('Audio rcv: {0:}'.format(rcv))
                if rcv == 'ACK':
                    #print('Audio Transfer complete')
                    audio_ack = True
                    device.flush_queues()
                else:
                    #print('Audio transfer failed')
                    continue
            
            if not SOS_ack:
                print('Sending SOS from COM3')
                x = Bytes_Segment(b'0x02', 1, 1, 'SOS')
                pickled = pickle.dumps(x)
                device.send_data(remote_device, pickled)
                rcv_bytes = device.read_data(1)
                rcv = pickle.loads(rcv_bytes.data)
                #print('SOS rcv: {0:}'.format(rcv))
                if rcv == 'ACK':
                    #print('SOS complete')
                    SOS_ack = True
                else:
                    #print('SOS transfer failed')
                    continue

            if not GPS_ack:   
                print('Sending GPS from COM3')          
                x = Bytes_Segment(b'0x03', 1, 1, '150,45,130012312312')
                pickled = pickle.dumps(x)
                device.send_data(remote_device, pickled)
                rcv_bytes = device.read_data(1)
                rcv = pickle.loads(rcv_bytes.data)
                #print('GPS rcv: {0:}'.format(rcv))
                if rcv == 'ACK':
                    #print('GPS complete')
                    GPS_ack = True
                else:
                    #print('GPS transfer failed')
                    continue
            
            if audio_ack and GPS_ack and SOS_ack:
            #if True:
                print('Sending Shutdown from COM3')
                x = Bytes_Segment(b'0x00', 1, 1, '')
                pickled = pickle.dumps(x)
                device.send_data(remote_device, pickled)
                rcv_bytes = device.read_data(1)
                rcv = pickle.loads(rcv_bytes.data)
                #print('Shutdown rcv: {0:}'.format(rcv))
                if rcv == 'ACK':
                    print('Shutting down')
                    device.close()       
                    return
                else:
                    print('Shutdown transfer failed') 
                    continue
                    device.close()
                    return

        except TimeoutException:
            #print('Timeout from COM3')
            continue

def main():

    print('Begin client')

    xbee_0()

    print('End client')
    