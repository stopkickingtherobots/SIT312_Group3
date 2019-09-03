import os
import re

mylines = []                                    # Declare an empty list
with open ('gps_data.txt', 'rt') as inFile:     # Open gps_data.txt for reading text.
    for line in inFile:                         # For each line of text,
        mylines.append(line)                    # add that line to the list.
inFile.close()

outFile = open("latitude.txt", "w")
for element in mylines:
    match = re.search(r'Lat:-(\d+).(\d+)',element)
    if match:
        str = match.group()
        str = str.replace('Lat:', '')
        outFile.write(str)
        outFile.write(", ")
outFile.close()

outFile = open("longitude.txt", "w")
for element in mylines:
    match = re.search(r'Lon:(\d+).(\d+)',element)
    if match:
        str = match.group()
        str = str.replace('Lon:', '')
        outFile.write(str)  
        outFile.write(", ")
outFile.close()

with open("latitude.txt", 'rb+') as filehandle:
    filehandle.seek(-2, os.SEEK_END)
    filehandle.truncate()
    filehandle.close()

with open("longitude.txt", 'rb+') as filehandle:
    filehandle.seek(-2, os.SEEK_END)
    filehandle.truncate()
    filehandle.close()