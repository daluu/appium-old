#    Copyright 2012 Appium Committers
#
#    Licensed to the Apache Software Foundation (ASF) under one
#    or more contributor license agreements.  See the NOTICE file
#    distributed with this work for additional information
#    regarding copyright ownership.  The ASF licenses this file
#    to you under the Apache License, Version 2.0 (the
#    "License"); you may not use this file except in compliance
#    with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing,
#    software distributed under the License is distributed on an
#    "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#    KIND, either express or implied.  See the License for the
#    specific language governing permissions and limitations
#    under the License.

import os
import sys
from sys import argv
from time import sleep
from math import sqrt, pow
from bitbeambot import Bot

appiumpath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'../'))
sys.path.append(appiumpath)
import appium

# globals
bot = None
driver = None
starting_position = 30
current_a = 30
current_b = 30
current_c = 30
contact_point = None
mappings = []
screen_center = None

def distance(x1,y1,x2,y2):
    return sqrt( pow(x2-x1,2) + pow(y2-y1,2) )

def get_coords():
    global driver
    coords = driver.proxy('mainWindow.staticTexts()[0].value()')
    if len(coords) < 1:
        return None
    return (int(coords.split(',')[0][1:].replace(' ','')), int(coords.split(',')[1][:-1].replace(' ','')) )

def map_screen_point(x,y):
    global mappings

    # find the closest points
    known_points = mappings[:]
    closest_distances = []
    closest_points = []
    for i in range (0,4):
        closest_distances.append(1000)
        closest_points.append(None)
        for point in known_points:
            dist =  distance(point[0][0], point[0][1])
            if dist < closest_distances[i]:
                closest_distances[i] = dist
                closest_points[i] = point
        known_points.remove(closest_points[i])

    # TODO triangulate the point based on the nearest points
    triangulated_point = None

    return  triangulated_point

def print_usage():
    print 'python calibrate.py /dev/usb-port "/path/to/my.app"'

if __name__ == '__main__':
    global bot, driver, starting_position, current_a, current_b, current_c, contact_point, mappings, screen_center

    if len(argv) < 2 or not argv[1].startswith("/dev/"):
        print_usage()
        exit(-1)

    # create a bot instance
    bot = Bot(argv[1])

    # create an appium instance
    driver = appium.Appium(argv[2])
    driver.start()

    # lower the pen until the ios device is touched
    current_point = starting_position
    screenCenter = None
    while current_point <= 80 and screenCenter == None:
        current_point += 1
        # exit if we did not touch the ios device
        if current_point > 80:
            raise Exception("Could not contact the iOS device")
        bot.move(current_point, current_point, current_point)
        screenCenter = get_coords()
        contact_point = screen_center

    # add a mapping to the screen center
    mappings.append(screenCenter, (current_a, current_b, current_c))

    # return the device to the original position
    bot.move(starting_position,starting_position,starting_position)

    # TODO: find the points in +x, -x, +y, and -y directions
    # TODO: find screen edges

    # quit appium
    driver.stop()

    # print summary of calibration
    print 'Contact Point : ' + str(contact_point)
    print 'Screen Center : (' + str(screen_center[0]) + ',' + str(screen_center[1]) + ')'
