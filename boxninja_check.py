#! /usr/bin/python

import sys
import os

import codecs
import argparse
import shutil
from hashlib import sha1
from pathlib import Path


def main(args):
    depsfile = args.input[0]
    tempfile = args.input[1]

    with codecs.open(depsfile, mode='r', encoding='utf-8') as df:
        boxhash = df.read().split('\n')[2]
        with open(tempfile, 'rb') as tf:
            filehash = sha1(tf.read()).hexdigest()
            if boxhash == filehash:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(tempfile.resolve(), args.output.resolve())
            else:
                print('hash mismatching')
                if args.output.exists():
                    args.output.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input file with file_id as name', type=Path, nargs='+')
    parser.add_argument('-o', '--output', help='output file name', type=Path)
    args = parser.parse_args()
    main(args)
