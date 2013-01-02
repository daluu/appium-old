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
from time import sleep

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

    def __init__(self, serial_port):
        self.serial = serial.Serial(serial_port,9600,timeout=1)
        self.a = Bot.Arm(self, "1")
        self.b = Bot.Arm(self, "2")
        self.c = Bot.Arm(self, "3")

    def position(self):
        return (self.a.angle, self.b.angle, self.c.angle)

    def send_command(self, command, position='0'):
        self.serial.write(command)
        self.serial.write(chr(position))

    def move(self, a_angle, b_angle, c_angle, delay=0.01):
        while self.a.angle is not a_angle and self.b.angle is not b_angle and self.c.angle is not c_angle:
            self.a.move(a_angle,0,1)
            self.b.move(b_angle,0,1)
            self.c.move(c_angle,0,1)
            sleep(delay)