import requests
import json

# SERVER_URL = 'http://34.71.208.17/api/'
SERVER_URL = 'http://localhost:8000/api/'


def get_API_response(url, reqData, method='GET'):
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(reqData)
    try:
        if method == 'GET':
            response = requests.get(url, data=json_data, headers=headers)
        else:
            response = requests.post(url, data=json_data, headers=headers)
        return response.json()
    except:
        return {'success': False}


def get_city(name, type='county'):
    req_data = {'city': name, 'type': type}
    response = get_API_response(SERVER_URL + 'city', req_data)
    return response


def post_meeting_to_server(location, meeting_data):
    try:
        meeting_data['city'] = get_city(location['name'], location['type'])['id']
        return get_API_response(SERVER_URL + 'meeting', meeting_data, 'POST')
    except Exception as e:
        return {'success': False, 'message': e}
def check_meeting_exists(name):
    try:
        response = get_API_response(SERVER_URL+'meeting', {'name': name}, 'GET')
        return response['exists']
    except Exception as e:
        return False