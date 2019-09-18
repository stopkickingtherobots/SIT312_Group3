from multiprocessing import Process, Queue # Used for multiprocessing
import time

def main(audio_queue_in, audio_queue_out):
    print('Begin server audio')

    while(True):

        msg = audio_queue_in.get()

        print(msg)

    print('End server audio')