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
appiumpath = os.path.abspath(os.path.join(os.path.split(os.path.abspath(__file__))[0],'../'))
sys.path.append(appiumpath)
import appium
import deltabot

# create a bot instance
bot = deltabot.Bot()

# create an appium instance
driver = appium.Appium(argv[1])
driver.start()

# set contact points
contactPoint = None
currentPoint = 30

# lower the pen until the ios device is touched
while currentPoint <= 80 and driver.proxy('mainWindow.staticTexts()[0].value()') == '':
	currentPoint += 1
	bot.a(currentPoint)
	bot.b(currentPoint)
	bot.c(currentPoint)
	sleep(.03)

# exit if we did not touch the ios device
if currentPoint > 80:
	raise Exception("Could not contact the iOS device")
contactPoint = currentPoint
coords = driver.proxy('mainWindow.staticTexts()[0].value()')
screenCenter = (int(coords.split(',')[0][1:].replace(' ','')), int(coords.split(',')[1][:-1].replace(' ','')) )

# return the device to the original position
for i in range(contactPoint, 30, -1):
	bot.a(i)
	bot.b(i)
	bot.c(i)
	sleep(.03)

# TODO: find the points in +x, -x, +y, and -y directions
# TODO: find screen edges

# quit appium
driver.stop()

# print summary of calibration
print 'Contact Point : ' + str(contactPoint)
print 'Screen Center : (' + str(screenCenter[0]) + ',' + str(screenCenter[1]) + ')'
