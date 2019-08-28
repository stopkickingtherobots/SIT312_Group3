from tkinter import *
import tkinter.font
from time import localtime, strftime, sleep
from PIL import ImageTk, Image
from pijuice import PiJuice
import RPi.GPIO as GPIO


def close():
    window.destroy()
    GPIO.cleanup()


def refresh_status_bar():
    date_time_label.config(text=strftime(
        "%H:%M  %d/%m/%Y", localtime()), font=status_font)

    battery_level = pijuice.status.GetChargeLevel()['data']
    battery_label.config(text=str(battery_level)+"%")

    # if wifi_connection:
    #     wifi_img = ImageTk.PhotoImage(Image.open("./resources/wifi_on.png"))
    # else:
    #     wifi_img = ImageTk.PhotoImage(Image.open("./resources/wifi_off.png"))
    # wifi_label.configure(image=wifi_img)
    # wifi_label.image = wifi_img

    # if gps_connection:
    #     gps_img = ImageTk.PhotoImage(Image.open("./resources/gps_on.png"))
    # else:
    #     gps_img = ImageTk.PhotoImage(Image.open("./resources/gps_off.png"))
    # gps_label.configure(image=gps_img)
    # gps_label.image = gps_img

    window.after(5000, refresh_status_bar)


def voice_message_countdown(countdown):
    activity_label.config(text="Record message in {0}".format(countdown))
    if countdown == 1:
        window.after(1000, lambda: record_voice_message(10))
    else:
        window.after(1000, lambda: voice_message_countdown(countdown-1))


def record_voice_message(timeframe):
    if timeframe == 0:
        activity_label.config(text="Message Sent!")
        return

    activity_label.config(text="Record your message\n{0}".format(timeframe))
    window.after(1000, lambda: record_voice_message(timeframe-1))


def monitor_input():
    if (GPIO.input(rewind_pin) == GPIO.HIGH):
        activity_label.config(text="Rewind")
        while (GPIO.input(rewind_pin) == GPIO.HIGH):
            pass

    if (GPIO.input(play_pause_pin) == GPIO.HIGH):
        global is_playing_audio
        text = "Pause" if is_playing_audio else "Play"
        activity_label.config(text=text)
        is_playing_audio = not is_playing_audio
        while (GPIO.input(play_pause_pin) == GPIO.HIGH):
            pass

    if (GPIO.input(skip_pin) == GPIO.HIGH):
        activity_label.config(text="Skip")
        while (GPIO.input(skip_pin) == GPIO.HIGH):
            pass

    if (GPIO.input(mic_pin) == GPIO.HIGH):
        voice_message_countdown(3)
        while (GPIO.input(skip_pin) == GPIO.HIGH):
            pass

    window.after(100, monitor_input)


GPIO.setmode(GPIO.BOARD)
play_pause_pin = 35
GPIO.setup(play_pause_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
rewind_pin = 37
GPIO.setup(rewind_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
skip_pin = 33
GPIO.setup(skip_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
mic_pin = 40
GPIO.setup(mic_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
emergency_pin = 38
GPIO.setup(emergency_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
piezo_pin = 36
GPIO.setup(piezo_pin, GPIO.OUT)

pijuice = PiJuice(1, 0x14)

is_playing_audio = False

window = Tk()
window.config(cursor='none')
window.geometry('320x480')
window['bg'] = "white"
# window.overrideredirect(Y)
window.title(' ')

status_font = tkinter.font.Font(
    family="Times New Roman", size=11, weight="bold")


# Frame for status bar
status_frame = Frame(window, borderwidth=1, relief="solid", bg="white")
status_frame.pack(side=TOP)

# date and time
date_time_label = Label(status_frame, text=strftime(
    "%H:%M  %d/%m/%Y", localtime()), font=status_font)
date_time_label.pack(side=LEFT)

# battery info
battery_level = pijuice.status.GetChargeLevel()['data']
battery_label = Label(status_frame, text=str(
    battery_level)+"%", font=status_font)
battery_label.pack(side=RIGHT)
battery_img = ImageTk.PhotoImage(Image.open("./resources/battery.png"))
battery_img_label = Label(status_frame, image=battery_img)
battery_img_label.pack(side=RIGHT)

# wifi status
wifi_img = ImageTk.PhotoImage(Image.open("./resources/wifi_off.png"))
wifi_label = Label(status_frame, image=wifi_img)
wifi_label.pack(side=RIGHT)

# gps status
gps_img = ImageTk.PhotoImage(Image.open("./resources/gps_off.png"))
gps_label = Label(status_frame, image=gps_img)
gps_label.pack(side=RIGHT)

# padding frame
padding_frame = Frame(window, height=20, bg="white")
padding_frame.pack()

# placeholder for testing inputs
activity_frame = Frame(window, borderwidth=1, relief="solid")
activity_frame.pack(side=TOP)
activity_label = Label(activity_frame, text="Pause",
                       font=("Times New Roman", 24, "bold"))
activity_label.pack(side=TOP)


window.protocol("WM_DELETE_WINDOW", close)
window.after(5000, refresh_status_bar)
window.after(100, monitor_input)
window.mainloop()
