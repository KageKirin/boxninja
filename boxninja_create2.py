#! /usr/bin/python

import sys
import os


sys.path.append("boxhelper")
sys.path.append("ninpo")

from boxhelper import config
from ninpo import ninpo

from boxsdk import OAuth2
from boxsdk import Client, DevelopmentClient, DeveloperTokenClient
from boxsdk.network.logging_network import LoggingNetwork
from boxsdk.exception import BoxAPIException

import logging
import codecs
import argparse
from pathlib import Path

ch = logging.StreamHandler()
formatter = logging.Formatter('\x1b[80D\x1b[1A\x1b[K%(message)s')
ch.setFormatter(formatter)
logger = logging.getLogger('')
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

def recurse_boxfolders(foldermap, nj, nj_getfile, nj_checkfile, args, client, ninjafilepath):
    print(foldermap)
    for path, folderid in foldermap:
        #print(path, folderid)
        folder = client.folder(folderid)
        for item in folder.get_items(offset=0, limit=1000):
            logger.info(str(item))
            sys.stdout.flush()

            if item.type == 'folder':
                foldermap.append([path.joinpath(item.name), item.id])
            elif item.type == 'file':
                itempath = path.joinpath(item.name)
                item_depspath = args.output_folder.joinpath(args.deps_folder, item.id)
                item_temppath = args.output_folder.joinpath(args.temp_folder, item.id).with_suffix('.data')

                with codecs.open(item_depspath, 'w', 'utf-8') as depsfile:
                    depsfile.writelines("\n".join([item.id, str(itempath), item.sha1]))
                local_depspath = item_depspath.resolve().relative_to(ninjafilepath.parent)
                local_temppath = item_temppath.resolve().relative_to(ninjafilepath.parent)
                local_itempath = itempath.resolve().relative_to(ninjafilepath.parent)
                ninpo.create_target(nj, nj_getfile, str(local_depspath), str(local_temppath))
                ninpo.create_target(nj, nj_checkfile, [str(local_depspath), str(local_temppath)], str(local_itempath))



def make_folders(folders):
    for f in folders:
        f.mkdir(parents=True, exist_ok=True)


def main(args):
    #print(args)
    settings = config.load_settings(Path.home().joinpath(args.config)
        if Path.home().joinpath(args.config).exists()
        else Path(__file__).parent.joinpath(args.config))
    #print(settings)

    # prepare folders
    make_folders([args.output_folder, args.deps_folder, args.temp_folder])

    # connect (this can fail if access token)
    oauth = OAuth2(
        client_id = settings['client_id'],
        client_secret = settings['client_secret'],
        access_token = settings['access_token'])
    client = Client(oauth)
    my = client.user(user_id='me').get()
    #print(my)


    ninja_path = args.output_folder.joinpath(args.ninja_file).resolve()
    with codecs.open(ninja_path, 'w', 'utf-8') as ninjafile:
        nj = ninpo.create_ninjascroll(ninjafile)

        # get file command
        get_cmd_path = Path(os.path.relpath(str(Path.cwd()), str(ninja_path.parent)), 'boxninja_get.py')
        print(get_cmd_path)
        nj_getfile = ninpo.create_rule(
            nj, name="get_file", cmd="python {0} -i $in -o $out".format(str(get_cmd_path)))

        # check file command
        check_cmd_path = Path(os.path.relpath(str(Path.cwd()), str(ninja_path.parent)), 'boxninja_check.py')
        print(check_cmd_path)
        nj_checkfile = ninpo.create_rule(
            nj, name="check_file", cmd="python {0} -i $in -o $out".format(str(check_cmd_path)))

        foldermap = list(map(lambda x:[Path(args.output_folder), x], args.box_id))
        recurse_boxfolders(foldermap, nj, nj_getfile, nj_checkfile, args, client, ninja_path)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--box-id', metavar='N', type=int, nargs='+', help='box ids of files/folders to get')
    parser.add_argument('-c', '--config', help='settings file to load (relative to script)', type=Path, default='.boxsettings')
    parser.add_argument('-o', '--output-folder', help='output folder name', type=Path, default='.')
    parser.add_argument('-d', '--deps-folder', help='deps folder name (relative to output folder)', type=Path, default='deps')
    parser.add_argument('-t', '--temp-folder', help='temp folder name (relative to output folder)', type=Path, default='tmp')
    parser.add_argument('-n', '--ninja-file', help='output ninja file (relative to output folder)', type=Path, default='build.ninja')
    args = parser.parse_args()
    main(args)
