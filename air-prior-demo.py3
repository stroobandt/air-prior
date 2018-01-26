#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
REQUIRES
    $ sudo pip3 install --upgrade pygame


USAGE
    $ chmod +x repeater.py3
    $ ./repeater.py3


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


### GLOBALS ###

w = 640
h = 240

black = (0, 0, 0)
grey  = (128, 128, 128)
white  = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)


### IMPORTS ###

import pygame, sys
import pygame.locals
import threading, time


### OBJECT CLASSES ###

class Channel:
    instances = set()

    def __init__(self):
        self.rx = False
        self.timer = None
        self.master = False
        self.tx = False
        Channel.instances.add(self)

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
            for other in other_channels:
                other.tx = True

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

    @property
    def rx_colour(self):
        if self.rx:
            return green
        else:
            return grey

    @property
    def tx_colour(self):
        if self.tx:
            return red
        else:
            return grey

def quit():
    pygame.quit()
    sys.exit()


### MAIN ###

pygame.init()
display = pygame.display.set_mode((w, h))
pygame.display.set_caption('ON0LN')
display.fill(black)
font = pygame.font.SysFont(None, 56)

ch1 = Channel()
ch2 = Channel()

while True:

    time.sleep(0.2)

    for event in pygame.event.get():

        if event.type == pygame.locals.QUIT:
            quit()

        elif event.type == pygame.locals.KEYDOWN:

            if event.key == pygame.K_LEFT:
                ch1.rx = True
                if not ch2.master:
                    ch1.take()

            if event.key == pygame.K_RIGHT:
                ch2.rx = True
                if not ch1.master:
                    ch2.take()

            if event.key == pygame.K_ESCAPE:
                quit()

        elif event.type == pygame.locals.KEYUP:

            if event.key == pygame.K_LEFT:
                ch1.set_drop_timer()

            if event.key == pygame.K_RIGHT:
                ch2.set_drop_timer()


    #GUI

    text = font.render('channel 1 RX', True, ch1.rx_colour)
    display.blit(text, (w//4 - text.get_width()//2, h//4 - text.get_height()//2))

    text = font.render('channel 2 RX', True, ch2.rx_colour)
    display.blit(text, (w//2 + w//4 - text.get_width()//2, h//4 - text.get_height()//2))

    text = font.render('channel 1 TX', True, ch1.tx_colour)
    display.blit(text, (w//4 - text.get_width()//2, h//2 + h//4 - text.get_height()//2))

    text = font.render('channel 2 TX', True, ch2.tx_colour)
    display.blit(text, (w//2 + w//4 - text.get_width()//2, h//2 + h//4 - text.get_height()//2))

    if ch1.master:
        colour = white
    else:
        colour = black
    text = font.render('master', True, colour)
    display.blit(text, (w//4 - text.get_width()//2, h//2 - text.get_height()//2))

    if ch2.master:
        colour = white
    else:
        colour = black
    text = font.render('master', True, colour)
    display.blit(text, (w//2 + w//4 - text.get_width()//2, h//2 - text.get_height()//2))

    pygame.display.flip()
