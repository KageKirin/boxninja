#! /usr/bin/python

import keyring
from pathlib import Path
### OAuth2 helper

def read_tokens():
    """Reads authorisation tokens from keyring"""
    # Use keyring to read the tokens
    auth_token = keyring.get_password('Box_Auth', 'mybox@box.com')
    refresh_token = keyring.get_password('Box_Refresh', 'mybox@box.com')
    return auth_token, refresh_token
 
 
def store_tokens(access_token, refresh_token):
    """Callback function when Box SDK refreshes tokens"""
    # Use keyring to store the tokens
    keyring.set_password('Box_Auth', 'mybox@box.com', access_token)
    keyring.set_password('Box_Refresh', 'mybox@box.com', refresh_token)



def refresh_token_from_proxyfile():
    with open(Path(__file__).parent.joinpath('token'), 'r') as tf:
        return tf.readline()
    return None