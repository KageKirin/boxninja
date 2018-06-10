import os, sys
from flask import Flask, redirect, request, session, url_for, jsonify
import requests
from datetime import datetime, timedelta
from functools import wraps
import argparse
import codecs
import argparse
from pathlib import Path

sys.path.append("boxhelper")
from boxhelper import config

settings = dict()
app = Flask(__name__)
BASE_URL = 'https://api.box.com/'


def requires_auth(func):
    """Checks for OAuth credentials in the session"""
    @wraps(func)
    def checked_auth(*args, **kwargs):
        if 'oauth_credentials' not in session:
            return redirect(url_for('login'))
        else:
            return func(*args, **kwargs)
    return checked_auth


@app.route('/')
def redirect_to_folder():
    return redirect(url_for('box_folder', folder_id='0'))


@app.route('/box-folder/<folder_id>')
@requires_auth
def box_folder(folder_id):
    api_response = get_box_folder(folder_id)
    page_output = {
        'access_token': session['oauth_credentials']['access_token'],
        'api_response': api_response.json()
    }
    with open('token', 'w') as tf:
        tf.write(session['oauth_credentials']['access_token'])

    output = jsonify(page_output)
    expirancy = int(session['oauth_credentials']['expires_in'])
    print('token expires in', expirancy)
    #output.headers.add('Refresh', '{0};url=http://localhost:5000/box-folder/{1}'.format(expirancy, folder_id))
    print(output.headers)
    return output


@app.route('/box-file/<file_id>')
@requires_auth
def box_file(file_id):
    api_response = get_box_file(file_id)
    page_output = {
        'access_token': session['oauth_credentials']['access_token'],
        'api_response': api_response.json()
    }
    return jsonify(page_output)


@app.route('/box-auth')
def box_auth():
    oauth_response = get_token(code=request.args.get('code'))
    print(oauth_response)
    set_oauth_credentials(oauth_response)
    return redirect(url_for('box_folder', folder_id=0))


@app.route('/login')
def login():
    params = {
        'response_type': 'code',
        'client_id': settings['client_id']
    }
    return redirect(build_box_api_url('oauth2/authorize', params=params))


@app.route('/logout')
def logout():
    session.clear()
    return 'You are now logged out of your Box account.'

@app.route('/box-token')
def box_token():
    res = get_box_folder(0)
    page_output = {
        'access_token': session['oauth_credentials']['access_token'],
        'payload': res.json()
    }
    print(session['oauth_credentials'])
    expirancy = int(session['oauth_credentials']['expires_in'])
    print('token expires in', expirancy)
    with open('token', 'w') as tf:
        tf.write(session['oauth_credentials']['access_token'])

    output = jsonify(page_output)
    output.headers.add('Refresh', '{};url=http://localhost:5000/box-token'.format(expirancy))
    print(output.headers)
    return output


# OAuth 2 Methods
def refresh_access_token_if_needed(func):
    """
    Does two checks:
    - Checks to see if the OAuth credentials are expired based
    on what we know about the last access token we got
    and if so refreshes the access_token
    - Checks to see if the status code of the response is 401,
    and if so refreshes the access_token
    """
    @wraps(func)
    def checked_auth(*args, **kwargs):
        if oauth_credentials_are_expired():
            refresh_oauth_credentials()

        api_response = func(*args, **kwargs)
        if api_response.status_code == 401:
            refresh_oauth_credentials()
            api_response = func(*args, **kwargs)

        return api_response
    return checked_auth


@refresh_access_token_if_needed
def get_box_folder(folder_id):
    """No error checking. If an error occurs, we just return its JSON"""
    resource = '2.0/folders/%s' % folder_id
    url = build_box_api_url(resource)

    bearer_token = session['oauth_credentials']['access_token']
    auth_header = {'Authorization': 'Bearer %s' % bearer_token}

    api_response = requests.get(url, headers=auth_header)
    return api_response

@refresh_access_token_if_needed
def get_box_file(file_id):
    """No error checking. If an error occurs, we just return its JSON"""
    resource = '2.0/files/%s' % file_id
    url = build_box_api_url(resource)

    bearer_token = session['oauth_credentials']['access_token']
    auth_header = {'Authorization': 'Bearer %s' % bearer_token}

    api_response = requests.get(url, headers=auth_header)
    return api_response


def oauth_credentials_are_expired():
    return datetime.now() > session['oauth_expiration']


def refresh_oauth_credentials():
    """
    Gets a new access token using the refresh token grant type
    """
    refresh_token = session['oauth_credentials']['refresh_token']
    oauth_response = get_token(grant_type='refresh_token',
                               refresh_token=refresh_token)
    set_oauth_credentials(oauth_response)


def set_oauth_credentials(oauth_response):
    """
    Sets the OAuth access/refresh tokens in the session,
    along with when the access token will expire

    Will include a 15 second buffer on the exipration time
    to account for any network slowness.
    """
    print(oauth_response)
    token_expiration = oauth_response.get('expires_in')
    session['oauth_expiration'] = (datetime.now()
                                   + timedelta(seconds=token_expiration - 15))
    session['oauth_credentials'] = oauth_response


def get_token(**kwargs):
    """
    Used to make token requests to the Box OAuth2 Endpoint

    Args:
        grant_type
        code
        refresh_token
    """
    url = build_box_api_url('oauth2/token')
    if 'grant_type' not in kwargs:
        kwargs['grant_type'] = 'authorization_code'
    kwargs['client_id'] = settings['client_id']
    kwargs['client_secret'] = settings['client_secret']
    token_response = requests.post(url, data=kwargs)
    return token_response.json()


def build_box_api_url(endpoint, params=''):
    if params != '':
        print(params)
        params = '&'.join(['%s=%s' % (k, v) for k, v in params.items()])
    url = '%s%s?%s' % (BASE_URL, endpoint, params)
    return url


def main(args):
    # load settings
    global settings
    print(settings)
    settings = config.load_settings(Path.home().joinpath(args.config)
        if Path.home().joinpath(args.config).exists()
        else Path(__file__).parent.joinpath(args.config))
    print(settings)
    
    app.debug = True
    app.secret_key = 'a'
    app.run(host='127.0.0.1', port=args.port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', help='port to open server on', type=int, default=5000)
    parser.add_argument('-c', '--config', help='settings file to load (relative to script)', type=Path, default='.boxsettings')
    args = parser.parse_args()
    main(args)
