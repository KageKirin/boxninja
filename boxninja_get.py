#! /usr/bin/python

import sys
import os

sys.path.append("boxhelper")
from boxhelper import config

from boxsdk import OAuth2
from boxsdk import Client, DevelopmentClient, DeveloperTokenClient
from boxsdk.network.logging_network import LoggingNetwork
from boxsdk.exception import BoxAPIException

import codecs
import argparse
from hashlib import sha1
from pathlib import Path


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

    # connect (this can fail if access token)
    oauth = OAuth2(
        client_id = settings['client_id'],
        client_secret = settings['client_secret'],
        access_token = settings['access_token'])
    client = DeveloperTokenClient(oauth)
    my = client.user(user_id='me').get()
    #print(my)

    boxgetfile(args.input, args.output, client)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input file with file_id as name', type=Path)
    parser.add_argument('-o', '--output', help='output file name', type=Path)
    parser.add_argument('-c', '--config', help='settings file to load (relative to script)', type=Path, default='.boxsettings')
    args = parser.parse_args()
    main(args)
