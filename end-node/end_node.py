from multiprocessing import Process, Queue # Used for multiprocessing
import time
from andrew_wireless import main as wireless_main
from benn_gps import main as gps_main
from ian_ui import main as ui_main
from sarah_audio import main as audio_main

if __name__ == "__main__":

    gps_queue = Queue()

    audio_queue_in = Queue()
    audio_queue_out = Queue()

    ui_queue_in = Queue()
    ui_queue_out = Queue()    

    wireless = Process(target = wireless_main, args = (gps_queue,audio_queue_in, audio_queue_out, ui_queue_in, ui_queue_out,))

    gps = Process(target = gps_main, args = (gps_queue,))

    ui = Process(target = ui_main, args=(ui_queue_in, ui_queue_out,))

    audio = Process(target = audio_main, args = (audio_queue_in, audio_queue_out,))

    wireless.start()    
    gps.start()
    ui.start()
    audio.start()

    # Give the processes time to start/run
    time.sleep(1)

    while wireless.is_alive() or gps.is_alive() or ui.is_alive() or audio.is_alive():
    
        # Sleep reduces CPU load for essential while(true) loop
        time.sleep(2)

    print('\nProducer and Consumer processes ended -------------------------------------\n')