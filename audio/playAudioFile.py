import pygame

file_name = 'Winter.wav'

pygame.mixer.init()                     # initialise player
pygame.mixer.music.load(file_name)      # play specified file from specific location

pygame.mixer.music.play()               # begin playing file
print "Audio file playing"

# continue playing until track has finished
while pygame.mixer.music.get_busy() == True:
    continue

print "Audio file finished"