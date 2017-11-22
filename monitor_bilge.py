#!/usr/bin/python2
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

# Copyright 2017 Philip J. Freeman <elektron@halo.nu>
#
#  This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from email.mime.text import MIMEText
import logging
import smtplib
import time

import RPi.GPIO as GPIO

##### CONFIGURATION #####

# GPIO_IN_PIN - Set the GPIO pin number to monitor
#
GPIO_IN_PIN = 17

# WARNING_THRESHOLD - seconds before we enter the "Warning" state, right
# now we only print a message to the console.
#
# TODO: decide if we even need a warning state. If we do, we should
# probably send a notification...
#
WARNING_THRESHOLD = 10

# ERROR_THRESHOLD -  seconds before we enter the "Error" state. This
# triggers a notofocation (configured below.)
#
ERROR_THRESHOLD = 30

# NOTIFICATION_FROM - from address for notification email
#
NOTIFICATION_FROM = "bilgemonitor@svzeno.com"

# NOTIFICATION_TO - to addresses for notification email
#
NOTIFICATION_TO = ["elektron@halo.nu"]

# NOTIFICATION_RESEND - seconds in error state before we send an
# additional notofocation
#
NOTIFICATION_RESEND = 60*60*3 # 3 hours

##### END OF CONFIG #####


def send_notification(subject, message):

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = NOTIFICATION_FROM
    msg['To'] = ", ".join(NOTIFICATION_TO)

    s = smtplib.SMTP('localhost')
    s.sendmail(NOTIFICATION_FROM, NOTIFICATION_TO, msg.as_string())
    s.quit()

def main():

    # Setup
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=logging.INFO
        )
    logging.info("Setup GPIO pin #{}".format(GPIO_IN_PIN))
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_IN_PIN, GPIO.IN)

    last_state=1 # Default to inactive
    last_state_change=time.time()
    warning_sent=0
    error_sent=0
    last_error_sent=0

    while True:
        new_state = GPIO.input(GPIO_IN_PIN)
        if new_state == last_state:
            if last_state == 0: # pump is still active
                new_timestamp = time.time()
                if new_timestamp-last_state_change > ERROR_THRESHOLD:
                    if new_timestamp-last_error_sent > RESEND_ERROR_THRESHOLD:
                        logging.error("Bilge pump is active for longer than error threshold ({}s) since {}s ago".format(ERROR_THRESHOLD, new_timestamp-last_state_change))
                        send_notification("ERROR: Bilge Pump", "Bilge pump is active for longer than error threshold ({}s) since {}s ago".format(ERROR_THRESHOLD, new_timestamp-last_state_change))
                        error_sent = 1
                        last_error_sent = new_timestamp
                elif new_timestamp-last_state_change > WARNING_THRESHOLD:
                    if warning_sent == 0:
                        logging.warning("Bilge pump is active for longer than warning threshold ({}s)".format(WARNING_THRESHOLD))
                        warning_sent = 1
                time.sleep(.2)
            else: # pump is still inactive
                time.sleep(.5)
        else:
            if new_state == 0: # pump switched to active
                new_timestamp = time.time()
                logging.info("Bilge pump is active (after bing inactive for {} seconds)".format(new_timestamp-last_state_change))
            else: # pump completed duty cycle
                logging.info("Bilge pump completed duty cycle (after being active for {} seconds)".format(new_timestamp-last_state_change))
                if error_sent == 1:
                    logging.info("Bilge pump recovered from error state (after being active for {} seconds)".format(new_timestamp-last_state_change))
                    send_notification("RECOVERY: Bilge Pump", "Bilge pump recovered from error state (after being active for {} seconds)".format(ERROR_THRESHOLD, new_timestamp-last_state_change))
                warning_sent = 0
                error_sent = 0
                last_error_sent=0
            last_state = new_state
            last_state_change = new_timestamp

if __name__ == "__main__":
    main()
