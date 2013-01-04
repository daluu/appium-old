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
from robot import Bot
import pickle

appiumpath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'../../'))
sys.path.append(appiumpath)
import appium

# globals
bot = None
driver = None
starting_position = 40
contact_point = None
origin_point = None
screen_center = None
up_vector = None
down_vector = None
right_vector = None
left_vector = None

mappings = []

def get_normalized_vector(coords, point, origin_coords):
    movement = point[0]
    if abs(point[1]) > abs(point[0]):
        movement = point[1]
    return ( movement / abs(abs(coords[0]) - abs(origin_coords[0])), movement / abs(abs(coords[1]) - abs(origin_coords[1])))

def get_coords():
    global driver
    coords = driver.proxy('mainWindow.staticTexts()[0].value()')
    if len(coords[0]) < 2:
        return None
    coords = coords[0][1]
    if len(coords) < 1 or ',' not in coords:
        return None
    return (int(coords.split(',')[0][1:].replace(' ','')), int(coords.split(',')[1][:-1].replace(' ','')) )

def print_usage():
    print 'python calibrate.py UDID /dev/usb-port'

if len(argv) < 2 or not argv[2].startswith("/dev/"):
    print_usage()
    exit(-1)

# create a bot instance
print 'Making robot'
bot = Bot(argv[2])

# create an appium instance
print 'Launching Calibration App'
driver = appium.Appium('Appium.RobotCalibration', argv[1])
driver.start()

# lower the pen until the ios device is touched
current_point = starting_position
screen_center = None
print 'Entering Calibration Loop'
while current_point <= 80 and screen_center == None:
    current_point += 1
    # exit if we did not touch the ios device
    if current_point > 80:
        raise Exception("Could not contact the iOS device")
    bot.move(current_point, current_point, current_point)
    screen_center = get_coords()

    contact_point = bot.forward_k(current_point, current_point, current_point)
    if contact_point[0] is not 0:
        raise Exception('Could not detect contact point')
    contact_point = (contact_point[1], contact_point[2], contact_point[3])

    origin_point = bot.forward_k(starting_position, starting_position, starting_position)
    if origin_point[0] is not 0:
        raise Exception('Could not detect origin point')
    origin_point = (origin_point[1], origin_point[2], origin_point[3])

# add a mapping to the screen center
mappings.append((screen_center, (bot.a.angle, bot.b.angle, bot.c.angle)))

# return the device to the original position
bot.move(starting_position,starting_position,starting_position)

# touch to the left
left50pt1 = bot.inverse_k(contact_point[0]-50, 0, origin_point[2])
left50pt2 = bot.inverse_k(contact_point[0]-50, 0, contact_point[2])
bot.set_position(left50pt1)
sleep(1.0)
bot.set_position(left50pt2)
left_coords = get_coords()
left_position = bot.position()
left_point = bot.forward_k(left_position[0], left_position[1], left_position[2])
if left_point[0] is not 0:
    raise Exception('Could not detect origin point')
left_point = (left_point[1], left_point[2], left_point[3])
mappings.append((left_coords, left_point))

# touch to the right
right50pt1 = bot.inverse_k(contact_point[0]+50, 0, origin_point[2])
right50pt2 = bot.inverse_k(contact_point[0]+50, 0, contact_point[2])
bot.set_position(right50pt1)
sleep(1.0)
bot.set_position(right50pt2)
right_coords = get_coords()
right_position = bot.position()
right_point = bot.forward_k(right_position[0], right_position[1], right_position[2])
if right_point[0] is not 0:
    raise Exception('Could not detect origin point')
right_point = (right_point[1], right_point[2], right_point[3])
mappings.append((right_coords, right_point))

# touch to the top
up50pt1 = bot.inverse_k(0, contact_point[0]+50, origin_point[2])
up50pt2 = bot.inverse_k(0, contact_point[0]+50, contact_point[2])
bot.set_position(up50pt1)
sleep(1.0)
bot.set_position(up50pt2)
up_coords = get_coords()
up_position = bot.position()
up_point = bot.forward_k(up_position[0], up_position[1], up_position[2])
if up_point[0] is not 0:
    raise Exception('Could not detect origin point')
up_point = (up_point[1], up_point[2], up_point[3])
mappings.append((up_coords, up_point))

# touch to the bottom
down50pt1 = bot.inverse_k(0, contact_point[0]-50, origin_point[2])
down50pt2 = bot.inverse_k(0, contact_point[0]-50, contact_point[2])
bot.set_position(down50pt1)
sleep(1.0)
bot.set_position(down50pt2)
down_coords = get_coords()
down_position = bot.position()
down_point = bot.forward_k(down_position[0], down_position[1], down_position[2])
if down_point[0] is not 0:
    raise Exception('Could not detect origin point')
down_point = (down_point[1], down_point[2], down_point[3])
mappings.append((down_coords, down_point))

# return the device to the original position
bot.move(starting_position,starting_position,starting_position)

# quit appium
driver.stop()

# calculate translation vectors (virtual space / software space)
left_vector_mapping = mappings[0]
for mapping in mappings:
    if mapping[0][0] - screen_center[0] < left_vector_mapping[0][0] - screen_center[0]:
        left_vector_mapping = mapping
left_vector = get_normalized_vector(left_vector_mapping[0], left_vector_mapping[1], screen_center)

right_vector_mapping = mappings[0]
for mapping in mappings:
    if mapping[0][0] - screen_center[0] > right_vector_mapping[0][0] - screen_center[0]:
        right_vector_mapping = mapping
right_vector = get_normalized_vector(right_vector_mapping[0], right_vector_mapping[1], screen_center)

up_vector_mapping = mappings[0]
for mapping in mappings:
    if mapping[0][1] - screen_center[1] > up_vector_mapping[0][1] - screen_center[1]:
        up_vector_mapping = mapping
up_vector = get_normalized_vector(up_vector_mapping[0], up_vector_mapping[1], screen_center)

down_vector_mapping = mappings[0]
for mapping in mappings:
    if mapping[0][1] - screen_center[1] < down_vector_mapping[0][1] - screen_center[1]:
        down_vector_mapping = mapping
down_vector = get_normalized_vector(down_vector_mapping[0], down_vector_mapping[1], screen_center)

# print summary of calibration
print 'Origin Point : ' + str(origin_point)
print ''
print 'Contact Point : ' + str(contact_point)
print 'Left Point : ' + str(left_point)
print 'Right Point : ' + str(right_point)
print 'Up Point : ' + str(up_point)
print 'Down Point : ' + str(down_point)
print''
print 'Center Coordinates : ' + str(screen_center)
print 'Left Coordinates : ' + str(left_coords)
print 'Right Coordinates : ' + str(right_coords)
print 'Up Coordinates : ' + str(up_coords)
print 'Down Coordinates : ' + str(down_coords)
print ''
print 'Left Vector' + str(left_vector)
print 'Right Vector' + str(right_vector)
print 'Up Vector' + str(up_vector)
print 'Down Vector' + str(down_vector)

# prepare calibration object
o = {}
o['origin_point'] = origin_point
o['contact_point'] = contact_point
o['screen_center'] = screen_center
o['up'] = up_vector
o['down'] = down_vector
o['left'] = left_vector
o['right'] = right_vector

# dump the calibration info with pickle
pickle.dump(o, open('calibration.pickle', 'wb'))