# import gmplot package 
#import gmplot

lat=open("latitude.txt", "r")  

try:  	
	latitude_list = eval('[' + lat.read() + ']')
finally:
	lat.close()

long=open("longitude.txt", "r")  

try:  	
	longitude_list = eval('[' + long.read() + ']')
	# longitude_list.strip()
finally:
	lat.close()

gmap3 = gmplot.GoogleMapPlotter(-32.93933025, 151.666152225, 18) 

# scatter method of map object 
# scatter points on the google map 
gmap3.scatter( latitude_list, longitude_list, '# FF0000', size = 40, marker = False ) 

# Plot method Draw a line in 
# between given coordinates 
gmap3.plot(latitude_list, longitude_list, 
		'cornflowerblue', edge_width = 2.5) 

gmap3.draw( "C:/Users/benn/Desktop/gps_project/base_maps/mapfingers_crossed.html" ) 