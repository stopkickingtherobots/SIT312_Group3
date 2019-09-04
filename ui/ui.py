from tkinter import *
from tkinter import ttk
import tkinter.font
from time import localtime, strftime, sleep
from PIL import ImageTk, Image
from pijuice import PiJuice
import RPi.GPIO as GPIO

class deviceUI():
    def __init__(self):
        #Test data
        self.test_track_info = [{"title": "Test Track 1", "length": 215}, {"title": "Test Track 2", "length": 351}, {"title": "Test Track 3", "length": 111}]
        self.current_track = 0

        self.is_playing_audio = False
        self.is_input_enabled = True
        #TODO: Implement controller for connectivity bools
        self.is_gps_connected = True
        self.is_basestation_connected = True

        self.__initialise_hardware()

        self.__initialise_window()
        self.__load_graphics()
        self.__build_status_frame()
        self.__add_padding_frame()
        self.__build_info_frame()
        self.__add_padding_frame()
        self.__build_playback_frame()
        self.__add_padding_frame()
        self.__build_control_frame()

        self.window.protocol("WM_DELETE_WINDOW", self.close)      

    def __initialise_hardware(self):
        self.pijuice = PiJuice(1, 0x14)
        GPIO.setmode(GPIO.BOARD)
        self.mic_pin = 40
        GPIO.setup(self.mic_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.emergency_pin = 38
        GPIO.setup(self.emergency_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.piezo_pin = 36
        GPIO.setup(self.piezo_pin, GPIO.OUT)

    def __initialise_window(self):
        self.window = Tk()
        self.window.config(cursor='none')
        self.window.geometry('320x480')
        self.window['bg'] = "white"
        #self.window.overrideredirect(True)
        self.window.title(' ')

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

    def __build_info_frame(self):
        self.info_frame = Frame(self.window, borderwidth=1, relief="solid")
        self.info_frame.pack(side=TOP)
        self.info_label = Label(self.info_frame, text="Pause", font=("Times New Roman", 24, "bold"))
        self.info_label.pack(side=TOP)

    def __build_playback_frame(self):
        self.playback_info_frame = Frame(self.window)
        self.playback_info_frame.pack()
        
        self.play_pause_display_icon = Label(self.playback_info_frame, image=self.pause_icon, padx=10)
        self.play_pause_display_icon.pack(side=LEFT)

        self.playback_prog_bar = ttk.Progressbar(self.playback_info_frame, orient="horizontal", length=150, mode="determinate")
        self.playback_prog_bar["value"] = 0
        self.playback_prog_bar["maximum"] = self.test_track_info[0]["length"]
        self.playback_prog_bar.pack(side=LEFT)

        mins = self.test_track_info[0]["length"]//60
        secs = self.test_track_info[0]["length"] % 60
        self.playback_prog_label = Label(self.playback_info_frame, text="0:00 / {0}:{1}".format(mins, secs))
        self.playback_prog_label.pack(side=LEFT)

        self.bottom_info_frame = Frame(self.window)
        self.bottom_info_frame.pack()
        self.track_label = Label(self.bottom_info_frame, text=self.test_track_info[0]["title"])
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
        self.window.mainloop()

    def close(self):
        self.window.destroy()
        GPIO.cleanup()

    def refresh_status_bar(self):
        self.date_time_label.config(text=strftime("%H:%M  %d/%m/%Y", localtime()), font=self.status_font)

        battery_level = self.pijuice.status.GetChargeLevel()['data']
        self.battery_label.config(text=str(battery_level)+"%")

        # TODO: Implement controller for base station connection status
        if self.is_basestation_connected:
            self.wifi_label.configure(image=self.wifi_on_img)
            self.wifi_label.image = self.wifi_on_img
        else:
            self.wifi_label.configure(image=self.wifi_off_img)
            self.wifi_label.image = self.wifi_off_img

        # TODO: Implement controller for gps connection status
        if self.is_gps_connected:
            self.gps_label.configure(image=self.gps_on_img)
            self.gps_label.image = self.gps_on_img
        else:
            self.gps_label.configure(image=self.gps_off_img)
            self.gps_label.image = self.gps_off_img

        self.window.after(5000, self.refresh_status_bar)

    def record_voice_message(self):
        # Disable controls while recording audio
        self.disable_controls()
        self.display_voice_message_warning_countdown(3)

    def display_voice_message_warning_countdown(self, countdown):
        self.info_label.config(text="Record message in {0}".format(countdown))

        # Callbacks need to be used here rather than sleep, otherwise the labels won't update
        if countdown == 1:
            window.after(1000, lambda: self.display_record_voice_message_countdown(10))
        else:
            window.after(1000, lambda: self.display_voice_message_warning_countdown(countdown-1))
            # Start thread for voice recording here
            # window.after(1000, ***THREAD START***)

    def display_record_voice_message_countdown(self, timeframe):
        if timeframe == 0:
            self.info_label.config(text="Message recorded.")
            self.enable_controls()
            return
        self.info_label.config(text="Record your message\n{0}".format(timeframe))
        self.window.after(1000, lambda: self.display_record_voice_message_countdown(timeframe-1))

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
        # Change play/pause state of audio playback here
        text = "Pause" if self.is_playing_audio else "Play"
        self.info_label.config(text=text)
        if self.is_playing_audio:
            self.play_pause_button.configure(image=self.play_img)
            self.play_pause_button.image = self.play_img

            self.play_pause_display_icon.configure(image=self.pause_icon)
            self.play_pause_display_icon.image = self.pause_icon

        else:
            self.play_pause_button.configure(image=self.pause_img)
            self.play_pause_button.image = self.pause_img

            self.play_pause_display_icon.configure(image=self.play_icon)
            self.play_pause_display_icon.image = self.play_icon

        self.is_playing_audio = not self.is_playing_audio

    def rewind_track(self):
        # Restart current audio here
        self.playback_prog_bar["value"] = 0
        self.info_label.config(text="Rewind")


    def skip_track(self):
        # Jump to next track in queue here
        self.playback_prog_bar["value"] = 0
        self.current_track += 1
        text = self.test_track_info[self.current_track]["title"]

        self.track_label.config(text=text)
        self.info_label.config(text="Skip")

    def update_playback_progress(self):
        if self.is_playing_audio:
            self.playback_prog_bar["value"] += 1

            total_mins = self.test_track_info[self.current_track]["length"] // 60
            total_secs = self.test_track_info[self.current_track]["length"] % 60
            current_mins = self.playback_prog_bar["value"] // 60
            current_secs = self.playback_prog_bar["value"] % 60

            text = "{0}:{1} / {2}:{3}".format(current_mins, current_secs, total_mins, total_secs)
            self.playback_prog_label.config(text=text)
        self.window.after(1000, self.update_playback_progress)


    def monitor_input(self):
        if self.is_input_enabled:
            if (GPIO.input(self.mic_pin) == GPIO.HIGH):
                self.record_voice_message()

        self.window.after(100, self.monitor_input)

if __name__ == "__main__":
    interface = deviceUI()
    interface.start()