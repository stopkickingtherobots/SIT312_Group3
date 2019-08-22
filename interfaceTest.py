import RPi.GPIO as GPIO
from time import sleep
from RPLCD.gpio import CharLCD

def soundAlarm(pwm, buttonPin):
    while True and not GPIO.input(buttonPin) == GPIO.HIGH:
        pwm.ChangeDutyCycle(90)
        sleep(1)
        pwm.ChangeDutyCycle(0)
        sleep(1)    

try:
	GPIO.setmode(GPIO.BOARD)
	
    #LCD screen
    lcd = CharLCD(cols=16, rows=2,
                  pin_rs=37, pin_e=35, pins_data=[22,18,15,13],
                  numbering_mode=GPIO.BOARD)
    #Buttons
    alarmButton = 10
    GPIO.setup(alarmButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    micButton = 33
    GPIO.setup(micButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    skipButton = 31
    GPIO.setup(skipButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    pauseButton = 7
    GPIO.setup(pauseButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    playButton = 11
    GPIO.setup(playButton, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    #Buzzer
    buzzPin = 8
    GPIO.setup(buzzPin, GPIO.OUT)
    pwm = GPIO.PWM(buzzPin, 400)
    pwm.start(0)

    micTransmit = False
    
    while True:
        while (GPIO.input(micButton) == GPIO.HIGH):
            if (micTransmit == False):
                lcd.clear()
                lcd.write_string("Transmitting audio")
            micTransmit = True
        if (GPIO.input(micButton) == GPIO.LOW and micTransmit):
            micTransmit = False
            lcd.clear()
            lcd.write_string("Ended audio transmission")
            
        if (GPIO.input(alarmButton) == GPIO.HIGH):
            while(GPIO.input(alarmButton) == GPIO.HIGH): pass
            lcd.clear()
            lcd.write_string("Alarm active")
            soundAlarm(pwm, alarmButton)
            lcd.clear()
            lcd.write_string("Alarm deactivated")
            while(GPIO.input(alarmButton) == GPIO.HIGH): pass

        if (GPIO.input(skipButton) == GPIO.HIGH):
            lcd.clear()
            lcd.write_string("Audio skipped")
            while (GPIO.input(skipButton) == GPIO.HIGH): pass
        if (GPIO.input(pauseButton) == GPIO.HIGH):
            lcd.clear()
            lcd.write_string("Audio paused")
            while (GPIO.input(pauseButton) == GPIO.HIGH): pass
        if (GPIO.input(playButton) == GPIO.HIGH):
            lcd.clear()
            lcd.write_string("Audio playing")
            while (GPIO.input(playButton) == GPIO.HIGH): pass


except KeyboardInterrupt:
    pass

finally:
    print("Done")
    pwm.stop()
    GPIO.cleanup()
