import pyaudio      # Connects with Portaudio for audio device streaming
import wave         # Used to save audio to .wav files
import collections  # Used for Double ended Queue (deque) structure
#import msvcrt       # Used for non-blocking keyboard event
from scipy import signal
import numpy
#import librosa

from pydub import AudioSegment

# Define Audio characteristics
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 1024
RECORD_SECONDS = 2
WAVE_OUTPUT_FILENAME = "file.wav"
FLAC_OUTPUT_FILENAME = "file.flac"
AAC_OUTPUT_FILENAME = "file.aac"

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
recording.export("raw.wave", format="wav")     # Raw audio at 161KB per 10 seconds
recording.export("raw.flac", format = "flac")  # ~50% reduction in file size; 91KB per 10 seconds
recording_samples = recording.get_array_of_samples()
recording_resample = signal.resample(recording_samples, 8000)

resamples = b''
for i in range(0, len(recording_resample)):
    resamples += (int(recording_resample[i].astype(numpy.int16)/32).to_bytes(4, byteorder='big', signed=True))
#print(resamples)

newrecording = AudioSegment(resamples, sample_width=2, frame_rate=8000, channels=1)
newrecording.export("resample.wav", format="wav")     # Raw audio at 161KB per 10 seconds
newrecording.export("resample.flac", format = "flac")  # ~50% reduction in file size; 91KB per 10 seconds
#newrecording.export(AAC_OUTPUT_FILENAME, format = "aac")   # Currently produces an error - unresolved github issue

# Desktop conversion results in 53KB; ~70% reduction
# C:\ > ffmpeg -i file.wav -codec:a aac file.aac 

print('Done export')
