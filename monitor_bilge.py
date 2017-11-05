#!/usr/bin/python2.7

import time
import logging

import RPi.GPIO as GPIO

GPIO_IN_PIN=17
ERROR_THRESHOLD=30
WARNING_THRESHOLD=10

# Setup
logging.basicConfig(
        filename='monitor_bilge.log',
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO
    )
logging.info("Setup GPIO pin #{}".format(GPIO_IN_PIN))
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_IN_PIN, GPIO.IN)  

#def float_switch_callback(channel):  
#    if GPIO.input(GPIO_IN_PIN):
#        logging.debug("Rising edge detected")
#    else:
#	logging.debug("Falling edge detected")
#
#GPIO.add_event_detect(GPIO_IN_PIN, GPIO.BOTH, callback=float_switch_callback)

last_state=1 # Default to inactive
last_state_change=time.time()
warning_sent=0
error_sent=0

while True:
    new_state = GPIO.input(GPIO_IN_PIN)
    if new_state == last_state:
        if new_state == 0:
            new_timestamp = time.time()
            if new_timestamp-last_state_change > ERROR_THRESHOLD:
		if error_sent == 0:
                    logging.error("Bilge pump is active for longer than error threshold ({}s)".format(ERROR_THRESHOLD))
                    error_sent = 1
            elif new_timestamp-last_state_change > WARNING_THRESHOLD:
                if warning_sent == 0:
                    logging.warning("Bilge pump is active for longer than warning threshold ({}s)".format(WARNING_THRESHOLD))
                    warning_sent = 1
            time.sleep(.2)
        else:
            time.sleep(.5)
    else:
        if new_state == 0: # pump switched to active
            new_timestamp = time.time()
            logging.info("Bilge pump is active (after bing inactive for {} seconds)".format(new_timestamp-last_state_change))
        else: # pump completed duty cycle
            warning_sent = 0
            error_sent = 0
            logging.info("Bilge pump completed duty cycle (after being active for {} seconds)".format(new_timestamp-last_state_change))
        last_state = new_state
        last_state_change = new_timestamp
