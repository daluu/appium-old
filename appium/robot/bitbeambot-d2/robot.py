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
from numpy import matrix
from numpy.linalg import inv

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
            print str(self.cal['matrix'])

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
            print str(self.position())
            self.a.set_angle(a_angle)
            self.b.set_angle(b_angle)
            self.c.set_angle(c_angle)
        else:
            while self.a.angle is not a_angle and self.b.angle is not b_angle and self.c.angle is not c_angle:
                self.a.move(a_angle,0,1)
                self.b.move(b_angle,0,1)
                self.c.move(c_angle,0,1)
                print str(self.position())
                sleep(delay)

    def tap(self,x,y):
        # calculate positions
        delta_x = x - self.cal['screen_center'][0]
        delta_y = y - self.cal['screen_center'][1]
        robot_deltas = self.ipad_to_robot((delta_x, delta_y))
        intermediate_arm_position = self.inverse_k(self.cal['origin_point'][0]+robot_deltas[0] , self.cal['origin_point'][1]+robot_deltas[1], self.cal['origin_point'][2])
        final_arm_position = self.inverse_k(self.cal['contact_point'][0]+robot_deltas[0] , self.cal['contact_point'][1]+robot_deltas[1], self.cal['contact_point'][2])

        # check for errors
        if intermediate_arm_position[0] == 1:
            raise Exception('Intermediate Arm Position Is Invalid: '+  str(intermediate_arm_position))
        if final_arm_position[0] == 1:
            raise Exception('Final Arm Position Is Invalid: '+  str(final_arm_position))

        # perform motion
        origin_position = self.inverse_k(self.cal['origin_point'][0], self.cal['origin_point'][1], self.cal['origin_point'][2])
        self.set_position(origin_position)
        sleep(1.5)
        self.set_position(intermediate_arm_position)
        sleep(1.5)
        self.set_position(final_arm_position)
        sleep(1.5)
        self.set_position(intermediate_arm_position)
        sleep(1.5)
        self.set_position(origin_position)


    # Forward kinematics: (theta1, theta2, theta3) -> (x0, y0, z0)
    # Returned {error code, x0,y0,z0}
    def forward_k(self, theta1, theta2, theta3):
        return kinematics.forward(theta1, theta2, theta3)

    # Forward kinematics: (x, y, z) -> (theta1, theta2, theta3)
    # Returned {error code, theta1, theta2, theta3}
    def inverse_k(self, x, y, z):
        return kinematics.inverse(x,y,z)

    def robot_to_ipad(self, robot_distance):
        S = matrix(self.cal['matrix'])
        return (matrix([robot_distance[0], robot_distance[1]]) * S).tolist()[0]

    def ipad_to_robot(self, ipad_distance):
        I = inv(matrix(self.cal['matrix']))
        return (matrix([ipad_distance[0], ipad_distance[1]]) * I).tolist()[0]
