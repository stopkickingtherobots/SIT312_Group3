<<<<<<< HEAD
from multiprocessing import Process, Queue # Used for multiprocessing
import time
from andrew_wireless import main as wireless_main
from benn_gps import main as gps_main
from server_gui import main as server_main

if __name__ == "__main__":

    gps_queue = Queue()
    gps_gui_queue = Queue()

    audio_queue_in = Queue()
    audio_queue_out = Queue()

    distress_queue = Queue()
    message_queue = Queue()

    wireless = Process(target = wireless_main, args = (gps_queue, distress_queue, message_queue, audio_queue_in, audio_queue_out,))

    gps = Process(target = gps_main, args = (gps_queue,gps_gui_queue))

    gui = Process(target = server_main, args = (distress_queue, message_queue, audio_queue_out, audio_queue_in))

    wireless.start()    
    gps.start()
    gui.start()

    # Give the processes time to start/run
    time.sleep(1)

    while wireless.is_alive() or gps.is_alive() or gui.is_alive():
    
        # Sleep reduces CPU load for essential while(true) loop
        time.sleep(2)

=======
from multiprocessing import Process, Queue # Used for multiprocessing
import time
from andrew_wireless import main as wireless_main
from benn_gps import main as gps_main
from sarah_audio import main as audio_main
from server_gui import main as server_main

if __name__ == "__main__":

    gps_queue = Queue()
    gps_gui_queue = Queue()

    audio_queue_in = Queue()
    audio_queue_out = Queue()

    distress_queue = Queue()
    message_queue = Queue()

    wireless = Process(target = wireless_main, args = (gps_queue, distress_queue, message_queue, audio_queue_in, audio_queue_out,))

    gps = Process(target = gps_main, args = (gps_queue,gps_gui_queue))

    audio = Process(target = audio_main, args = (audio_queue_in, audio_queue_out))

    gui = Process(target = server_main, args = (distress_queue, message_queue))

    wireless.start()    
    gps.start()
    audio.start()
    gui.start()

    # Give the processes time to start/run
    time.sleep(1)

    while wireless.is_alive() or gps.is_alive() or audio.is_alive() or gui.is_alive():
    
        # Sleep reduces CPU load for essential while(true) loop
        time.sleep(2)

>>>>>>> 536bb62244a04a7ad2148b81b56f06155b3e39bd
    print('\nAll running processes finished -------------------------------------\n')