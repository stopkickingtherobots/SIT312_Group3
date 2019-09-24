from multiprocessing import Process, Queue # Used for multiprocessing
import time
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Data_Segment:
    data_type: str
    data: str

def get_gps():

    # Place code here to collect GPS data
    # Return type may vary (utilising Data_Segment), 
    # str return used for demonstration.
    
    # https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/uart-serial
    
    # Will wait for a fix and print a message every second with the current location
    # and other details.
    import time
    import board
    import busio

    import adafruit_gps

    # for a computer, use the pyserial library for uart access
    import serial
    uart = serial.Serial("/dev/ttyUSB1", baudrate=9600, timeout=3000)

    # Create a GPS module instance.
    gps = adafruit_gps.GPS(uart, debug=False)

    # Turn on the basic GGA and RMC info (what you typically want)
    gps.send_command(b'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

    # Set update rate to once every 10 seconds (0.1hz)
    gps.send_command(b'PMTK220,10000')

    # Main loop runs forever printing the location, etc. every second.
    last_print = time.monotonic()
    while True:
        # Make sure to call gps.update() every loop iteration and at least twice
        # as fast as data comes from the GPS unit (usually every second).
        # This returns a bool that's true if it parsed new data (you can ignore it
        # though if you don't care and instead look at the has_fix property).
        gps.update()
        # Every second print out current location details if there's a fix.
        current = time.monotonic()
        if current - last_print >= 1.0:
            last_print = current
            if not gps.has_fix:
                # Try again if we don't have a fix yet.
                #print('Waiting for fix...')
                continue
            # We have a fix! (gps.has_fix is true)
            # Print out details about the fix like location, date, etc.
            '''
            print('=' * 40)  # Print a separator line.
            print('Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}'.format(
                gps.timestamp_utc.tm_mon,   # Grab parts of the time from the
                gps.timestamp_utc.tm_mday,  # struct_time object that holds
                gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                gps.timestamp_utc.tm_hour,  # not get all data like year, day,
                gps.timestamp_utc.tm_min,   # month!
                gps.timestamp_utc.tm_sec))
            print('Latitude: {0:.6f} degrees'.format(gps.latitude))
            print('Longitude: {0:.6f} degrees'.format(gps.longitude))
            print('Fix quality: {}'.format(gps.fix_quality))
            '''
            # Some attributes beyond latitude, longitude and timestamp are optional
            # and might not be present.  Check if they're None before trying to use!
            #if gps.altitude_m is not None:
            #   print('Altitude: {} meters'.format(gps.altitude_m))
    
            # msg = str(gps.latitude) + ',' + str(gps.longitude)
            # return msg

            
            # Write to text file 
            timestring = '{}/{}/{} {:02}:{:02}:{:02}'.format(gps.timestamp_utc.tm_year, gps.timestamp_utc.tm_mon,gps.timestamp_utc.tm_mday,gps.timestamp_utc.tm_hour, gps.timestamp_utc.tm_min, gps.timestamp_utc.tm_sec)
                
            #print(timestring)
            try:
                datetime_obj = datetime.strptime(timestring, '%Y/%m/%d %H:%M:%S')
            
                #print('timestamp: {0:}'.format(datetime_obj.timestamp()))
                msg = Data_Segment('gps', str(gps.latitude) +',' + str(gps.longitude) +','+str(datetime_obj.timestamp()))
                
                file = open("gps_coordinates.txt","w") 
                file.write(str(gps.latitude) + ",  " + str(gps.longitude) + ",  " 
                + '{}/{}/{} {:02}:{:02}:{:02}'.format(
                    gps.timestamp_utc.tm_year, 
                    gps.timestamp_utc.tm_mon,   
                    gps.timestamp_utc.tm_mday,                   
                    gps.timestamp_utc.tm_hour,  
                    gps.timestamp_utc.tm_min,   
                    gps.timestamp_utc.tm_sec)) 
                file.close()
                
                #print('GPS time: {0:}'.format(gps.timestamp_utc))
                return msg
            except ValueError:
                pass
            #gps_queue.put(msg)  
            return None

def main(gps_queue_out):
    print('Begin gps')

    while(True): 
        gps_msg = get_gps()
        if gps_msg is not None:

            gps_queue_out.put(gps_msg)

    print('End gps')
