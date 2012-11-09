from appium import Appium
from bottle import Bottle, request, response, redirect
from bottle import run, static_file
import json
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
        status = 13  # UnknownError

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
        status = 13  # UnknownError

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
        status = 13  # UnknownError

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
        status = 13  # UnknownError

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
        status = 13  # UnknownError

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
        status = 13  # UnknownError

    app_response = {'sessionId': '1',
		'status': status,
		'value': ''}
    return app_response

@app.route('/wd/hub/session/<session_id>/elements', method='POST')
def find_elements(session_id=''):
    status = 0
    found_elements = []
    try:
        # TODO: need to support more locator_strategy's
        request_data = request.body.read()
        locator_strategy = json.loads(request_data).get('using')
        element_type = json.loads(request_data).get('value')

        ios_request = "wd_frame.findElements('%s').length" % element_type
        number_of_items = int(app.ios_client.proxy(ios_request)[0][1])

        for i in range(number_of_items):
            var_name = 'wde' + str(int(time() * 1000000))
            ios_request = "elements['%s'] = wd_frame.findElements('%s')[%s]" % (var_name, element_type, i)
            ios_response = app.ios_client.proxy(ios_request)
            found_elements.append({'ELEMENT':var_name})
    except:
        response.status = 400
        status = 13  # UnknownError

    app_response = {'sessionId': '1',
                'status': status,
                'value': found_elements}
    return app_response

@app.route('/wd/hub/session/<session_id>/element', method='POST')
def find_element(session_id=''):
    status = 7
    found_element = {}
    try:
        request_data = request.body.read()
        print request_data
        locator_strategy = json.loads(request_data).get('using')
        value = json.loads(request_data).get('value')
        # value is "tag_name/text" (i.e. "button/login")
        sep = value.index('/')
        tag_name = value[0:sep]
        text = value[sep + 1:]
        var_name = 'wde' + str(int(time() * 1000000))

        ios_request = "wd_frame.findElementAndSetKey('%s', '%s', '%s')" % (tag_name, text, var_name)
        ios_response = app.ios_client.proxy(ios_request)
        element = ios_response[0][1];
        if (element != ''):
            status = 0
            found_element = {'ELEMENT':var_name}
    except:
        response.status = 400
        status = 13  # UnknownError

    return {'sessionId': '1', 'status': status, 'value': found_element}

@app.route('/wd/hub/session/<session_id>/source', method='GET')
def get_page_source(session_id=''):
    status = 0
    page_source = ''
    try:
        script = "wd_frame.getPageSource()"
        ios_response = app.ios_client.proxy(script)
        page_source = ios_response[0][1];
    except:
        response.status = 400
        status = 13  # UnknownError

    return {'sessionId': '1', 'status': status, 'value': page_source}

@app.route('/wd/hub/session/<session_id>/orientation', method='GET')
def get_orientation(session_id=''):
    status = 0
    orientation = ''
    try:
        ios_response = app.ios_client.proxy("getScreenOrientation()")
        orientation = ios_response[0][1];
        if (orientation == "UNKNOWN"):
            status = 12 # invalid element state
    except:
        response.status = 400
        status = 13  # UnknownError

    return {'sessionId': '1', 'status': status, 'value': orientation}

@app.route('/wd/hub/session/<session_id>/orientation', method='POST')
def set_orientation(session_id=''):
    status = 0
    orientation = ''
    try:
        request_data = request.body.read()
        desired_orientation = json.loads(request_data).get('orientation')
        ios_response = app.ios_client.proxy("setScreenOrientation('%s')" % desired_orientation)
        orientation = ios_response[0][1];
        if (orientation == "UNKNOWN"):
            status = 12 # invalid element state?
    except:
        response.status = 400
        status = 13  # UnknownError

    return {'sessionId': '1', 'status': status, 'value': orientation}

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

