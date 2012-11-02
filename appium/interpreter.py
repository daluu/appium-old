from appium import Appium
import readline

def launch(app=None, udid=None):
    if app:
        client = Appium(app, udid)
        client.start()

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
