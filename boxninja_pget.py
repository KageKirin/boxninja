#! /usr/bin/python

import sys
import os

sys.path.append("boxhelper")
from boxhelper import config

from boxsdk import OAuth2
from boxsdk import Client, DevelopmentClient, DeveloperTokenClient
from boxsdk.exception import BoxAPIException, BoxOAuthException
from boxsdk.network.logging_network import LoggingNetwork
from functools import wraps

import requests
import codecs
import argparse
from hashlib import sha1
from pathlib import Path

from oauth_helper import refresh_token_from_proxyfile

def boxgetfile(depsfile, outfile, client):
    boxid = depsfile.stem
    item = client.file(boxid)
    info = item.get()

    if outfile.exists():
        # check for overwrite
        if outfile.stat().st_size == info.size:
            with codecs.open(depsfile, mode='r', encoding='utf-8') as df:
                boxhash = df.readlines()[2]
                with open(outfile, mode='rb') as of:
                    filehash = sha1(of.read()).hexdigest()
                    if boxhash == filehash:
                        print("file already fully downloaded. we're good.")
                        return

    with open(outfile, 'wb') as of:
        of.write(info.content())


def main(args):
    settings = config.load_settings(Path.home().joinpath(args.config) 
        if Path.home().joinpath(args.config).exists() 
        else Path(__file__).parent.joinpath(args.config))

    access_token = refresh_token_from_proxyfile()
    print(access_token)

    # connect (this can fail if access token)
    fileOk = False
    while not fileOk:
        try:
            oauth = OAuth2(
                client_id = settings['client_id'],
                client_secret = settings['client_secret'],
                access_token = access_token)
            client = Client(oauth) #DevelopmentClient
            my = client.user(user_id='me').get()
            #print(my)
            boxgetfile(args.input, args.output, client)
            fileOk = True
        except BoxOAuthException:
            access_token = refresh_token_from_proxyfile()
            print('retrying with new token:', access_token)
        except BoxAPIException:
            print('box API exception')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input file with file_id as name', type=Path)
    parser.add_argument('-o', '--output', help='output file name', type=Path)
    parser.add_argument('-c', '--config', help='settings file to load (relative to script)', type=Path, default='.boxsettings')
    parser.add_argument('-p', '--proxy', help='proxy base url', default='http://127.0.0.1:5000')
    args = parser.parse_args()
    main(args)
