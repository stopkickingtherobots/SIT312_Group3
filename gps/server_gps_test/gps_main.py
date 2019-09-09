from multiprocessing import Process, Queue # Used for multiprocessing
import time
from pi_gps import main as pi_main
from server_gps import main as server_main

if __name__ == "__main__":

    gps_queue = Queue()

    gps_pi = Process(target = pi_main, args = (gps_queue,))
    gps_server = Process(target = server_main, args = (gps_queue,))

    gps_pi.start()
    gps_server.start()

    # Give the processes time to start/run
    time.sleep(1)

    while gps_pi.is_alive() or gps_server.is_alive():
    
        # Sleep reduces CPU load for essential while(true) loop
        time.sleep(2)

    print('\nAll running processes finished -------------------------------------\n')