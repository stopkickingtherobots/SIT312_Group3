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
import queue
import datetime
import math

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

    #print('\nrecv compress length: {0:}'.format(len(result)))
    time_code = str(datetime.datetime.timestamp(datetime.datetime.now()))
    filename = 'audio/' + time_code + '.mp3'
    wav_filename = 'audio/' + time_code + '.wav'
    short_filename = time_code + '.wav'
    #print('filename: ' + filename)
    #print('compressed: {0:}'.format(result[0:20]))

    decompressed_result = lzma.decompress(result)

    #unpickled = pickle.loads(decompressed_result)

    un_hex = binascii.unhexlify(decompressed_result)

    fout = open(filename, 'wb')
    fout.write(un_hex)
    fout.close()
    
    wave_data = AudioSegment.from_file(filename).get_array_of_samples()
    
    pydub_audio = AudioSegment(wave_data, sample_width=2, frame_rate=8000, channels=1)

    pydub_audio.export(wav_filename, format = "wav")  # ~50% reduction in file size; 91KB per 10 seconds
    
    #print('recv bytes    length: {0:}'.format(len(decompressed_result)))
    #print('Array of samples server: {0:}'.format(len(wave_data)))

    return short_filename
    
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
        
    #print('first segment: {0:}'.format(result_arr[0]))
    #print('bytes    length: {0:}'.format(len(pickled)))
    #print('compress length: {0:}'.format(len(compressed_bytes)))
    #print('compressed: {0:}'.format(compressed_bytes[:20]))
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

    pydub_audio.export("resample.wav", format = "wav")  # ~50% reduction in file size; 91KB per 10 seconds
    
    #print('Length of wav_data: {0:}'.format(len(wave_data)))
    #print('Length of signal_arr: {0:}'.format(len(signal_arr)))
    #print('Begin resampling')
    #print('Finished resampling: {0:} seconds'.format(end-start))

    return 'resample.wav'

def prepare_audio(filename):
    
    new_filename = 'audio/audio_out/' + filename

    with open(new_filename, 'rb') as f:
        content = f.read()
    
    #pickled = pickle.dumps(binascii.hexlify(content))

    compressed_bytes = lzma.compress(content)

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
    print('compress length: {0:}'.format(len(compressed_bytes)))
    print('compressed: {0:}'.format(compressed_bytes[0:20]))
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
        print('New message: {0:}'.format(rcv))
        result = []
        
        if rcv == 'ACK':
            return Data_Segment('ERROR','')

        if rcv.data_type == b'0x01':   # Audio byte signature
            #print('Client recieved Audio')
            result = []
            result.append(rcv)
            for i in range(0, rcv.total_sequence - 1):
                rcv_bytes = device.read_data(5)
                rcv = pickle.loads(rcv_bytes.data)
                result.append(rcv)
            filename = build_pickle(result)

            #print('Server recieved Audio message')
            #print('Sending ACK')

            bytes_obj = pickle.dumps('ACK')
            device.send_data(rcv_bytes.remote_device, bytes_obj)
            device.flush_queues()

            data_segment = Data_Segment('audio', filename)
            return data_segment            
        
        if rcv.data_type == b'0x04':   # Message byte signature
            #print('Client recieved message')

            #print('Sending ACK')
            bytes_obj = pickle.dumps('ACK')
            device.send_data(rcv_bytes.remote_device, bytes_obj)

            data_segment = Data_Segment('message',rcv.data)
            return data_segment

        if rcv.data_type == b'0x00':   # Shutdown byte signature
            print('Client recieved shutdown')
            #print('Sending ACK')
            bytes_obj = pickle.dumps('ACK')
            device.send_data(rcv_bytes.remote_device, bytes_obj)
            
            device.close()
            return None

    except TimeoutException:
        #print("Timeout on Server Wireless read()")
        return Data_Segment('TIMEOUT','')
    except AttributeError:
        #print('Attribute error for: {0:}'.format(rcv_bytes))
        return Data_Segment('ERROR','')

def xbee_write(device, remote_device, data):

    if data.data_type == 'audio':
        prepared_audio = prepare_audio(data.data) # prepare_audio(filename)
        #print('Sending AUDIO message from Client')
        while(True):
            try:
                for i in range(0, len(prepared_audio)):        
                    bytes_obj = pickle.dumps(prepared_audio[i])
                    device.send_data(remote_device, bytes_obj)
                rcv_bytes = device.read_data(1)
                rcv = pickle.loads(rcv_bytes.data)
                #print('Audio rcv: {0:}'.format(rcv))
                if rcv == 'ACK':
                    #print('Audio Transfer complete')     
                    return 'ACK'
                else:
                    print('Audio transfer failed')
                    return 'ERROR'
            except TimeoutException:
                time.sleep(3)
                continue

    if data.data_type == 'distress':
        #print('Sending distress from write()')
        sent = False
        while(not sent):
            try:
                msg = data.data
                sending_arr = []
                #print('Sending Message message from Client')
                if len(msg) > 140:
                    x = pickle.dumps(msg)
                    sending_arr = split_pickle(x)
                else:
                    sending_arr.append(Bytes_Segment(b'0x02', 1, 1, data.data))
                for i in range(0, len(sending_arr)):
                    bytes_obj = pickle.dumps(sending_arr[i])
                    device.send_data(remote_device, bytes_obj)
                rcv_bytes = device.read_data(5)
                if rcv_bytes is not None:
                    rcv = pickle.loads(rcv_bytes.data)
                    print('MSG rcv: {0:}, expected "ACK"'.format(rcv))
                    if rcv == 'ACK':
                        sent = True
                        #device.flush_queues()
                        #print('MSG complete')
                        return 'ACK'
                    else:
                        print('Distress MSG transfer failed')
                        return 'ERROR'
            except TimeoutException:
                continue
            
    if data.data_type == 'gps':
        #print('Sending gps from write()')
        msg = data.data
        sending_arr = []
        #print('Sending GPS message from Client')
        if len(msg) > 140:
            x = pickle.dumps(msg)
            sending_arr = split_pickle(x)
        else:
            sending_arr.append(Bytes_Segment(b'0x03', 1, 1, data.data))
        
        sent = False
        while(not sent):
            try:
                for i in range(0, len(sending_arr)):
                    bytes_obj = pickle.dumps(sending_arr[i])
                    device.send_data(remote_device, bytes_obj)

                rcv_bytes = device.read_data(2)
                if rcv_bytes is not None:
                    rcv = pickle.loads(rcv_bytes.data)
                            
                    #print('MSG rcv: {0:}'.format(rcv))
                    #print('EXIT rcv: {0:}'.format(rcv))
                    if rcv == 'ACK':
                        #print('EXIT complete')
                        return 'ACK'
                    else:
                        print('GPS transfer failed')
                        return 'ERROR'
            except TimeoutException:
                continue;

    if data.data_type == 'exit':
        msg = data.data
        sending_arr = []
        print('Sending EXIT message from Client')
        if len(msg) > 140:
            x = pickle.dumps(msg)
            sending_arr = split_pickle(x)
        else:
            sending_arr.append(Bytes_Segment(b'0x00', 1, 1, data.data))
        for i in range(0, len(sending_arr)):
            bytes_obj = pickle.dumps(sending_arr[i])
            device.send_data(remote_device, bytes_obj)
            
        while (rcv != 'ACK'):
            rcv_bytes = device.read_data(2)
            if rcv_bytes is not None:
                rcv = pickle.loads(rcv_bytes.data)
                
        #print('EXIT rcv: {0:}'.format(rcv))
        if rcv == 'ACK':
            #print('EXIT complete')
            return 'ACK'
        else:
            print('EXIT transfer failed')
            return 'ERROR'  
    else:
        print('Unknown data_type to send via XBee: {0:}'.format(data))
        return 'ERROR'

def main(gps_queue_out, audio_queue_in, audio_queue_out, ui_queue_in, ui_queue_out):

    print('Begin Wireless')
        
    device = XBeeDevice('/dev/ttyUSB0', 230400)

    device.open()
    device.flush_queues()
    
    remote_addr = '0013A2004155E2A6'
    remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(remote_addr))
    last_sent = datetime.datetime.timestamp(datetime.datetime.now())
    while(True):
        #print('Trying the ui_queue.get()')
        try:
            distress_msg = ui_queue_out.get(block=False) # Distress messages?
            #print('Got distress_msg from queue')
            if distress_msg is not None:
                if distress_msg == 'exit':
                    print('Exit command recieved, sending termination message to remote devices')
                    result = xbee_write(device, remote_device, data_segment)
                    if result != 'ACK':
                        print('Data_Segment: {0:} failed to send, remote devices not commanded to exit.\n Exiting...'.format(data_segment))         
                        device.close()
                        return
                    print('Exit sucessfully sent from client to server')
                    
                if distress_msg == 'Distress beacon active':
                    device_id = '0013A2004155E2AB'
                    date_time = datetime.datetime.utcfromtimestamp(0)
                    gps = '150.112,-45.555' # Should read latest GPS stamp from benn_gps??
                    data_segment = Data_Segment('distress','0013A2004155E2AB' + ',' + str(datetime.datetime.timestamp(datetime.datetime.now())) + ',' + '150.111,-45.444')
                    #print('Sending distress to xbee_write()')
                    result = xbee_write(device, remote_device, data_segment) # Write distress to xbee
                    if result != 'ACK':
                        print('Distress Data_Segment: {0:} failed to send, dropping packet'.format(distress_segment))
                    #print('Distress sucessfully sent from client to server')
                    
        except queue.Empty:
            pass
            #print('Empty ui_queue, continuing')
        
        #print('Trying the gps_queue.get()')
        try:
            gps_msg = gps_queue_out.get(block=False)
            #print('Got data_segment from gps_queue_out: {0:}'.format(gps_msg))
            if gps_msg is not None:
                now = datetime.datetime.timestamp(datetime.datetime.now())
                if now - last_sent > 15:
                    last_sent = now
                    data_segment = Data_Segment('gps', gps_msg.data)
                    print('Sending gps to xbee_write()')
                    result = xbee_write(device, remote_device, data_segment)
                    if result != 'ACK':
                        print('GPS Data_Segment: {0:} failed to send, dropping packet'.format(data_segment))
                    #print('GPS sucessfully sent from client to server')
        except queue.Empty:
            pass
            #print('Empty gps queue, continuing')
        
        #print('Trying the audio_out.get()')
        try:
            audio_file = audio_queue_out.get(block=False)
            print('Got filename from audio_queue_out: {0:}'.format(audio_file))
            if audio_file is not None:
                data_segment = Data_Segment('audio', audio_file)
                #print('Sending audio to xbee_write()')
                result = xbee_write(device, remote_device, data_segment)
                if result != 'ACK':
                    print('Audio Data_Segment: {0:} failed to send, dropping packet'.format(data_segment))
                #print('Audio sucessfully sent from client to server')
        except queue.Empty:
            pass
            #print('Empty gps queue, continuing')        
        
        print('xbee_read()')
        data_segment = xbee_read(device) # This device
        if data_segment is not None:
    
            if data_segment.data_type == 'audio':
                audio_queue_in.put(data_segment.data) # .data = filename

            if data_segment.data_type == 'message':
                ui_queue_in.put(data_segment.data) # .data = msg string

        elif data_segment.data_type == 'TIMEOUT':
            print('Timeout at Client wireless read(), retrying')
            continue
        elif data_segment.data_type == 'ERROR':
            print('XBee read error in main()')
            continue

        else:
            # Probably shutdown signal, so exit
            print('Shutdown signal at wireless read(), exiting')
            device.close()
            return
            
    print('End wireless')
