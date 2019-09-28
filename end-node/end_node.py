from multiprocessing import Process, Queue # Used for multiprocessing
import time
from andrew_wireless import main as wireless_main
from benn_gps import main as gps_main
from ian_ui import main as ui_main
from ui_display import main as ui_display
from sarah_audio import main as audio_main

if __name__ == "__main__":

    gps_queue = Queue(maxsize=1)

    audio_queue_in = Queue()
    audio_queue_out = Queue()

    ui_queue_in = Queue()
    ui_queue_out = Queue()    

    wireless = Process(target = wireless_main, args = (gps_queue, audio_queue_in, audio_queue_out, ui_queue_in, ui_queue_out,))

    gps = Process(target = gps_main, args = (gps_queue,))

    ui = Process(target = ui_main, args=(ui_queue_in, ui_queue_out,))

    audio = Process(target = audio_main, args = (audio_queue_in, audio_queue_out,))

    ui_display = Process(target = ui_display)

<<<<<<< HEAD
    wireless.start()   
    #print('Started Wireless')
    #time.sleep(0.5) 
=======
    wireless.start()    
>>>>>>> 536bb62244a04a7ad2148b81b56f06155b3e39bd
    gps.start()
    #print('Started gps')
    #time.sleep(0.5)
    ui.start()
    #print('Started ui')
    #time.sleep(0.5)
    audio.start()
<<<<<<< HEAD
    #print('Started audio')
    #time.sleep(0.5)
    ui_display.start()
    #print('Started ui_display')
    #time.sleep(0.5)
=======
    ui_display.start()
>>>>>>> 536bb62244a04a7ad2148b81b56f06155b3e39bd

    # Give the processes time to start/run
    time.sleep(1)

    while wireless.is_alive() or gps.is_alive() or ui.is_alive() or audio.is_alive():
    
        # Sleep reduces CPU load for essential while(true) loop
        time.sleep(2)

    print('\nProducer and Consumer processes ended -------------------------------------\n')
