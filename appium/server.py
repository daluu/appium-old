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

from appium import Appium
from bottle import Bottle, request, response, redirect
from bottle import run, static_file
import json
import socket
import sys
from time import time
from time import sleep

app = Bottle()
local_storage = {}

@app.get('/favicon.ico')
def get_favicon():
    return static_file('favicon.ico', root='.')

@app.route('/wd/hub/status', method='GET')
def status():
    status = {'sessionId': app.SESSION_ID if app.started else None,
              'status': 0,
              'value': {'build': {'version': 'Appium 1.0'}}}
    return status

@app.route('/wd/hub/session', method='POST')
def create_session():
    app.ios_client.start()
    app.started = True
    redirect('/wd/hub/session/%s' % app.SESSION_ID)

@app.route('/wd/hub/session/<session_id>', method='GET')
def get_session(session_id=''):
    app_response = {'sessionId': session_id,
                'status': 0,
                'value': {"version":"5.0",
                          "webStorageEnabled":False,
                          "locationContextEnabled":False,
                          "browserName":"iOS",
                          "platform":"MAC",
                          "javascriptEnabled":True,
                          "databaseEnabled":False,
                          "takesScreenshot":False}}
    return app_response

@app.route('/wd/hub/session/<session_id>', method='DELETE')
def delete_session(session_id=''):
    app.ios_client.stop()
    app.started = False
    app_response = {'sessionId': session_id,
                'status': 0,
                'value': {}}
    return app_response

@app.route('/wd/hub/session/<session_id>/frame', method='POST')
def switch_to_frame(session_id=''):
    status = 0
    request_data = request.body.read()
    try:
        frame = json.loads(request_data).get('id')
        if frame is None:
            app.ios_client.proxy('wd_frame = mainWindow')
        else:
            app.ios_client.proxy('wd_frame = %s' % frame)
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};

    app_response = {'sessionId': session_id,
                'status': status,
                'value': {}}
    return app_response

@app.route('/wd/hub/session/<session_id>/execute', method='POST')
def execute_script(session_id=''):
    status = 0
    ios_response = ''
    request_data = request.body.read()
    try:
        script = json.loads(request_data).get('script')
        ios_response = app.ios_client.proxy(script,True)
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};

    app_response = {'sessionId': session_id,
        'status': status,
        'value': ios_response}
    return app_response

@app.route('/wd/hub/session/<session_id>/element/<element_id>/text', method='GET')
def get_text(session_id='', element_id=''):
    status = 0
    ios_response = ''
    try:
        script = "elements['%s'].getText()" % element_id
        ios_response = app.ios_client.proxy(script)[0][1]
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};

    app_response = {'sessionId': session_id,
        'status': status,
        'value': ios_response}
    return app_response

@app.route('/wd/hub/session/<session_id>/element/<element_id>/attribute/<attribute>', method='GET')
def get_text(session_id='', element_id='', attribute=''):
    status = 0
    ios_response = ''
    try:
        script = "elements['%s'].name()" % element_id
        ios_response = app.ios_client.proxy(script)[0][1]
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};

    app_response = {'sessionId': session_id,
        'status': status,
        'value': ios_response}
    return app_response

@app.route('/wd/hub/session/<session_id>/element/<element_id>/click', method='POST')
def do_click(session_id='', element_id=''):
    status = 0
    ios_response = ''
    try:
        script = "elements['%s'].tap()" % element_id
        ios_response = app.ios_client.proxy(script)[0][1]
        if ios_response == 'undefined':
            # Stale Reference Exception
            return { 'sessionId': session_id, 'status': 10,
                'value': {'message': 'undefined result tapping element %s' % element_id } }
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};

    app_response = {'sessionId': session_id,
        'status': status,
        'value': ios_response}
    return app_response

@app.route('/wd/hub/session/<session_id>/element/<element_id>/value', method='POST')
def set_value(session_id='', element_id=''):
    status = 0
    ios_response = ''
    request_data = request.body.read()
    print request_data
    try:
        value_to_set = json.loads(request_data).get('value')
        value_to_set = ''.join(value_to_set)

        script = "elements['%s'].setValue('%s')" % (element_id, value_to_set)
        print script
        ios_response = app.ios_client.proxy(script)[0][1]
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};

    app_response = {'sessionId': session_id,
        'status': status,
        'value': ''}
    return app_response

@app.route('/wd/hub/session/<session_id>/element/<element_id>/elements', method='POST')
def element_find_elements(session_id='', element_id=''):
    return _find_element(session_id, "elements['%s']" % element_id, many=True)

@app.route('/wd/hub/session/<session_id>/elements', method='POST')
def find_elements(session_id=''):
    return _find_element(session_id, "wd_frame", many=True)

@app.route('/wd/hub/session/<session_id>/element/<element_id>/element', method='POST')
def element_find_element(session_id='', element_id=''):
    return _find_element(session_id, "elements['%s']" % element_id)

@app.route('/wd/hub/session/<session_id>/element', method='POST')
def find_element(session_id=''):
    return _find_element(session_id, "wd_frame")

def _find_element(session_id, context, many=False):
    try:
        # TODO: need to support more locator_strategy's
        json_request_data = json.loads(request.body.read())
        locator_strategy = json_request_data.get('using')
        value = json_request_data.get('value')

        ios_request = "%s.findElement%sAndSetKey%s('%s')" % (context, 's' if many else ''
                                                             , 's' if many else '', value)
        ios_response = app.ios_client.proxy(ios_request)
        if not many:
            var_name = ios_response[0][1]
            if (var_name == ''):
                return {'sessionId': session_id, 'status': 7};
            found_elements = {'ELEMENT':var_name}
        else:
            found_elements = json.loads(ios_response[0][1])
        return {'sessionId': session_id, 'status': 0, 'value': found_elements}
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};

@app.route('/wd/hub/session/<session_id>/source', method='GET')
def get_page_source(session_id=''):
    try:
        script = "wd_frame.getPageSource()"
        ios_response = app.ios_client.proxy(script)
        page_source = ios_response[0][1];
        return {'sessionId': session_id, 'status': 0, 'value': page_source}
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};

@app.route('/wd/hub/session/<session_id>/orientation', method='GET')
def get_orientation(session_id=''):
    try:
        status = 0
        ios_response = app.ios_client.proxy("getScreenOrientation()")
        orientation = ios_response[0][1];
        if (orientation == "UNKNOWN"):
            status = 12 # invalid element state
        return {'sessionId': session_id, 'status': status, 'value': orientation}
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};

@app.route('/wd/hub/session/<session_id>/orientation', method='POST')
def set_orientation(session_id=''):
    try:
        status = 0
        request_data = request.body.read()
        desired_orientation = json.loads(request_data).get('orientation')
        ios_response = app.ios_client.proxy("setScreenOrientation('%s')" % desired_orientation)
        orientation = ios_response[0][1];
        if (orientation == "UNKNOWN"):
            status = 12 # invalid element state?
        return {'sessionId': session_id, 'status': status, 'value': orientation}
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};

@app.route('/wd/hub/session/<session_id>/alert_text', method='GET')
def get_alert_text(session_id=''):
    status = 0
    ios_response = ''
    try:
        script = "target.frontMostApp().alert().name();"
        ios_response = app.ios_client.proxy(script)[0][1]
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};

    app_response = {'sessionId': session_id,
                    'status': status,
                    'value': ios_response}
    return app_response

@app.route('/wd/hub/session/<session_id>/accept_alert', method='POST')
def post_accept_alert(session_id=''):
    status = 0
    ios_response = ''
    try:
        script = "target.frontMostApp().alert().defaultButton().tap();"
        ios_response = app.ios_client.proxy(script)[0][1]
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};

    app_response = {'sessionId': session_id,
                    'status': status,
                    'value': ios_response}
    return app_response

@app.route('/wd/hub/session/<session_id>/dismiss_alert', method='POST')
def post_dismiss_alert(session_id=''):
    status = 0
    ios_response = ''
    try:
        script = "target.frontMostApp().alert().cancelButton().tap();"
        ios_response = app.ios_client.proxy(script)[0][1]
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};

    app_response = {'sessionId': session_id,
                    'status': status,
                    'value': ios_response}
    return app_response

@app.route('/wd/hub/session/<session_id>/timeouts/implicit_wait', method='POST')
def implicit_wait(session_id=''):
    try:
        request_data = request.body.read()
        timeoutSeconds = json.loads(request_data).get('ms') / 1000
        app.ios_client.proxy("setImplicitWait('%s')" % timeoutSeconds)
        return {'sessionId': session_id, 'status': 0}
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};

@app.route('/wd/hub/session/<session_id>/keys', method='POST')
def keys(session_id=''):
    try:
        request_data = request.body.read()
        keys = json.loads(request_data).get('value')[0].encode('utf-8');
        ios_response = app.ios_client.proxy("sendKeysToActiveElement('%s')" % keys)
        return {'sessionId': session_id, 'status': 0}
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};

@app.route('/wd/hub/session/<session_id>/element/<element_id>/location', method='GET')
def element_location(session_id='', element_id=''):
    try:
        script = "elements['%s'].getElementLocation()" % element_id
        location = json.loads(app.ios_client.proxy(script)[0][1])
        return {'sessionId': session_id, 'status': 0, 'value': location}
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};
    
@app.route('/wd/hub/session/<session_id>/element/<element_id>/size', method='GET')
def element_size(session_id='', element_id=''):
    try:
        script = "elements['%s'].getElementSize()" % element_id
        size = json.loads(app.ios_client.proxy(script)[0][1])
        return {'sessionId': session_id, 'status': 0, 'value': size}
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};
    
@app.route('/wd/hub/session/<session_id>/element/<element_id>/displayed', method='GET')
def element_displayed(session_id='', element_id=''):
    try:
        script = "elements['%s'].isDisplayed()" % element_id
        displayed = app.ios_client.proxy(script)[0][1]
        return {'sessionId': session_id, 'status': 0, 'value': displayed == 'true'}
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])}

@app.route('/wd/hub/session/<session_id>/touch/flick', method='POST')
def touch_flick(session_id=''):
    try:
        json_request_data = json.loads(request.body.read())
        x_speed = json_request_data.get('xSpeed')
        y_speed = json_request_data.get('ySpeed')
        swipe = json_request_data.get('swipe')
        if (swipe):
            app.ios_client.proxy("touchSwipeFromSpeed(%s, %s)" % (x_speed, y_speed))
        else:
            app.ios_client.proxy("touchFlickFromSpeed(%s, %s)" % (x_speed, y_speed))
        return {'sessionId': session_id, 'status': 0}
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])};

@app.route('/wd/hub/session/<session_id>/location', method='POST')
def post_location(session_id=''):
    try:
        json_request_data = json.loads(request.body.read())
        latitude = json_request_data.get('latitude')
        longitude = json_request_data.get('longitude')
        altitude = json_request_data.get('altitude')
        app.ios_client.proxy('target.setLocationWithOptions({"latitude": %s, "longitude": %s},{"altitude": %s})' % (
        latitude, longitude, altitude))
        return {'sessionId': session_id, 'status': 0}
    except:
        response.status = 400
        return {'sessionId': session_id, 'status': 13, 'value': str(sys.exc_info()[1])}

@app.route('/wd/hub/session/<session_id>/local_storage', method='GET')
def get_local_storage(session_id=''):
    if not local_storage.has_key(session_id):
        local_storage[session_id] = {}
    return {'sessionId': session_id, 'status': 0, 'value': local_storage[session_id].keys() }

@app.route('/wd/hub/session/<session_id>/local_storage', method='POST')
def post_local_storage(session_id=''):
    json_request_data = json.loads(request.body.read())
    key = json_request_data.get('key')
    value = json_request_data.get('value')
    if not local_storage.has_key(session_id):
        local_storage[session_id] = {}
    local_storage[session_id][key] = value
    return {'sessionId': session_id, 'status': 0 }

@app.route('/wd/hub/session/<session_id>/local_storage', method='DELETE')
def delete_local_storage(session_id=''):
    local_storage[session_id] = {}
    return {'sessionId': session_id, 'status': 0 }

@app.route('/wd/hub/session/<session_id>/local_storage/key/<key>', method='GET')
def get_local_storage_key(session_id='', key=''):
    if not local_storage.has_key(session_id):
        local_storage[session_id] = {}
    if not local_storage[session_id].has_key(key):
        return {'sessionId': session_id, 'status': 0, 'value': None}
    else:
        return {'sessionId': session_id, 'status': 0, 'value': local_storage[session_id][key]}

@app.route('/wd/hub/session/<session_id>/local_storage/key/<key>', method='DELETE')
def delete_local_storage_key(session_id='', key=''):
    if not local_storage.has_key(session_id):
        local_storage[session_id] = {}
    if local_storage[session_id].has_key(key):
        local_storage[session_id].pop(key)
    return {'sessionId': session_id, 'status': 0}

@app.route('/wd/hub/session/<session_id>/local_storage/size', method='GET')
def get_local_storage_size(session_id=''):
    if not local_storage.has_key(session_id):
        local_storage[session_id] = {}
    return {'sessionId': session_id, 'status': 0, 'value': len(local_storage[session_id].keys())}

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='A webdriver-compatible server for use with native and hybrid iOS applications.')
    parser.add_argument('app', type=str, help='path to simulators .app file or the bundle_id of the desired target on device')
    parser.add_argument('-v', dest='verbose', action="store_true", default=False, help='verbose mode')
    parser.add_argument('-U', '--UDID', type=str, help='unique device identifier of the SUT')
    parser.add_argument('-a', '--address', type=str, default=None, help='ip address to listen on')
    parser.add_argument('-p', '--port', type=int, default=4723, help='port to listen on')

    args = parser.parse_args()
    app.ios_client = Appium(args.app, args.UDID, args.verbose)
    if args.address is None:
        try:
            args.address = socket.gethostbyname(socket.gethostname())
        except:
            args.address = '127.0.0.1'
    app.SESSION_ID = "%s:%d" % (args.address, args.port)
    app.started = False
    run(app, host=args.address, port=args.port)