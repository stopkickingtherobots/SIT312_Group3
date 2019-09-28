from multiprocessing import Process, Queue # Used for multiprocessing
import serial
import time

def readlineCR(port):
    rv = ""
    while True:
        ch = port.read()
        if ch==b'\r' or ch==b'':
            return rv
        #print('Read from port')
        rv += ch.decode()
        #print('rv: {0:} ch: {1:}'.format(rv,ch))

def xbee_0():
    port = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=None)
    msg = "Test from TTYUSB0\r"
    while True:
        time.sleep(1)
        #print('Sending from ttyUSB0')
        port.write(msg.encode())
        rcv = readlineCR(port)
        print("TTYUSB0 received:" + repr(rcv))
        time.sleep(2)
'''
def xbee_1():
    port = serial.Serial("COM4", baudrate=9600, timeout=None)
    msg = "Test from COM4\r"
    while True:
        time.sleep(1)
        #print('Sending from COM4')
        port.write(msg.encode())
        rcv = readlineCR(port)
        print("COM4 received:" + repr(rcv))
        time.sleep(2)       
'''
if __name__ == "__main__":

    producer = Process(target = xbee_0, args = ())

    #consumer = Process(target = xbee_1, args = ())

    producer.start()
    #consumer.start()

    # Give the processes time to start/run
    time.sleep(1)

    #while producer.is_alive() or consumer.is_alive():
    while producer.is_alive():
        
        # Sleep reduces CPU load for essential while(true) loop
        time.sleep(2)

    #if (producer.is_alive() and consumer.is_alive()):
    if (producer.is_alive()):
    
        producer.close()
        #consumer.close()

    print('\nProducer processes ended -------------------------------------\n')