#	Copyright 2012 Appium Committers
#
#	Licensed to the Apache Software Foundation (ASF) under one
#	or more contributor license agreements.  See the NOTICE file
#	distributed with this work for additional information
#	regarding copyright ownership.  The ASF licenses this file
#	to you under the Apache License, Version 2.0 (the
#	"License"); you may not use this file except in compliance
#	with the License.  You may obtain a copy of the License at
#
#	http://www.apache.org/licenses/LICENSE-2.0
#
#	Unless required by applicable law or agreed to in writing,
#	software distributed under the License is distributed on an
#	"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#	KIND, either express or implied.  See the License for the
#	specific language governing permissions and limitations
#	under the License.

from appium import Appium
import os, readline

def launch(app=None, udid=None):
    if app:
        client = Appium(app, udid)
        client.start()
        
        utils = os.path.join(os.path.dirname(os.path.realpath(__file__)),
            "js/interpreter_utils.js")
        with open(utils) as file:
            js = "".join(file.read().splitlines())
        print client.proxy(js)[0][1]

        print ""
        print "Enter UIAutomation Command (type 'quit' to quit):"

        try:
            while True:
                line = raw_input('> ')

                if line == 'quit':
                    client.stop()
                    break

                response = client.proxy(line)
                try:
                    print response[0][1]
                except:
                    print response
        except KeyboardInterrupt:
            pass
    else:
        raise "ERROR: No app specified"
