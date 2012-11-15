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
