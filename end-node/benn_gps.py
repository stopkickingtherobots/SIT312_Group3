from multiprocessing import Process, Queue # Used for multiprocessing
import time

def get_gps():

    # Place code here to collect GPS data
    # Return type may vary (utilising Data_Segment), 
    # str return used for demonstration.
    
    lat = 150.5
    lon = -45.4

    msg = str(lat) + ',' + str(lon)

    return msg

def main(gps_queue_out):
    print('Begin gps')

    #while(True): # Normally this will be an infinite loop
        #gps_msg = get_gps()

        #gps_queue_out.put(gps_msg)

    gps_msg = get_gps()

    gps_queue_out.put(gps_msg)

    print('End gps')