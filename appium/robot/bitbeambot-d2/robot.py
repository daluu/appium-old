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

import serial
import os
import pickle
from time import sleep
import kinematics

class Bot():

    class Arm:
        def __init__(self, bot, num):
            self.bot = bot
            self.number = num
            self.angle = 30

        def set_angle(self, new_angle):
            self.bot.send_command(self.number, new_angle)
            self.angle = new_angle

        def move(self, desired_angle, delay=0.1, max_movement=1000):

            # determine the angles between the current angle and the desired angle
            intermediate_angles = []
            if self.angle < desired_angle:
                intermediate_angles = range(self.angle, desired_angle + 1)
            elif desired_angle < self.angle:
                intermediate_angles = range(self.angle, desired_angle - 1, -1)
            if self.angle in intermediate_angles:
                intermediate_angles.remove(self.angle)

            # only move the arm by the maximum amount
            if len(intermediate_angles) > max_movement:
                intermediate_angles = intermediate_angles[:max_movement]

            # move the arm 1 degree at a time
            for angle in intermediate_angles:
                self.set_angle(angle)
                sleep(delay)

    def __init__(self, serial_port=None, calibrationFile=None):

        # auto-detect serial port
        if serial_port is None:
            for device in os.listdir('/dev/'):
                if 'tty' in device and 'usb' in device:
                    serial_port = os.path.join('/dev/', device)

        # load calibration data if it's supplied
        self.cal = None
        if calibrationFile is not None:
            self.cal = pickle.load(open( calibrationFile, 'rb' ))

        self.serial = serial.Serial(serial_port,9600,timeout=1)
        self.is_calibrated = self.cal is not None
        self.a = Bot.Arm(self, "1")
        self.b = Bot.Arm(self, "2")
        self.c = Bot.Arm(self, "3")

    def position(self):
        return (self.a.angle, self.b.angle, self.c.angle)

    def set_position(self, position):
        offset = len(position) - 3
        t1 = int(round(position[offset]))
        t2 = int(round(position[offset+1]))
        t3 = int(round(position[offset+2]))
        self.move(t1,t2,t3,0)

    def send_command(self, command, position='0'):
        self.serial.write(command)
        self.serial.write(chr(position))

    def move(self, a_angle, b_angle, c_angle, delay=0):
        if delay <= 0:
            self.a.set_angle(a_angle)
            self.b.set_angle(b_angle)
            self.c.set_angle(c_angle)
            print str(self.position())
        else:
            while self.a.angle is not a_angle and self.b.angle is not b_angle and self.c.angle is not c_angle:
                self.a.move(a_angle,0,1)
                self.b.move(b_angle,0,1)
                self.c.move(c_angle,0,1)
                print str(self.position())
                sleep(delay)

    def tap(self,x,y):
        # calculate positions
        intermediate_arm_point = self.map_screen_point(x,y, False)
        intermediate_arm_position = self.inverse_k(intermediate_arm_point[0], intermediate_arm_point[1], intermediate_arm_point[2])
        final_arm_point = self.map_screen_point(x,y, True)
        final_arm_position = self.inverse_k(final_arm_point[0], final_arm_point[1], final_arm_point[2])

        print 'desired coordinates: (%d,%d)' % (x,y)
        print 'screen center: ' + str(self.cal['screen_center'])
        print 'intermediate arm point: ' + str(intermediate_arm_point)
        print 'final arm point: ' + str(final_arm_point)
        print 'intermediate arm position: ' + str(intermediate_arm_position)
        print 'final arm position: ' + str(final_arm_position)

        # check for errors
        if intermediate_arm_position[0] == 1:
            raise Exception('Intermediate Arm Position Is Invalid: '+  str(intermediate_arm_position))
        if final_arm_position[0] == 1:
            raise Exception('Final Arm Position Is Invalid: '+  str(final_arm_position))

        # perform motion
        #self.set_position(self.cal['origin_point'])
        sleep(10)
        self.set_position(intermediate_arm_position)
        sleep(1)
        self.set_position(final_arm_position)
        sleep(1)
        self.set_position(intermediate_arm_position)
        sleep(1)
        self.set_position(self.cal['origin_point'])


    # Forward kinematics: (theta1, theta2, theta3) -> (x0, y0, z0)
    # Returned {error code, x0,y0,z0}
    def forward_k(self, theta1, theta2, theta3):
        return kinematics.forward(theta1, theta2, theta3)

    # Forward kinematics: (x, y, z) -> (theta1, theta2, theta3)
    # Returned {error code, theta1, theta2, theta3}
    def inverse_k(self, x, y, z):
        return kinematics.inverse(x,y,z)

    # maps a screen point to a bitbeambot x,y,z
    def map_screen_point(self,x,y,contact=True):
        if not self.is_calibrated:
            raise Exception('cannot map screen points without calibration data')

        x_motion = x - self.cal['screen_center'][0]
        y_motion = y - self.cal['screen_center'][1]

        # setup starting position at robot center
        point = self.cal['contact_point']
        if not contact:
            point = self.cal['origin_point']

        # translate x
        x_vector = self.cal['right']
        if x_motion < 0:
            x_vector = self.cal['left']
        for i in range(0,abs(x_motion)):
            point = (point[0] + x_vector[0], point[1] + x_vector[1], point[2])

        # translate y
        y_vector = self.cal['up']
        if y_motion < 0:
            x_vector = self.cal['down']
        for i in range(0,abs(y_motion)):
            point = (point[0]+ + y_vector[0], point[1] + y_vector[1], point[2])

        return point
