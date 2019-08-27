from multiprocessing import Process, Queue 
import serial
import time
import pickle
from digi.xbee.devices import XBeeDevice
from digi.xbee.devices import RemoteXBeeDevice
from digi.xbee.devices import XBee64BitAddress
from digi.xbee.exception import TimeoutException
import sys
import serial

def gps_locate(ser):

    while(True):
              
        x = ser.readline()  
        x = x.decode()         
        x_arr = x.split(',')    
        if 'GNGGA' in x:
            print(x_arr)
            return x_arr[2],x_arr[4] #GNGGA Lat, Long
   
def xbee_slave():

    # Slave device - responds to requests from Master (Remote Device)
    
    # Set up the GPS serial device
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.port = '/dev/ttyS0'
    ser.timeout = 1
    ser.open()
    
    # Set up the XBee serial device
    device = XBeeDevice('/dev/ttyUSB0', 230400)
    remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string('')) # Insert remote address
    device.open()
 
    while True:

        lat,lon = gps_locate(ser)

        try:
            rcv = device.read_data(1) # Listen for 1 seconds (then sleep, to save power?)
        
        except TimeoutException:
            continue

        if rcv is None:   
            continue    

        if pickle.loads(rcv.data) == 'Alive?':
            msg = 'Alive recieved at: ' + str(time.time()) + '\tLocation: {0:} {1:}'.format(lat,lon)
            pickled = pickle.dumps(msg)
            device.send_data(remote_device, pickled)  

        unpickled = pickle.loads(rcv.data)   
        print('COM4 (Slave) recieved: \n\tValue: {0:}\n'.format(unpickled))        
        time.sleep(5) #device sleeps for 5 seconds.

    device.close()

if __name__ == "__main__":

    consumer = Process(target = xbee_slave, args = ())

    consumer.start()

    # Give the processes time to start/run
    time.sleep(1)

    while consumer.is_alive():
    
        # Sleep reduces CPU load for essential while(true) loop
        time.sleep(2)

    if consumer.is_alive():

        consumer.close()

    print('\nConsumer processes ended -------------------------------------\n')