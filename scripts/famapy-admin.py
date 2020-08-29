#!/usr/bin/python

import argparse
import os
import re
from distutils.dir_util import copy_tree


# TODO: add option to add operation


# Parser arguments
parser = argparse.ArgumentParser(description='famapy-script.py: generate structure for new plugins')
parser.add_argument('name', type=str, help='A name for your plugin. Ex: fama')
parser.add_argument('extension', type=str, help='A extension for your plugin. Ex: fm')
parser.add_argument('--path', default='.', type=str, help='Plugin project path.  Default: .')
args = parser.parse_args()

NAME = args.name
EXT = args.extension
DST = args.path
SRC = 'skel_metamodel/'


# Check DST exist
if not os.path.isdir(DST):
    print(f"Folder {DST} not exist")
    exit(0)

# Check DST is empty
if len(os.listdir(DST)) != 0:
    print(f"Folder {DST} is not empty")
    exit(0)

# Check DST has permissions to WRITE
if not os.access(DST, os.W_OK):
    print(f"Folder {DST} has not write permissions")
    exit(0)


# Generating structure
print("Generating structure ...")

copy_files = copy_tree(SRC, DST)

for copy_file in copy_files:
    with open(copy_file, "r") as f:
        lines = f.readlines()
    with open(copy_file, "w") as fw:
        for line in lines:
            out_line = line.replace('__NAME__', NAME.capitalize()).replace('__EXT__', EXT)
            fw.write(out_line)


os.rename(os.path.join(DST, 'famapy/metamodels/__NAME__'),
          os.path.join(DST, f'famapy/metamodels/{NAME}'))

print("Done!")
