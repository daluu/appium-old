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
from bottle import Bottle, request, response, redirect
from bottle import run, static_file
import json
import sys
from time import time
from time import sleep

app = Bottle()

@app.get('/favicon.ico')
def get_favicon():
    return static_file('favicon.ico', root='.')

@app.route('/wd/hub/status', method='GET')
def status():
    status = {'sessionId': None,
              'status': 0,
              'value': {'build': {'version': 'Appium 1.0'}}}
    return status

@app.route('/wd/hub/session', method='POST')
def create_session():
    redirect('/wd/hub/session/1')

@app.route('/wd/hub/session/<session_id>', method='GET')
def get_session(session_id=''):
    app_response = {'sessionId': '1',
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
    app_response = {'sessionId': '1',
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
        return {'sessionId': '1', 'status': 13, 'value': str(sys.exc_info()[1])};

    app_response = {'sessionId': '1',
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
        ios_response = app.ios_client.proxy(script)[0][1]
    except:
        response.status = 400
        return {'sessionId': '1', 'status': 13, 'value': str(sys.exc_info()[1])};

    app_response = {'sessionId': '1',
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
        return {'sessionId': '1', 'status': 13, 'value': str(sys.exc_info()[1])};

    app_response = {'sessionId': '1',
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
        return {'sessionId': '1', 'status': 13, 'value': str(sys.exc_info()[1])};

    app_response = {'sessionId': '1',
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
    except:
        response.status = 400
        return {'sessionId': '1', 'status': 13, 'value': str(sys.exc_info()[1])};

    app_response = {'sessionId': '1',
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
        return {'sessionId': '1', 'status': 13, 'value': str(sys.exc_info()[1])};

    app_response = {'sessionId': '1',
		'status': status,
		'value': ''}
    return app_response

@app.route('/wd/hub/session/<session_id>/elements', method='POST')
def find_elements(session_id=''):
    try:
        # TODO: need to support more locator_strategy's
        json_request_data = json.loads(request.body.read())
        locator_strategy = json_request_data.get('using')
        value = json_request_data.get('value')

        ios_request = "wd_frame.findElementsAndSetKeys('%s')" % value
        ios_response = app.ios_client.proxy(ios_request)
        found_elements = json.loads(ios_response[0][1])
        return {'sessionId': '1', 'status': 0, 'value': found_elements}
    except:
        response.status = 400
        return {'sessionId': '1', 'status': 13, 'value': str(sys.exc_info()[1])};

@app.route('/wd/hub/session/<session_id>/element', method='POST')
def find_element(session_id=''):
    try:
        json_request_data = json.loads(request.body.read())
        locator_strategy = json_request_data.get('using')
        value = json_request_data.get('value')

        ios_request = "wd_frame.findElementAndSetKey('%s')" % value
        ios_response = app.ios_client.proxy(ios_request)
        var_name = ios_response[0][1];
        if (var_name == ''):
            return {'sessionId': '1', 'status': 7};
        found_element = {'ELEMENT':var_name}
        return {'sessionId': '1', 'status': 0, 'value': found_element}
    except:
        response.status = 400
        return {'sessionId': '1', 'status': 13, 'value': str(sys.exc_info()[1])};

@app.route('/wd/hub/session/<session_id>/source', method='GET')
def get_page_source(session_id=''):
    try:
        script = "wd_frame.getPageSource()"
        ios_response = app.ios_client.proxy(script)
        page_source = ios_response[0][1];
        return {'sessionId': '1', 'status': 0, 'value': page_source}
    except:
        response.status = 400
        return {'sessionId': '1', 'status': 13, 'value': str(sys.exc_info()[1])};

@app.route('/wd/hub/session/<session_id>/orientation', method='GET')
def get_orientation(session_id=''):
    try:
        status = 0
        ios_response = app.ios_client.proxy("getScreenOrientation()")
        orientation = ios_response[0][1];
        if (orientation == "UNKNOWN"):
            status = 12 # invalid element state
        return {'sessionId': '1', 'status': status, 'value': orientation}
    except:
        response.status = 400
        return {'sessionId': '1', 'status': 13, 'value': str(sys.exc_info()[1])};

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
        return {'sessionId': '1', 'status': status, 'value': orientation}
    except:
        response.status = 400
        return {'sessionId': '1', 'status': 13, 'value': str(sys.exc_info()[1])};

@app.route('/wd/hub/session/<session_id>/timeouts/implicit_wait', method='POST')
def implicit_wait(session_id=''):
    try:
        request_data = request.body.read()
        timeoutSeconds = json.loads(request_data).get('ms') / 1000
        app.ios_client.proxy("setImplicitWait('%s')" % timeoutSeconds)
        return {'sessionId': '1', 'status': 0}
    except:
        response.status = 400
        return {'sessionId': '1', 'status': 13, 'value': str(sys.exc_info()[1])};

@app.route('/wd/hub/session/<session_id>/keys', method='POST')
def keys(session_id=''):
    try:
        request_data = request.body.read()
        keys = json.loads(request_data).get('value')[0].encode('utf-8');
        ios_response = app.ios_client.proxy("sendKeysToActiveElement('%s')" % keys)
        return {'sessionId': '1', 'status': 0}
    except:
        response.status = 400
        return {'sessionId': '1', 'status': 13, 'value': str(sys.exc_info()[1])};

@app.route('/wd/hub/session/<session_id>/element/<element_id>/location', method='GET')
def element_location(session_id='', element_id=''):
    try:
        script = "elements['%s'].getElementLocation()" % element_id
        location = json.loads(app.ios_client.proxy(script)[0][1])
        return {'sessionId': '1', 'status': 0, 'value': location}
    except:
        response.status = 400
        return {'sessionId': '1', 'status': 13, 'value': str(sys.exc_info()[1])};
    
@app.route('/wd/hub/session/<session_id>/element/<element_id>/size', method='GET')
def element_size(session_id='', element_id=''):
    try:
        script = "elements['%s'].getElementSize()" % element_id
        size = json.loads(app.ios_client.proxy(script)[0][1])
        return {'sessionId': '1', 'status': 0, 'value': size}
    except:
        response.status = 400
        return {'sessionId': '1', 'status': 13, 'value': str(sys.exc_info()[1])};

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
        return {'sessionId': '1', 'status': 0}
    except:
        response.status = 400
        return {'sessionId': '1', 'status': 13, 'value': str(sys.exc_info()[1])};


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='A webdriver-compatible server for use with native and hybrid iOS applications.')
    parser.add_argument('app', type=str, help='path to simulators .app file or the bundle_id of the desired target on device')
    parser.add_argument('-U', '--UDID', type=str, help='unique device identifier of the SUT')
    parser.add_argument('-p', '--port', type=int, default=4723, help='port to listen on')

    args = parser.parse_args()
    app.ios_client = Appium(args.app, args.UDID)
    app.ios_client.start()
    run(app, host='0.0.0.0', port=args.port)

