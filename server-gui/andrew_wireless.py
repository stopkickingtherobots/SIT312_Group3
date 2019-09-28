<<<<<<< HEAD
from multiprocessing import Process, Queue # Used for multiprocessing
import serial
import time
import pickle
from digi.xbee.devices import XBeeDevice
from digi.xbee.devices import RemoteXBeeDevice
from digi.xbee.devices import XBee64BitAddress
from digi.xbee.exception import TimeoutException
import datetime
from pydub import AudioSegment
from numpy import ndarray
import numpy
import sys
from dataclasses import dataclass
import struct
import lzma
import binascii
import queue # for Queue.Empty exception
import math
import wave
from scipy import signal
from timeit import default_timer as timer # Used to report processing time

@dataclass
class Data_Segment:
    data_type: str
    data: str

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
    #print('first segment: {0:}'.format(segment_arr[0]))
    size = segment_arr[0].total_sequence

    result = numpy.empty(size, dtype=list)
    result = b''

    for i in range(0, len(segment_arr)):
        result += segment_arr[i].data

    print('\nrecv compress length: {0:}'.format(len(result)))
    print('compressed: {0:}'.format(result[0:20]))

    decompressed_result = lzma.decompress(result)

    #unpickled = pickle.loads(decompressed_result)

    #un_hex = binascii.unhexlify(decompressed_result)

    filename = str(datetime.datetime.timestamp(datetime.datetime.now())) + '.ogg'
    wav_filename = 'audio/in/'+ str(datetime.datetime.timestamp(datetime.datetime.now())) + '.wav'
    
    fout = open(filename, 'wb')
    fout.write(decompressed_result)
    fout.close()

    wave_data = AudioSegment.from_file(filename).get_array_of_samples()
    pydub_audio = AudioSegment(wave_data, sample_width=2, frame_rate=8000, channels=1)

    pydub_audio.export(wav_filename, format = "wav")  # ~50% reduction in file size; 91KB per 10 seconds
    
    #print('recv bytes    length: {0:}'.format(len(decompressed_result)))
    #print('Array of samples server: {0:}'.format(len(wave_data)))

    return wav_filename

def split_pickle(pickled):

    compressed_bytes = lzma.compress(pickled)
    bytes_per_msg = 125
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

    print('bytes    length: {0:}'.format(len(pickled)))
    print('compress length: {0:}'.format(len(compressed_bytes)))
    print('num_segments ceil: {0:}'.format(num_segments))
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

    #start = timer()
    recording_resample = signal.resample(signal_arr, int(len(signal_arr)/6)).astype(numpy.int16)
    #end = timer()

    resample_len = int(len(recording_resample) * diff_rate)

    if resample_len % 2 == 1:
        resample_len -= 1
    truncate_arr = numpy.zeros(resample_len)

    truncate_arr = recording_resample[:len(truncate_arr)]

    resamples = b''

    for i in range(0, len(truncate_arr)):
        resamples += (int(truncate_arr[i]/256)).to_bytes(2, byteorder='big', signed=True)

    pydub_audio = AudioSegment(resamples, sample_width=2, frame_rate=8000, channels=1)

    pydub_audio.export(filename, format = "mp3", codec='libmp3lame')  # ~50% reduction in file size; 91KB per 10 seconds
    
    #print('Length of wav_data: {0:}'.format(len(wave_data)))
    #print('Length of signal_arr: {0:}'.format(len(signal_arr)))
    #print('Begin resampling')
    #print('Finished resampling: {0:} seconds'.format(end-start))

    return filename

def prepare_audio(filename):

    resample_audio(filename)

    with open(filename, 'rb') as f:
        content = f.read()
    
    #pickled = pickle.dumps(binascii.hexlify(content))

    compressed_bytes = lzma.compress(binascii.hexlify(content))

    bytes_per_msg = 125 # Xbee packet size limit
    #length = len(compressed_bytes)
    #bytes_in_data = length
    bytes_in_data = len(compressed_bytes)
    num_segments = math.ceil(bytes_in_data / bytes_per_msg)
    result_arr = []
    index = 0

    for i in range(0, num_segments):
        seg = Bytes_Segment(b'0x01', i, num_segments, compressed_bytes[index:index+bytes_per_msg])
        index += bytes_per_msg
        result_arr.append(seg)

    # Troubleshooting statements, not for deployment
    #byte_piece = compressed_bytes[0:bytes_per_msg]
    #b = Bytes_Segment(b'0x01', 1, 1, compressed_bytes[index:index+bytes_per_msg])
    #print('bytes    length: {0:}'.format(len(pickled)))
    print('uncompress length: {0:}'.format(len(content)))
    print('compress length: {0:}'.format(len(compressed_bytes)))
    print('num_segments ceil: {0:}'.format(num_segments))
    #print('Byte_piece size: {0:}'.format(getsizeof(byte_piece)))
    #print('Data_Segment size: {0:}'.format(getsizeof(b)))

    return result_arr

    #recording_arr = split_pickle(pickled)

    #return recording_arr

def xbee_read(device):

    try:
        #device.flush_queues()
        rcv_bytes = device.read_data(1)
        rcv = pickle.loads(rcv_bytes.data)
        print('xbee_read(): {0:}'.format(rcv))
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

            print('Server recieved Audio message')
            print('Sending ACK')

            bytes_obj = pickle.dumps('ACK')
            device.send_data(rcv_bytes.remote_device, bytes_obj)
            device.flush_queues()

            recv_addr = str(rcv_bytes.remote_device.get_64bit_addr())
            time_stamp = str(datetime.datetime.timestamp(datetime.datetime.now()))

            data_segment = Data_Segment('audio', recv_addr + ','+ time_stamp+','+filename)
            return data_segment            
        
        if rcv.data_type == b'0x02':   # Distress byte signature
            #print('Server recieved distress, sending ACK')
            bytes_obj = pickle.dumps('ACK')
            device.send_data(rcv_bytes.remote_device, bytes_obj)
            data_segment = Data_Segment('distress',rcv.data)
            return data_segment

        if rcv.data_type == b'0x03':   # GPS byte signature
            #print('Server recieved GPS')
            #print('Sending ACK')
            bytes_obj = pickle.dumps('ACK')
            device.send_data(rcv_bytes.remote_device, bytes_obj)

            data_segment = Data_Segment('gps', rcv.data)
            return data_segment

        if rcv.data_type == b'0x00':   # Shutdown byte signature
            print('Server recieved shutdown')
            #print('Sending ACK')
            bytes_obj = pickle.dumps('ACK')
            device.send_data(rcv_bytes.remote_device, bytes_obj)
            
            device.close()
            return None

    except TimeoutException:
        #print("Timeout on Server Wireless read()")
        return Data_Segment('TIMEOUT','')

def xbee_write(device, data_segment):

    #print('xbee_writing: {0:}'.format(data_segment))

    data_arr = data_segment.data.split(',')
    
    remote_addr = data_arr[0]
    if remote_addr != '0013A2004155E2AB':
        print('Invalid address supplied - proceeding with known good address for demonstration')
        print('data_arr: {0:}'.format(data_arr))
        remote_addr = '0013A2004155E2AB'
    remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(remote_addr))

    if data_segment.data_type == 'audio':
        prepared_audio = prepare_audio(data_segment.data) # prepare_audio(filename)
        #print('Sending Audio from Server')
        for i in range(0, len(prepared_audio)):        
            bytes_obj = pickle.dumps(prepared_audio[i])
            device.send_data(remote_device, bytes_obj)
        
        device.flush_queues()
        rcv_bytes = None
        while rcv_bytes is None:
            rcv_bytes = device.read_data()

        rcv = pickle.loads(rcv_bytes.data)
        #print('Audio rcv: {0:}'.format(rcv))
        if rcv == 'ACK':
            #print('Audio Transfer complete')     
            device.flush_queues()
            return 'ACK'
        else:
            print('Audio transfer failed')
            return 'ERROR'

    if data_segment.data_type == 'message':
        print('Sending \'message\' from Server')
        msg = data_segment.data
        sending_arr = []
        if len(msg) > 125:
            print('\'message\' is greater than 140! length: {0:}'.format(len(msg)))
            x = pickle.dumps(msg)
            sending_arr = split_pickle(x)
        else:
            sending_arr.append(Bytes_Segment(b'0x04', 1, 1, data_segment.data))
            #print('message sending_arr: {0:}'.format(sending_arr))
        for i in range(0, len(sending_arr)):
            bytes_obj = pickle.dumps(sending_arr[i])
            #print('Sending message bytes_obj')
            device.send_data(remote_device, bytes_obj)
        try:
            device.flush_queues()
            rcv_bytes = device.read_data(2)
            rcv = pickle.loads(rcv_bytes.data)
            if rcv == 'ACK':
                return 'ACK'
            else:
                print('message not ack\'d')
        except TimeoutException:
            print('Message was not transmitted from xbee_write()')
        #print('MSG rcv: {0:}'.format(rcv))
        #if rcv == 'ACK':
            #print('MSG complete')
        #    return 'ACK'
        #else:
        #    print('MSG transfer failed')
        #    return 'ERROR'  

    if data_segment.data_type == 'exit':
        msg = data_segment.data
        sending_arr = []
        #print('Sending Message from Server')
        if len(msg) > 140:
            x = pickle.dumps(msg)
            sending_arr = split_pickle(x)
        else:
            sending_arr.append(Bytes_Segment(b'0x00', 1, 1, data_segment.data))
        for i in range(0, len(sending_arr)):
            bytes_obj = pickle.dumps(sending_arr[i])
            device.send_data(remote_device, bytes_obj)

        rcv_bytes = None
        while rcv_bytes is None:
            rcv_bytes = device.read_data()
        rcv = pickle.loads(rcv_bytes.data)
        if rcv == 'ACK':
            return 'ACK'
        else:
            print('EXIT transfer failed')
            return 'ERROR'  
    else:
        print('Unknown data_type to send via XBee: {0:}'.format(data_segment))
        return 'ERROR'

def main(gps_queue, distress_queue, message_queue, audio_queue_in, audio_queue_out):

    print('Begin Wireless')

    device = XBeeDevice('COM3', 230400)

    device.open()
    device.flush_queues()

    while(True):
        
        data_segment = xbee_read(device) # This device, Set timeout
        #print('Got data_segment from xbee_read: {0:}'.format(data_segment))
        #print('data_segment type: {0:}'.format(type(data_segment)))
        #print('data_segment isinstance: {0:}'.format(isinstance(data_segment, Data_Segment)))

        if data_segment is not None:
            if data_segment.data_type == 'TIMEOUT':
                pass
            if data_segment.data_type == 'gps':
                #print('Server got: {0:}'.format(data_segment))
                gps_queue.put(data_segment)

            if data_segment.data_type == 'audio':
                #print('Got audio segment from xbee read in main()')
                audio_queue_in.put(data_segment)
                print('audio put on queue')

            if data_segment.data_type == 'distress':
                distress_queue.put(data_segment)

            if data_segment.data_type == 'TIMEOUT':
                pass
                # print('Timeout at server wireless read(), retrying')

        else:
            # Probably shutdown signal, so exit
            print('Shutdown signal at wireless read(), exiting')
            device.close()
            return
        
        try:
            #print('checking message queue')
            old_segment = message_queue.get(timeout=2)
            
            #print('Got data_segment from message_queue: {0:}'.format(data_segment))
            #print('data_segment type: {0:}'.format(type(data_segment)))
            #print('data_segment isinstance: {0:}'.format(isinstance(data_segment, Data_Segment)))
            if data_segment is not None:
                
                if old_segment.data_type == 'exit':
                    data_segment = Data_Segment('exit', old_segment.data)
                    print('Exit command recieved, sending termination message to remote devices')
                    result = xbee_write(device, data_segment)
                    if result != 'ACK':
                        print('Data_Segment: {0:} failed to send, remote devices not commanded to exit.\n Exiting...'.format(data_segment))         
                        device.close()
                        return

                data_segment = Data_Segment('message', old_segment.data)
                #print('Got message from message queue in wireless.main(), writing to xbee')
                result = xbee_write(device, data_segment)
                if result != 'ACK':
                    print('Data_Segment: {0:} failed to send, dropping packet'.format(data_segment))
        except queue.Empty:
            pass
            #print('Empty message_out queue, continuing')
        
        try:
            #print('checking audio queue')
            data_segment = audio_queue_out.get(timeout=2)
            #print('Got data_segment from message_queue: {0:}'.format(data_segment))
            #print('data_segment type: {0:}'.format(type(data_segment)))
            #print('data_segment isinstance: {0:}'.format(isinstance(data_segment, Data_Segment)))
            if data_segment is not None:
                result = xbee_write(device, data_segment)
                if result != 'ACK':
                    print('Data_Segment: {0:} failed to send, dropping packet'.format(data_segment))
        except queue.Empty:
            pass
            #print('Empty audio_out queue, continuing')
        
=======
from multiprocessing import Process, Queue # Used for multiprocessing
import time

def main(gps_queue, distress_queue, message_queue, audio_queue_in, audio_queue_out):

    print('Begin wireless')

>>>>>>> 536bb62244a04a7ad2148b81b56f06155b3e39bd
    print('End wireless')