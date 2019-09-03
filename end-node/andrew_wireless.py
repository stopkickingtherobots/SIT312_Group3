from multiprocessing import Process, Queue # Used for multiprocessing
import time

def main(gps_queue_in, audio_queue_in, audio_queue_out, ui_queue_in, ui_queue_out):

    print('Begin wireless')

    ui_queue_out.put('Hello from andrew_wireless.py')

    audio_queue_out.put('')

    gps = gps_queue_in.get(2)

    print('GPS: {0:}'.format(gps))

    distress = ui_queue_in.get(2)

    print('Message: {0:}'.format(distress))

    print('End wireless')