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
import lzma, bz2
import zstandard as zstd
from sys import getsizeof
import math
from pydub import AudioSegment
from scipy import signal
from timeit import default_timer as timer # Used to report processing time
import binascii

@dataclass
class Bytes_Segment:
    data_type: numpy.byte
    sequence: numpy.uint8
    total_sequence: numpy.uint8
    data: str

def split_pickle(pickled):

    print('\nbytes    length: {0:}'.format(len(pickled)))

    compressed_bytes = lzma.compress(pickled)

    print('    lzma length: {0:}'.format(len(compressed_bytes)))

    compressed_bytes = bz2.compress(pickled)

    print('    bz2  length: {0:}'.format(len(compressed_bytes)))

    cctx = zstd.ZstdCompressor()
    compressed_bytes = cctx.compress(pickled)

    print('    zstd length: {0:}\n\n'.format(len(compressed_bytes)))

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

    print('bytes    length: {0:}'.format(len(pickled)))
    print('compress length: {0:}'.format(len(compressed_bytes)))
    print('num_segments ceil: {0:}'.format(num_segments))
    print('Byte_piece size: {0:}'.format(getsizeof(byte_piece)))
    print('Data_Segment size: {0:}'.format(getsizeof(b)))

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

def build_audio_from_compressed(segment_arr):
    size = segment_arr[0].total_sequence

    result = numpy.empty(size, dtype=list)
    result = b''

    for i in range(0, len(segment_arr)):
        result += segment_arr[i].data

    decompressed_result = lzma.decompress(result)

    filename = 'test.mp3'

    fout = open(filename, 'wb')
    fout.write(decompressed_result)
    fout.close()

    wave_data = AudioSegment.from_file('test.mp3').get_array_of_samples()

    print('recv compress length: {0:}'.format(len(result)))
    print('recv bytes    length: {0:}'.format(len(decompressed_result)))
    print('Array of samples server: {0:}'.format(len(wave_data)))

    return filename

def prepare_audio_no_pickle_nohex(filename):

    with open(filename, 'rb') as f:
        content = f.read()

    print('Content length: {0:}'.format(len(content)))

    recording_arr = split_pickle(content)

    print('Array length: {0:}'.format(len(recording_arr)))

    return recording_arr

resamples = resample_audio('raw.wav') # Sarah's example; typical - may change
'''
print('\nTesting pickle code\n')

prepared_audio = prepare_audio('resample.mp3')

print('\nTesting no pickle code\n')

prepared_audio_no_pickle = prepare_audio_no_pickle('resample.mp3')
'''
print('\nTesting no pickle no hex code\n')

prepared_audio_no_pickle_nohex = prepare_audio_no_pickle_nohex('resample.mp3')

build_audio_from_compressed(prepared_audio_no_pickle_nohex)
