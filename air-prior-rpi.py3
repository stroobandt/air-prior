#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
REQUIRES
    $ sudo pip3 install --upgrade RPi.GPIO


USAGE
    $ chmod +x on0nl.py3
    $ ./on0nl.py3


COPYRIGHT
    Copyright (C) 2017-2018  Serge Y. Stroobandt

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


CONTACT
    ON4AA
    echo c2VyZ2VAc3Ryb29iYW5kdC5jb20K |base64 -d
'''


### IMPORTS ###

import RPi.GPIO as GPIO
import threading, time
import sys


### OBJECT CLASS ###

class Channel:
    instances = set()

    def __init__(self, rx_pin, tx_pin):
        self.rx = False
        self.timer = None
        self.master = False
        self.tx = False
        self.rx_pin = rx_pin
        self.tx_pin = tx_pin
        Channel.instances.add(self)

        GPIO.setup(rx_pin, GPIO.IN)
        GPIO.add_event_detect(rx_pin, GPIO.BOTH, callback=self.callback)
        GPIO.setup(tx_pin, GPIO.OUT, initial=0) 

    def callback(self, channel):
        if GPIO.input(self.rx_pin):
            self.take()
        else:
            self.set_drop_timer()

    def take(self):
        self.rx = True
        other_channels = Channel.instances - {self}
        other_master = False
        for other in other_channels:
            if other.master:
                other_master = True
        if not other_master:
            self.master = True
            if self.timer:
                self.timer.cancel()
            self.tx = True
            GPIO.output(self.tx_pin, 1)
            for other in other_channels:
                other.tx = True
                GPIO.output(other.tx_pin, 1)

    def set_drop_timer(self):
        self.rx = False
        self.timer = threading.Timer(3 , self.drop)
        self.timer.start()

    def drop(self):
        if self.master:
            self.master = False
            self.timer = None
            other_channels = Channel.instances - {self}
            other_master = False
            for other in other_channels:
                if other.rx and not other_master:
                    other.master = True
                    other_master = True
            if not other_master:
                for ch in Channel.instances:
                    ch.tx = False
                    GPIO.output(ch.tx_pin, 0)


### MAIN ###

# Setup GPIO numbering according to the Board numbering
GPIO.setmode(GPIO.BOARD)

ch1 = Channel(22, 9)
ch2 = Channel(27, 10)
#ch3 = Channel(28, 11)

try:
    while True:
        time.sleep(0.2)

except KeyboardInterrupt:
    sys.exit()
