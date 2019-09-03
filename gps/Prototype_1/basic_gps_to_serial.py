import serial
import pynmea2
 
port = "/dev/serial0"

def parseGPS(str):
    if str.find('GGA') > 0:
        msg = pynmea2.parse(str)

        latitude = (float(msg.lat))/100    
        longitude = (float(msg.lon))/100 

        latitude_direction = msg.lat_dir
        longitude_dirction = msg.lon_dir

        if latitude_direction == 'S':
                latitude *= -1

        if longitude_dirction == 'W':
                longitude *= -1

        print "Timestamp:%s -- Lat:%s -- Lon:%s -- Altitude:%s %s -- Satellites:%s" % (msg.timestamp,latitude,longitude,msg.altitude,msg.altitude_units,msg.num_sats)
  
serialPort = serial.Serial(port, baudrate = 9600, timeout = 0.5)
while True:
    str = serialPort.readline()
    parseGPS(str)