import pygame
import time

pygame.mixer.pre_init(8000,-16, 1, 1024)
pygame.mixer.init()
#audio = pygame.mixer.Sound('/audio/1569057162.238353.ogg')
audio = pygame.mixer.Sound('audio/1569064235.332012.wav')
pygame.mixer.Sound.play(audio)
#audio.play()
time.sleep(10)
