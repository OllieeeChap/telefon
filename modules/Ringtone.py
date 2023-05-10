import RPi.GPIO as GPIO
from threading import Timer
import time

class Ringtone:
    
    # Output relay pin
    pin_relay = 14

    def __init__(self):
        # Set GPIO mode to Broadcom SOC numbering
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_relay, GPIO.OUT)
        GPIO.output(self.pin_relay, GPIO.HIGH)

    def ring(self):
        print('[RING] Ring')
        GPIO.output(self.pin_relay, GPIO.LOW)

        #time.sleep(0.2)

    def unring(self):
        print('[RING] Unring')
        GPIO.output(self.pin_relay, GPIO.HIGH)
        #time.sleep(1)