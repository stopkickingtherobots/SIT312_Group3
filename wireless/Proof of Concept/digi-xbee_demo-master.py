from multiprocessing import Process, Queue 
import serial
import time
import pickle
from digi.xbee.devices import XBeeDevice
from digi.xbee.devices import RemoteXBeeDevice
from digi.xbee.devices import XBee64BitAddress
from digi.xbee.exception import TimeoutException
import sys

def xbee_master():

    #Master device - polls remote device. 

    device = XBeeDevice('COM4', 230400)

    remote_addr = '0013A2004155E2A6'
    remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(remote_addr))

    device.open()

    # Represents the largest single 'packet' that can be transmitted.
    #msg = b'0' * 249

    msg = "Alive?"
    pickled = pickle.dumps(msg)

    while True:           
        try:
            rcv = device.read_data(1)

            if rcv is None:
                continue
            
            print('COM4 (Master) recieved:\n\tDevice: {0:}\n\t Value: {1:}\n'.format(remote_addr, pickle.loads(rcv.data)))
        
        except TimeoutException:
            device.send_data(remote_device, pickled)  
            continue

        device.send_data(remote_device, pickled)  
        
    device.close()

if __name__ == "__main__":

    producer = Process(target = xbee_master, args = ())

    producer.start()

    # Give the processes time to start/run
    time.sleep(1)

    while producer.is_alive():
    
        # Sleep reduces CPU load for essential while(true) loop
        time.sleep(2)

    if (producer.is_alive()):
        
        producer.close()

    print('\nProducer processes ended -------------------------------------\n')