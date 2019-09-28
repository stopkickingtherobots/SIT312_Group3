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

recording = AudioSegment.from_file("short.wav").get_array_of_samples()


recording_arr = split_audio(recording)

send = []

for i in range(0, len(recording_arr)):
    bytes_obj = pickle.dumps(recording_arr[i])
    send.append(bytes_obj)
    #print('Size: {0:}'.format(sys.getsizeof(bytes_obj)))

recieve = []

for i in range(0,len(send)):
    deserial = pickle.loads(send[i])
    recieve.append(deserial)

result_arr = build_data(recieve)
print('Result_arr: {0:}'.format(result_arr))

print('Result_arr len: {0:}'.format(len(result_arr)))

#for i in range(0, len(result_arr)):
#    print(result_arr[i])

newrecording = AudioSegment(result_arr, sample_width=2, frame_rate=8000, channels=1)
newrecording.export('file.flac', format = "flac")


