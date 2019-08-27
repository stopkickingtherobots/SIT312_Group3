import RPi.GPIO as GPIO
import pyaudio
import time
import wave
import os

STOP = 23
START = 24
stopRecording = False
messageNumber = 1

GPIO.setmode(GPIO.BCM)

GPIO.setup(STOP, GPIO.IN)
GPIO.setup(START, GPIO.IN)

form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1                # 1 channel
samp_rate = 44100        # 44.1kHz sampling rate
chunk = 4096             # 2^12 samples for buffer
record_secs = 10         # seconds to record
dev_index = 2            # device index, found by p.get_device_info_by_index(i)

time.sleep(2)

try:
    while True:
    
        wav_output_filename = 'Message_' # start of name of .wav file
    
        # when the start button is pressed
        if (GPIO.input(START) == 0):
            print "Initiate recording ..."
            
            wav_output_filename += str(dreamNumber) + '.wav'
            
            # create pyaudio instantiation
            audio = pyaudio.PyAudio()

            # create pyaudio stream
            stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=chunk)
            
            frames = []
            
            # until the stop button is pressed, keep recording
            while (stopRecording == False):
                # append audio chunks to frame array
                data = stream.read(chunk,exception_on_overflow = False)
                frames.append(data)
                
                # if the stop button is pressed, stop the recording loop
                if (GPIO.input(STOP) == 0):
                    stopRecording = True
                    print "Cease recording " + wav_output_filename
            
            time.sleep(1)
            
            # stop the stream, close it, and terminate the pyaudio instantiation
            print "Closing stream"
            stream.stop_stream()
            stream.close()
            audio.terminate()

            # save the audio frames as .wav file
            print "Saving Audio as " + wav_output_filename
            wavefile = wave.open(wav_output_filename,'wb')
            wavefile.setnchannels(chans)
            wavefile.setsampwidth(audio.get_sample_size(form_1))
            wavefile.setframerate(samp_rate)
            wavefile.writeframes(b''.join(frames))
            wavefile.close()
            print wav_output_filename + " saved"
            
            stopRecording = False
            messageNumber += 1
    
except KeyboardInterrupt:
    GPIO.cleanup()

GPIO.cleanup()