import pyaudio      # Connects with Portaudio for audio device streaming
import wave         # Used to save audio to .wav files
import collections  # Used for Double ended Queue (deque) structure
#import msvcrt       # Used for non-blocking keyboard event

from pydub import AudioSegment

# Define Audio characteristics
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000
CHUNK = 1024
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "file.wav"
FLAC_OUTPUT_FILENAME = "file.flac"
AAC_OUTPUT_FILENAME = "file.aac"

audio = pyaudio.PyAudio()
 
# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,rate=RATE, input=True,frames_per_buffer=CHUNK)
                
print ('recording...')

data = stream.read(8 * CHUNK * RECORD_SECONDS)


print ('finished recording')

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()
 
waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(data)
waveFile.close()

# Pydub addition - will export raw audio - data - into specified formats.
newrecording = AudioSegment(data, sample_width=2, frame_rate=8000, channels=1)
newrecording.export(WAVE_OUTPUT_FILENAME, format="wav")     # Raw audio at 161KB per 10 seconds
newrecording.export(FLAC_OUTPUT_FILENAME, format = "flac")  # ~50% reduction in file size; 91KB per 10 seconds
#newrecording.export(AAC_OUTPUT_FILENAME, format = "aac")   # Currently produces an error - unresolved github issue

# Desktop conversion results in 53KB; ~70% reduction
# C:\ > ffmpeg -i file.wav -codec:a aac file.aac 

print('Done export')