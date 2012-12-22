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

    class Servo:
        def __init__(self, bot, num):
            self.bot = bot
            self.arm_number = num
            self.position = 30

        def set_position(self, new_position):
            self.bot.send_command(self.arm_number, new_position)
            self.bot.position = new_position

        def move(self, new_position, delay=0.03, max_movement=1000):
            positions = []
            if self.position < new_position:
                positions = range(self.position, new_position)
            elif new_position < self.position:
                positions = range(self.position, new_position, -1)
            if len(positions) > max_movement:
                positions = positions[:max_movement]
            for position in positions:
                self.set_position(position)
                sleep(delay)

    def __init__(self, serial_port):
        self.serial = serial.Serial(serial_port,9600,timeout=1)
        self.a = Bot.Servo(self, "1")
        self.b = Bot.Servo(self, "2")
        self.c = Bot.Servo(self, "3")

    def position(self):
        return (self.a.position, self.b.position, self.c.position)

    def send_command(self, command, position='0'):
        self.serial.write(command)
        self.serial.write( chr(position))

    def move(self, a_position, b_position, c_position, delay=0.03):
        while self.position() is not (a_position, b_position, c_position):
            self.a.move(a_position,0,1)
            self.b.move(b_position,0,1)
            self.c.move(c_position,0,1)
            sleep(delay)
