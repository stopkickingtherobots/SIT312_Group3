from multiprocessing import Process, Queue # Used for multiprocessing
import time

def record_audio():

    # Pseudocode to record audio when record button is pressed.
    # Return value will be array of raw audio; or       - no saved audio
    # Return value will be filename of recorded audio   - saved audio (for auditing)
    #audio = pyaudio.read()

    return ''

def play_audio(audio):

    # Pseudocode to play audio.
    # Input will be raw audio array; or         - no saved audio
    # Input will be filename of recorded audio  - saved audio
    # Unsure of integration with UI (play, pause, etc); 
    # may merge with ian_ui.py in future.
    #pyaudio.play(audio)

    return ''

def main(audio_queue_out, audio_queue_in):
    print('Begin audio')

    audio = audio_queue_in.get(2)
    print('got audio')
    if audio is not None:
        play_audio(audio)

    print('End audio')