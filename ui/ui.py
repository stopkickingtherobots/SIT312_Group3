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

    # Implement check for connection to base station
    # if wifi_connection:
    #     wifi_img = ImageTk.PhotoImage(Image.open("./resources/wifi_on.png"))
    # else:
    #     wifi_img = ImageTk.PhotoImage(Image.open("./resources/wifi_off.png"))
    # wifi_label.configure(image=wifi_img)
    # wifi_label.image = wifi_img

    # Implement check for gps connection
    # if gps_connection:
    #     gps_img = ImageTk.PhotoImage(Image.open("./resources/gps_on.png"))
    # else:
    #     gps_img = ImageTk.PhotoImage(Image.open("./resources/gps_off.png"))
    # gps_label.configure(image=gps_img)
    # gps_label.image = gps_img

    window.after(5000, refresh_status_bar)


def display_voice_message_warning_countdown(countdown):
    activity_label.config(text="Record message in {0}".format(countdown))

    # Callbacks need to be used here rather than sleep, otherwise the labels won't update
    if countdown == 1:
        window.after(1000, lambda: display_record_voice_message_countdown(10))
    else:
        window.after(
            1000, lambda: display_voice_message_warning_countdown(countdown-1))
        # Start thread for voice recording here
        # window.after(1000, ***THREAD START***)


def display_record_voice_message_countdown(timeframe):
    if timeframe == 0:
        activity_label.config(text="Message recorded.")
        enable_controls()
        return
    activity_label.config(text="Record your message\n{0}".format(timeframe))
    window.after(
        1000, lambda: display_record_voice_message_countdown(timeframe-1))


def record_voice_message():
    # Disable controls while recording audio
    disable_controls()
    display_voice_message_warning_countdown(3)


def disable_controls():
    rewind_button.config(state=DISABLED)
    play_pause_button.config(state=DISABLED)
    skip_button.config(state=DISABLED)
    global is_input_enabled
    is_input_enabled = False


def enable_controls():
    rewind_button.config(state=NORMAL)
    play_pause_button.config(state=NORMAL)
    skip_button.config(state=NORMAL)
    global is_input_enabled
    is_input_enabled = True


def play_pause_audio():
    global is_playing_audio
    # Change play/pause state of audio playback here
    text = "Pause" if is_playing_audio else "Play"
    activity_label.config(text=text)
    if is_playing_audio:
        play_pause_button.configure(image=play_img)
        play_pause_button.image = play_img

    else:
        play_pause_button.configure(image=pause_img)
        play_pause_button.image = pause_img

    is_playing_audio = not is_playing_audio


def rewind_track():
    # Restart current audio here
    activity_label.config(text="Rewind")


def skip_track():
    # Jump to next track in queue here
    activity_label.config(text="Skip")


def monitor_input():
    if is_input_enabled:
        if (GPIO.input(mic_pin) == GPIO.HIGH):
            record_voice_message()

    window.after(100, monitor_input)


GPIO.setmode(GPIO.BOARD)

mic_pin = 40
GPIO.setup(mic_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
emergency_pin = 38
GPIO.setup(emergency_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
piezo_pin = 36
GPIO.setup(piezo_pin, GPIO.OUT)

pijuice = PiJuice(1, 0x14)

is_playing_audio = False
is_input_enabled = True

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

play_img = ImageTk.PhotoImage(Image.open("./resources/play_button.png"))
pause_img = ImageTk.PhotoImage(Image.open("./resources/pause_button.png"))
rewind_img = ImageTk.PhotoImage(Image.open("./resources/back_button.png"))
skip_img = ImageTk.PhotoImage(Image.open("./resources/forward_button.png"))

playback_frame = Frame(window)
playback_frame.pack(side=BOTTOM)

rewind_button = Button(playback_frame, image=rewind_img,
                       command=rewind_track)
rewind_button.pack(side=LEFT)

play_pause_button = Button(
    playback_frame, image=play_img, command=play_pause_audio)
play_pause_button.pack(side=LEFT)

skip_button = Button(playback_frame, image=skip_img, command=skip_track)
skip_button.pack(side=RIGHT)


# # playback controls frame
# playback_frame=Frame(window)
# playback_frame.pack(side=BOTTOM)

# rewind_img=ImageTk.PhotoImage(Image.open("./resources/back_button.png"))
# rewind_button=Button(playback_frame, image=rewind_img, command=rewind_track)
# rewind_button.pack(side=LEFT)

# play_pause_img=ImageTk.PhotoImage(Image.open("./resources/play_button.png"))
# play_pause_button=Button(
#     playback_frame, image=play_pause_img, command=play_pause_audio)
# play_pause_button.pack(side=LEFT)

# skip_img=ImageTk.PhotoImage(Image.open("./resources/forward_button.png"))
# skip_button=Button(playback_frame, image=skip_img, command=skip_track)
# skip_button.pack(side=RIGHT)


window.protocol("WM_DELETE_WINDOW", close)
window.after(5000, refresh_status_bar)
window.after(100, monitor_input)
window.mainloop()
