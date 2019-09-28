from tkinter import *
from tkinter import ttk
import tkinter.font
from time import localtime, strftime, sleep
from PIL import ImageTk, Image
from pijuice import PiJuice
import RPi.GPIO as GPIO
import json
from pathlib import Path
import geopy.distance
from time import strftime, strptime, localtime, gmtime, mktime
import pygame
import pyaudio      # Connects with Portaudio for audio device streaming
import wave         # Used to save audio to .wav files
import collections  # Used for Double ended Queue (deque) structure
from scipy import signal
import numpy
from pydub import AudioSegment
from multiprocessing import Process
import time
import math
import wave
from scipy import signal
import struct


class deviceUI():
    def __init__(self):
        self.is_distress_active = False
        self.is_playing_audio = False
        self.is_paused = False
        self.is_input_enabled = True
        self.is_gps_connected = True
        self.is_basestation_connected = True      

        self.poi_range_threshold = 0.1 #Poi trigger radius in km
        self.current_track_idx = 0
        self.playback_list = []  
        self.player = pygame.mixer   
        pygame.mixer.pre_init(8000, -16, 1, 1024)
        pygame.mixer.init()   

        self.__initialise_hardware()
        self.__initialise_window()
        self.__load_graphics()
        self.__build_status_frame()
        self.__add_padding_frame()
        self.__build_header_frame("Messages")
        self.__build_messages_frame()
        self.build_messages_list()
        self.__add_padding_frame()
        self.__build_header_frame("Available Tracks")
        self.__build_tracklist_frame()
        self.__add_padding_frame()
        self.build_playback_list() 
        self.__build_playback_frame()
        self.__add_padding_frame()
        self.__build_control_frame() 
        self.current_track = dict(self.playback_list[0])

    def __initialise_hardware(self):        
        self.pijuice = PiJuice(1, 0x14)
        GPIO.setmode(GPIO.BOARD)
        self.mic_pin = 40
        GPIO.setup(self.mic_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.emergency_pin = 38
        GPIO.setup(self.emergency_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.piezo_pin = 37
        GPIO.setup(self.piezo_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.piezo_pin, 400)
        self.pwm.start(0)

    def __initialise_window(self):
        self.window = Tk()
        self.window.config(cursor='none')
        self.window.geometry('320x480')
        self.window['bg'] = "white"
        self.window.overrideredirect(True)
        self.window.title(' ')
        self.window.protocol("WM_DELETE_WINDOW", self.close)      

    def __load_graphics(self):
        self.battery_img = ImageTk.PhotoImage(Image.open("./resources/battery.png"))
        self.wifi_off_img = ImageTk.PhotoImage(Image.open("./resources/wifi_off.png"))
        self.gps_off_img = ImageTk.PhotoImage(Image.open("./resources/gps_off.png"))
        self.wifi_on_img = ImageTk.PhotoImage(Image.open("./resources/wifi_on.png"))
        self.gps_on_img = ImageTk.PhotoImage(Image.open("./resources/gps_on.png"))
        self.pause_icon = ImageTk.PhotoImage(Image.open("./resources/pause_icon.png"))
        self.play_icon = ImageTk.PhotoImage(Image.open("./resources/play_icon.png"))
        self.play_img = ImageTk.PhotoImage(Image.open("./resources/play_button.png"))
        self.pause_img = ImageTk.PhotoImage(Image.open("./resources/pause_button.png"))
        self.rewind_img = ImageTk.PhotoImage(Image.open("./resources/back_button.png"))
        self.skip_img = ImageTk.PhotoImage(Image.open("./resources/forward_button.png"))

    def __build_status_frame(self):
        self.status_font = tkinter.font.Font(family="Times New Roman", size=11, weight="bold")
        self.status_frame = Frame(self.window, borderwidth=1, relief="solid", bg="white")
        self.status_frame.pack(side=TOP)

        # date and time
        self.date_time_label = Label(self.status_frame, text=strftime("%H:%M  %d/%m/%Y", localtime()), font=self.status_font)
        self.date_time_label.pack(side=LEFT)

        # battery info
        battery_level = self.pijuice.status.GetChargeLevel()['data']
        self.battery_label = Label(self.status_frame, text=str(battery_level)+"%", font=self.status_font)
        self.battery_label.pack(side=RIGHT)        
        self.battery_img_label = Label(self.status_frame, image=self.battery_img)
        self.battery_img_label.pack(side=RIGHT)

        # wifi status        
        self.wifi_label = Label(self.status_frame, image=self.wifi_off_img)
        self.wifi_label.pack(side=RIGHT)

        # gps status        
        self.gps_label = Label(self.status_frame, image=self.gps_off_img)
        self.gps_label.pack(side=RIGHT)

    def __add_padding_frame(self):
        new_frame = Frame(self.window, height=20, bg="white")
        new_frame.pack()

    def __build_header_frame(self, text):
        header_frame = Frame(self.window, bg="white")
        header_frame.pack(side=TOP)
        header = Label(header_frame, text=text)
        header.pack()

    def __build_messages_frame(self):
        self.messages_frame = Frame(self.window, borderwidth=1, relief="solid", bg="white")
        self.messages_frame.pack(side=TOP, fill=X)
        self.message_scrollbar = Scrollbar(self.messages_frame)
        self.message_scrollbar.pack(side=RIGHT, fill=Y)
        self.messages_list = Listbox(self.messages_frame, yscrollcommand=self.message_scrollbar.set, width=300, height=5)
        self.messages_list.pack(side=LEFT, fill=BOTH)
        self.message_scrollbar.config(command=self.messages_list.yview)

    def __build_tracklist_frame(self):
        self.tracklist_frame = Frame(self.window, borderwidth=1, relief="solid")
        self.tracklist_frame.pack(side=TOP)
        self.tracklist_scrollbar = Scrollbar(self.tracklist_frame)
        self.tracklist_scrollbar.pack(side=RIGHT, fill=Y)
        self.tracklist_list = Listbox(self.tracklist_frame, selectmode=SINGLE, yscrollcommand=self.tracklist_scrollbar.set, exportselection=False, width=300, height=5)
        for t in self.playback_list:
            self.tracklist_list.insert(END, t["title"])
        self.tracklist_list.pack(side=LEFT, fill=BOTH)
        self.tracklist_list.activate(0)
        self.tracklist_scrollbar.config(command=self.tracklist_list.yview)

    def __build_playback_frame(self):
        self.playback_tracklist_frame = Frame(self.window)
        self.playback_tracklist_frame.pack()
        
        self.play_pause_display_icon = Label(self.playback_tracklist_frame, image=self.pause_icon, padx=10)
        self.play_pause_display_icon.pack(side=LEFT)

        self.playback_prog_bar = ttk.Progressbar(self.playback_tracklist_frame, orient="horizontal", length=150, mode="determinate")
        self.playback_prog_bar["value"] = 0
        self.playback_prog_bar["maximum"] = self.playback_list[0]["length"]

        self.playback_prog_bar.pack(side=LEFT)

        mins = self.playback_list[0]["length"]//60
        secs = self.playback_list[0]["length"] % 60

        self.playback_prog_label = Label(self.playback_tracklist_frame, text="0:00 / {0}:{1}".format(mins, secs))
        self.playback_prog_label.pack(side=LEFT)

        self.bottom_tracklist_frame = Frame(self.window)
        self.bottom_tracklist_frame.pack()
        self.track_label = Label(self.bottom_tracklist_frame, text=self.playback_list[0]["title"])

        self.track_label.pack(side=BOTTOM)

    def __build_control_frame(self):
        self.playback_control_frame = Frame(self.window)
        self.playback_control_frame.pack(side=BOTTOM)

        self.rewind_button = Button(self.playback_control_frame, image=self.rewind_img, command=self.rewind_track)
        self.rewind_button.pack(side=LEFT)

        self.play_pause_button = Button(self.playback_control_frame, image=self.play_img, command=self.play_pause_audio)
        self.play_pause_button.pack(side=LEFT)

        self.skip_button = Button(self.playback_control_frame, image=self.skip_img, command=self.skip_track)
        self.skip_button.pack(side=RIGHT)

    def start(self):
        self.window.after(5000, self.refresh_status_bar)
        self.window.after(100, self.monitor_input)
        self.window.after(1000, self.update_playback_progress)
        self.window.after(15000, self.build_playback_list)
        self.window.after(15000, self.build_messages_list)
        self.window.mainloop()

    def close(self):
        GPIO.cleanup()
        self.window.destroy()

    def refresh_status_bar(self):
        self.date_time_label.config(text=strftime("%H:%M  %d/%m/%Y", localtime()), font=self.status_font)

        battery_level = self.pijuice.status.GetChargeLevel()['data']
        self.battery_label.config(text=str(battery_level)+"%")

        if self.is_basestation_connected:
            self.wifi_label.configure(image=self.wifi_on_img)
            self.wifi_label.image = self.wifi_on_img
        else:
            self.wifi_label.configure(image=self.wifi_off_img)
            self.wifi_label.image = self.wifi_off_img
        if self.is_gps_connected:
            self.gps_label.configure(image=self.gps_on_img)
            self.gps_label.image = self.gps_on_img
        else:
            self.gps_label.configure(image=self.gps_off_img)
            self.gps_label.image = self.gps_off_img

        self.window.after(5000, self.refresh_status_bar)

    def record_voice_message(self):
        self.disable_controls()

        self.recording_window = Tk()
        self.recording_window.config(cursor='none')
        self.recording_window.geometry('320x480')
        self.recording_window['bg'] = "white"
        #self.recording_window.overrideredirect(True)
        self.recording_window.title(' ')
        self.recording_window.protocol("WM_DELETE_WINDOW", self.recording_window.destroy)           

        padding_frame = Frame(self.recording_window, height=100, bg="white")
        padding_frame.pack()

        self.recording_frame = Frame(self.recording_window, bg="white")
        self.recording_frame.pack(side=TOP)

        recording_font = tkinter.font.Font(family="Times New Roman", size=24, weight="bold")
        self.countdown_label = Label(self.recording_frame, text="", bg="white", font=recording_font)
        self.countdown_label.pack(side=TOP)        

        self.display_voice_message_warning_countdown(3)
        self.recording_window.mainloop()

    def display_voice_message_warning_countdown(self, countdown):
        self.countdown_label.config(text="Record message in {0}".format(countdown))

        if countdown == 0:         
            self.countdown_label.config(text="Record a 10 second message.")
            self.recording_window.update_idletasks()
            self.record_audio()
        else:
            self.recording_window.after(1000, lambda: self.display_voice_message_warning_countdown(countdown-1))
                  

    def disable_controls(self):
        self.rewind_button.config(state=DISABLED)
        self.play_pause_button.config(state=DISABLED)
        self.skip_button.config(state=DISABLED)
        self.is_input_enabled = False


    def enable_controls(self):
        self.rewind_button.config(state=NORMAL)
        self.play_pause_button.config(state=NORMAL)
        self.skip_button.config(state=NORMAL)
        self.is_input_enabled = True

    def play_pause_audio(self):
        if self.is_playing_audio:
            self.pause()
            self.is_paused = True
            self.is_playing_audio = False
            self.play_pause_button.configure(image=self.play_img)
            self.play_pause_button.image = self.play_img

            self.play_pause_display_icon.configure(image=self.pause_icon)
            self.play_pause_display_icon.image = self.pause_icon

        else:
            if self.is_paused:
                self.resume()
                self.is_paused = False
                self.is_playing_audio = True
            else:
                self.play()
                self.is_playing_audio = True
            self.play_pause_button.configure(image=self.pause_img)
            self.play_pause_button.image = self.pause_img

            self.play_pause_display_icon.configure(image=self.play_icon)
            self.play_pause_display_icon.image = self.play_icon


    def rewind_track(self):
        if self.playback_prog_bar["value"] < 2:
            self.current_track_idx = len(self.playback_list) -1 if self.current_track_idx == 0 else self.current_track_idx-1
            self.tracklist_list.activate(self.current_track_idx)
            text = self.playback_list[self.current_track_idx]["title"]
            self.track_label.config(text=text)
            self.current_track = dict(self.playback_list[self.current_track_idx])
            self.playback_prog_bar["maximum"] = self.current_track["length"]
            self.play()
        else:
            self.restart()
        self.playback_prog_bar["value"] = 0    


    def skip_track(self):       
        if self.current_track_idx == len(self.playback_list)-1:
            self.current_track_idx = 0
        else:
            self.current_track_idx += 1

        self.tracklist_list.activate(self.current_track_idx)
        text = self.playback_list[self.current_track_idx]["title"]
        self.track_label.config(text=text)        
        self.current_track = dict(self.playback_list[self.current_track_idx])
        self.playback_prog_bar["value"] = 0
        self.playback_prog_bar["maximum"] = self.current_track["length"]
        self.play()

    def update_playback_progress(self):
        if self.is_playing_audio:
            self.playback_prog_bar["value"] += 1

            total_mins = self.playback_list[self.current_track_idx]["length"] // 60
            total_secs = self.playback_list[self.current_track_idx]["length"] % 60
            current_mins = self.playback_prog_bar["value"] // 60
            current_secs = self.playback_prog_bar["value"] % 60

            text = "{0}:{1} / {2}:{3}".format(current_mins, current_secs, total_mins, total_secs)
            self.playback_prog_label.config(text=text)
            if self.playback_prog_bar["value"] == self.current_track["length"]:
                self.is_playing_audio = False
        self.window.after(1000, self.update_playback_progress)    


    def monitor_input(self):
        if self.is_input_enabled:
            if GPIO.input(self.mic_pin) == GPIO.HIGH:
                self.record_voice_message()
            if GPIO.input(self.emergency_pin) == GPIO.HIGH:
                while GPIO.input(self.emergency_pin) == GPIO.HIGH:
                    pass            
                if self.is_distress_active:    
                    self.is_distress_active = False      
                    with open("distress.txt", "w") as file:
                        #This wipes the distress.txt file
                        pass
                    self.distress_window.destroy()
                else:
                    if self.is_playing_audio:
                        self.play_pause_audio()                            
                    self.is_distress_active = True                    
                    self.trigger_distress()                                 

        self.window.after(50, self.monitor_input)

    def build_messages_list(self):
        msg_count = self.messages_list.size()
        with open("./messages.txt") as file:  
            data = file.read()
        data = data.splitlines()
        self.messages_list.delete(0, END)
        for d in data:
            self.messages_list.insert(END, d)
        if self.messages_list.size() > msg_count:
            self.pwm.ChangeDutyCycle(90)
            sleep(0.2)
            self.pwm.ChangeDutyCycle(0)
            sleep(0.1)
            self.pwm.ChangeDutyCycle(90)
            sleep(0.2)
            self.pwm.ChangeDutyCycle(0)
        self.window.after(15000, self.build_messages_list)

    def trigger_distress(self):
        with open("distress.txt", "w") as file:
            file.write("Distress active")

        self.distress_window = Tk()
        self.distress_window.config(cursor='none')
        self.distress_window.geometry('320x480')
        self.distress_window['bg'] = "red"
        #self.distress_window.overrideredirect(True)
        self.distress_window.title(' ')
        self.distress_window.protocol("WM_DELETE_WINDOW", self.distress_window.destroy)           

        padding_frame = Frame(self.distress_window, height=100, bg="red")
        padding_frame.pack()

        self.distress_frame = Frame(self.distress_window, bg="red")
        self.distress_frame.pack(side=TOP)

        distress_font = tkinter.font.Font(family="Times New Roman", size=24, weight="bold")
        self.distress_label = Label(self.distress_frame, text="DISTRESS BEACON ACTIVE", bg="white", font=distress_font)
        self.distress_label.pack(side=TOP)          

        self.distress_window.after(50, self.monitor_input) 
        self.distress_window.mainloop()  


    def build_playback_list(self):
        try:
            current_track = dict(self.playback_list[self.current_track_idx])
        except:
            pass
        self.playback_list = []
        
        with open("gps_coordinates.txt", "r") as file:
            data = file.read()
        current_location = [c.strip() for c in data.split(',')]

        #Ensure gps signal is recent
        gps_time = strptime(current_location[2], "%Y/%m/%d %H:%M:%S")
        current_time = gmtime()
        diff = mktime(current_time)-mktime(gps_time)
        if diff > 30:
            self.is_gps_connected = False
        else:
            self.is_gps_connected = True            
        current_location = (float(current_location[0]), float(current_location[1]))

        with open("./audio/tracklist.json") as file:  
            data = json.load(file)

        for d in data:
            weight = self.calculate_distance(d, current_location)
            if weight < self.poi_range_threshold or d["title"] == current_track["title"]:
                entry = {"handle":"audio/"+d["filename"], "title":d["title"], "length":d["length"], "weight": weight}  
            self.playback_list.append(entry)

        self.playback_list.sort(key=lambda item:item["weight"])
        self.tracklist_list.delete(0, END)
        for t in self.playback_list:
            self.tracklist_list.insert(END, t["title"])
        try:
            self.current_track_idx = next((index for (index, d) in enumerate(self.playback_list) if d["title"] == self.current_track["title"]))
        except:
            pass
        self.window.after(15000, self.build_playback_list)

    def calculate_distance(self, d, loc):
        if not d["lat"]:
            return float("-inf")        
        
        poi_location = (d["lat"], d["long"])
        return geopy.distance.vincenty(loc, poi_location).km

    def play(self):
        self.player.stop()                         # stops any track currently playing
        print('Playing: {0:}'.format(self.current_track["handle"]))
        self.player.pre_init(8000, -16, 1, 1024)
        self.player.init()  
        audio = self.player.Sound(self.current_track["handle"])
        self.player.Sound.play(audio)
        #pygame.mixer.pre_init(8000, -16, 1, 1024)
        #pygame.mixer.init()
        #pygame.mixer.music.load(self.current_track["handle"])
        #pygame.mixer.music.play()
        return(audio)

    def pause(self):
        if self.player is not None:
            self.player.pause()
            
    def resume(self):
        self.player.unpause()

    def restart(self):
        self.play()    

    def record_audio(self):	
        # Define Audio characteristics
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 48000
        CHUNK = 1024
        RECORD_SECONDS = 10
        FILENAME = "message"+strftime('%H:%M', localtime())
        TARGET = "./audio/audio_out/"+FILENAME+".ogg"

        # Audio Recording
        audio = pyaudio.PyAudio()

        # start Recording
        stream = audio.open(format=FORMAT, channels=CHANNELS,rate=RATE, input=True,frames_per_buffer=CHUNK)
        print ('recording...')

        data = stream.read(int(RATE/CHUNK) * CHUNK * RECORD_SECONDS)
        print ('finished recording')

        # stop Recording
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        wave_data = struct.unpack("%ih" % int(RATE/CHUNK) * CHUNK *RECORD_SECONDS, data) # '%ih' is 16-bit format
    
        y = numpy.floor(numpy.log2(len(wave_data)))
        nextpow2  = numpy.power(2, y+1)

        diff = (nextpow2 - len(wave_data)) % 2
        diff_rate = len(wave_data) / nextpow2

        signal_arr = numpy.zeros(int(nextpow2))
        signal_arr[0:len(wave_data)] = wave_data

        #start = timer()
        recording_resample = signal.resample(signal_arr, int(len(signal_arr)/6)).astype(numpy.int16)
        #end = timer()

        resample_len = int(len(recording_resample) * diff_rate)

        if resample_len % 2 == 1:
                resample_len -= 1
        truncate_arr = numpy.zeros(resample_len)

        truncate_arr = recording_resample[:len(truncate_arr)]

        resamples = b''

        for i in range(0, len(truncate_arr)):
                resamples += (int(truncate_arr[i]/256)).to_bytes(2, byteorder='big', signed=True)

        pydub_audio = AudioSegment(resamples, sample_width=2, frame_rate=8000, channels=1)

        pydub_audio.export(TARGET, format = "ogg")  # ~50% reduction in file size; 91KB per 10 seconds

        print('Done export')

        new_data = {"filename": FILENAME+".ogg", "is_sent": False}
        with open("./audio/audio_out/outlist.json", "r+") as file:
            data = list(json.load(file))
            data.append(new_data)
            file.seek(0)
            json.dump(data, file)
            file.truncate()   

        self.enable_controls()
        self.recording_window.destroy()


if __name__ == "__main__":
    interface = deviceUI()
    interface.start()  

def main():
    interface = deviceUI()
    interface.start()  
