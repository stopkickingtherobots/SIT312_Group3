from multiprocessing import Process, Queue # Used for multiprocessing
import time

def main(gps_queue, distress_queue, message_queue, audio_queue_in, audio_queue_out):

    print('Begin wireless')

    print('End wireless')