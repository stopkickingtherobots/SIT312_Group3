from multiprocessing import Process, Queue # Used for multiprocessing
import time
from client import main as xbee_client
from server import main as xbee_server

if __name__ == "__main__":

    server_proc = Process(target = xbee_server, args = ())
    client_proc = Process(target = xbee_client, args = ())

    server_proc.start()
    client_proc.start()

    # Give the processes time to start/run
    time.sleep(1)

    while server_proc.is_alive() or client_proc.is_alive():
    
        # Sleep reduces CPU load for essential while(true) loop
        time.sleep(2)

    print('\nAll running processes finished -------------------------------------\n')